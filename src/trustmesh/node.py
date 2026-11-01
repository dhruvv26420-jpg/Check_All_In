"""Trust network Node implementation for projects.

Manages cryptographic record ingestion, key pinning, per-issuer hash-chain integrity,
gossip-based set-difference pulls, personal transitive trust path calculation with
hop-decay and fan-out dilution, and multi-factor contributor evaluations.
"""

from __future__ import annotations

import dataclasses
import heapq
import math
import random
import time
from typing import Any, Optional

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization
    _HAS_NATIVE_CRYPTO = True
except ImportError:
    _HAS_NATIVE_CRYPTO = False

from trustmesh.campaign import (
    CampaignCluster,
    FingerprintItem,
    cluster_near_duplicates,
    identify_campaign_members,
    minhash_similarity,
)
from trustmesh.records import (
    HashChainError,
    InvalidSignatureError,
    KeyImpersonationError,
    Record,
    RecordError,
    RecordKind,
    create_record,
    generate_keypair,
)

# Half-lives in seconds
HALF_LIFE_DENOUNCE_SECONDS = 120.0 * 86400.0  # 120 days
HALF_LIFE_VOUCH_SECONDS = 365.0 * 86400.0     # 365 days

MAX_TRANSITIVE_HOPS = 3
HOP_DECAY_FACTOR = 0.7
FAN_OUT_MAX_PEERS = 8


class Verdict:
    """Possible evaluation verdicts for contributors."""

    TRUST = "TRUST"
    ALLOW = "ALLOW"
    PROBATION = "PROBATION"
    FLAG = "FLAG"
    HOLD = "HOLD"
    BLOCK = "BLOCK"

    ALL = {TRUST, ALLOW, PROBATION, FLAG, HOLD, BLOCK}


@dataclasses.dataclass
class EvaluationResult:
    """Structured result returned by node.evaluate(contributor)."""

    contributor: str
    verdict: str
    pos: float
    neg: float
    reason: str
    trusted_denouncers_count: int
    is_campaign_member: bool
    is_exempt_from_hold: bool
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "contributor": self.contributor,
            "verdict": self.verdict,
            "pos": round(self.pos, 4),
            "neg": round(self.neg, 4),
            "reason": self.reason,
            "trusted_denouncers_count": self.trusted_denouncers_count,
            "is_campaign_member": self.is_campaign_member,
            "is_exempt_from_hold": self.is_exempt_from_hold,
            "details": self.details,
        }


class Node:
    """Represents a project maintaining a local trust graph and record database."""

    def __init__(
        self,
        project_id: str,
        seed: Optional[str | bytes] = None,
        private_key: Optional[ed25519.Ed25519PrivateKey] = None,
    ) -> None:
        self.project_id = project_id

        if private_key is not None:
            self.private_key = private_key
            pub = private_key.public_key()
            if _HAS_NATIVE_CRYPTO:
                self.public_key_hex = pub.public_bytes(
                    serialization.Encoding.Raw,
                    serialization.PublicFormat.Raw,
                ).hex()
            else:
                self.public_key_hex = pub.public_bytes().hex()
        else:
            self.private_key, self.public_key_hex = generate_keypair(seed or project_id)

        # Identity key pinning on first sight: issuer -> public_key_hex
        self.key_pins: dict[str, str] = {self.project_id: self.public_key_hex}

        # Records store: record_id -> Record
        self.records: dict[str, Record] = {}

        # Hash chains: issuer -> list[Record] in monotonic chain order
        self.chains: dict[str, list[Record]] = {}

        # Retracted records
        self.retracted_record_ids: set[str] = set()

        # PR Fingerprints: record_id -> FingerprintItem
        self.pr_fingerprints: dict[str, FingerprintItem] = {}

        # Declared direct peers: peer_project_id -> weight
        self.declared_peers: dict[str, float] = {}

        # Network peer trust declarations: issuer -> {target: weight}
        self.peer_trust_edges: dict[str, dict[str, float]] = {}

    def declare_peer(self, peer_id: str, weight: float, ts: Optional[float] = None) -> Record:
        """Declares direct trust in another project, publishing a signed TRUST_PEER record."""
        weight = max(0.0, min(1.0, float(weight)))
        self.declared_peers[peer_id] = weight

        prev_id = self.chains[self.project_id][-1].record_id if self.chains.get(self.project_id) else ""
        rec = create_record(
            issuer=self.project_id,
            private_key=self.private_key,
            kind=RecordKind.TRUST_PEER,
            subject=peer_id,
            payload={"weight": weight},
            prev=prev_id,
            ts=ts,
        )
        self.ingest_record(rec)
        return rec

    def vouch(
        self,
        subject: str,
        score: float = 1.0,
        comment: str = "",
        ts: Optional[float] = None,
    ) -> Record:
        """Issues and ingests a signed VOUCH record for a contributor."""
        prev_id = self.chains[self.project_id][-1].record_id if self.chains.get(self.project_id) else ""
        rec = create_record(
            issuer=self.project_id,
            private_key=self.private_key,
            kind=RecordKind.VOUCH,
            subject=subject,
            payload={"score": float(score), "comment": comment},
            prev=prev_id,
            ts=ts,
        )
        self.ingest_record(rec)
        return rec

    def denounce(
        self,
        subject: str,
        evidence: Optional[list[str]] = None,
        reason: str = "",
        ts: Optional[float] = None,
    ) -> Record:
        """Issues and ingests a signed DENOUNCE record with optional cited fingerprint evidence."""
        prev_id = self.chains[self.project_id][-1].record_id if self.chains.get(self.project_id) else ""
        rec = create_record(
            issuer=self.project_id,
            private_key=self.private_key,
            kind=RecordKind.DENOUNCE,
            subject=subject,
            payload={"evidence": evidence or [], "reason": reason},
            prev=prev_id,
            ts=ts,
        )
        self.ingest_record(rec)
        return rec

    def retract(
        self,
        target_record_id: str,
        reason: str = "",
        ts: Optional[float] = None,
    ) -> Record:
        """Issues and ingests a signed RETRACT record revoking a prior record."""
        prev_id = self.chains[self.project_id][-1].record_id if self.chains.get(self.project_id) else ""
        rec = create_record(
            issuer=self.project_id,
            private_key=self.private_key,
            kind=RecordKind.RETRACT,
            subject=target_record_id,
            payload={"target_record_id": target_record_id, "reason": reason},
            prev=prev_id,
            ts=ts,
        )
        self.ingest_record(rec)
        return rec

    def publish_pr_fingerprint(
        self,
        contributor: str,
        pr_id: str,
        text: str,
        additions: int = 1,
        account_age_days: float = 30.0,
        outcome: str = "open",
        is_low_value: Optional[bool] = None,
        ts: Optional[float] = None,
    ) -> Record:
        """Publishes a signed PR_FINGERPRINT record with MinHash metadata."""
        from trustmesh.campaign import compute_minhash

        minhash_sig = compute_minhash(text)
        is_low_val = is_low_value if is_low_value is not None else (additions <= 5)

        prev_id = self.chains[self.project_id][-1].record_id if self.chains.get(self.project_id) else ""
        rec = create_record(
            issuer=self.project_id,
            private_key=self.private_key,
            kind=RecordKind.PR_FINGERPRINT,
            subject=contributor,
            payload={
                "pr_id": pr_id,
                "project": self.project_id,
                "text": text,
                "minhash": minhash_sig,
                "additions": additions,
                "account_age_days": account_age_days,
                "outcome": outcome,
                "is_low_value": is_low_val,
            },
            prev=prev_id,
            ts=ts,
        )
        self.ingest_record(rec)
        return rec

    def ingest_record(self, record: Record) -> bool:
        """Ingests a record after verifying signature, key pinning, and hash-chain continuity."""
        # 1. Cryptographic signature and schema verification
        record.verify()

        # 2. Key pinning on first sight
        issuer = record.issuer
        key_hex = record.issuer_key.lower()
        if issuer in self.key_pins:
            if self.key_pins[issuer] != key_hex:
                raise KeyImpersonationError(
                    f"Key impersonation detected for issuer '{issuer}': "
                    f"pinned '{self.key_pins[issuer]}', got '{key_hex}'"
                )
        else:
            self.key_pins[issuer] = key_hex

        # 3. Hash-chain verification for issuer
        issuer_chain = self.chains.get(issuer, [])
        if issuer_chain:
            last_record = issuer_chain[-1]
            if record.prev != last_record.record_id:
                raise HashChainError(
                    f"Hash-chain gap for '{issuer}': expected prev '{last_record.record_id}', got '{record.prev}'"
                )
            if record.ts < last_record.ts:
                raise HashChainError(
                    f"Non-monotonic timestamp for '{issuer}': {record.ts} < {last_record.ts}"
                )
        else:
            if record.prev not in ("", None):
                raise HashChainError(
                    f"First record for '{issuer}' must have empty prev, got '{record.prev}'"
                )

        # 4. Idempotent storage
        if record.record_id in self.records:
            return False

        self.records[record.record_id] = record
        self.chains.setdefault(issuer, []).append(record)

        # 5. Process internal state updates
        if record.kind == RecordKind.TRUST_PEER:
            weight = max(0.0, min(1.0, float(record.payload.get("weight", 1.0))))
            self.peer_trust_edges.setdefault(record.issuer, {})[record.subject] = weight

        elif record.kind == RecordKind.RETRACT:
            target_id = record.payload.get("target_record_id")
            if target_id:
                self.retracted_record_ids.add(target_id)

        elif record.kind == RecordKind.PR_FINGERPRINT:
            fp_item = FingerprintItem.from_record_payload(
                record.record_id,
                record.subject,
                record.ts,
                record.payload,
            )
            self.pr_fingerprints[record.record_id] = fp_item

        return True

    def get_known_record_ids(self) -> set[str]:
        """Returns set of all record IDs known to this node."""
        return set(self.records.keys())

    def gossip_pull_from(self, peer: Node) -> int:
        """Pulls and ingests missing records from a peer by set-difference."""
        remote_ids = peer.get_known_record_ids()
        missing_ids = remote_ids - self.get_known_record_ids()
        if not missing_ids:
            return 0

        ingested_count = 0
        # Iterate over peer's chains to ingest in exact chain order per issuer
        for issuer, chain in peer.chains.items():
            for rec in chain:
                if rec.record_id in missing_ids and rec.record_id not in self.records:
                    try:
                        if self.ingest_record(rec):
                            ingested_count += 1
                    except RecordError:
                        continue

        return ingested_count

    def gossip_round(self, network_nodes: dict[str, Node], random_count: int = 2) -> int:
        """Conducts a gossip round with declared peers plus a few random nodes."""
        targets: set[str] = set()

        # Add active declared peers
        for peer_id in self.declared_peers:
            if peer_id in network_nodes and peer_id != self.project_id:
                targets.add(peer_id)

        # Add random other nodes
        other_candidates = [
            nid for nid in network_nodes
            if nid != self.project_id and nid not in targets
        ]
        if other_candidates:
            sample_size = min(len(other_candidates), random_count)
            for rnd_id in random.sample(other_candidates, sample_size):
                targets.add(rnd_id)

        total_pulled = 0
        for target_id in targets:
            peer_node = network_nodes[target_id]
            total_pulled += self.gossip_pull_from(peer_node)

        return total_pulled

    def compute_transitive_trust(self) -> dict[str, float]:
        """Computes personal transitive trust from this project to all reachable projects.

        Rules:
        - Product of edge weights along path.
        - x0.7 discount per hop after the first (hop 2 gets x0.7, hop 3 gets x0.7^2).
        - Maximum 3 hops.
        - Fan-out dilution: if a peer declares trust in K > 8 projects, its outgoing edges
          are diluted by factor (8 / K).
        - Returns map of project_id -> maximum transitive trust weight.
        """
        trust_map: dict[str, float] = {self.project_id: 1.0}

        # Build composite edge graph from declared peers and gossip records
        graph: dict[str, dict[str, float]] = {}

        # Project's own direct declared edges
        graph[self.project_id] = dict(self.declared_peers)

        # Edges announced by other issuers
        for issuer, edges in self.peer_trust_edges.items():
            if issuer not in graph:
                graph[issuer] = {}
            for target, w in edges.items():
                graph[issuer][target] = w

        # Queue contains: (current_node, hops_count, current_path_trust)
        # Using BFS / path exploration for maximum path trust within <= 3 hops
        queue: list[tuple[str, int, float, list[str]]] = [(self.project_id, 0, 1.0, [self.project_id])]

        while queue:
            curr_node, hops, curr_trust, path = queue.pop(0)

            if hops >= MAX_TRANSITIVE_HOPS:
                continue

            outgoing = graph.get(curr_node, {})
            k_out = len(outgoing)
            # Fan-out dilution
            dilution = (float(FAN_OUT_MAX_PEERS) / float(k_out)) if k_out > FAN_OUT_MAX_PEERS else 1.0

            for next_node, raw_weight in outgoing.items():
                if next_node in path:
                    # Avoid cyclic loops
                    continue

                effective_edge = raw_weight * dilution
                hop_penalty = HOP_DECAY_FACTOR if hops >= 1 else 1.0
                next_trust = curr_trust * effective_edge * hop_penalty
                next_hops = hops + 1

                if next_trust > trust_map.get(next_node, 0.0):
                    trust_map[next_node] = next_trust
                    queue.append((next_node, next_hops, next_trust, path + [next_node]))

        return trust_map

    def get_transitive_trust(self, target_project_id: str) -> float:
        """Returns personal transitive trust to a specific project."""
        if target_project_id == self.project_id:
            return 1.0
        trust_map = self.compute_transitive_trust()
        return trust_map.get(target_project_id, 0.0)

    def verify_denouncement_evidence(self, denounce_record: Record) -> float:
        """Calculates evidence factor for a denouncement.

        Returns 1.0 only if cited fingerprints belong to subject and are verified near-duplicates.
        Returns 0.0 otherwise.
        """
        evidence_ids = denounce_record.payload.get("evidence", [])
        if not evidence_ids or len(evidence_ids) < 2:
            return 0.0

        cited_fps: list[FingerprintItem] = []
        for eid in evidence_ids:
            if eid in self.pr_fingerprints:
                fp = self.pr_fingerprints[eid]
                if fp.contributor != denounce_record.subject:
                    return 0.0
                cited_fps.append(fp)
            else:
                # Receiver cannot verify cited fingerprint (not in local database)
                return 0.0

        # Verify all cited fingerprints are near-duplicates within 48h
        for i in range(len(cited_fps)):
            for j in range(i + 1, len(cited_fps)):
                fp1 = cited_fps[i]
                fp2 = cited_fps[j]
                time_diff = abs(fp1.timestamp - fp2.timestamp)
                sim = minhash_similarity(fp1.minhash, fp2.minhash)
                if time_diff > 48.0 * 3600.0 or sim < 0.65:
                    return 0.0

        return 1.0

    def compute_issuer_reliability(self, issuer: str) -> float:
        """Computes Beta(2, 1)-style reliability score for an issuer.

        Uncorroborated serial accusers who make accusations without verifiable evidence
        or agreement from other projects lose credibility.
        """
        # Prior Beta(2, 1)
        alpha = 2.0
        beta = 1.0

        # Scan all denouncements issued by this issuer
        issuer_denouncements = [
            r for r in self.records.values()
            if r.issuer == issuer and r.kind == RecordKind.DENOUNCE and r.record_id not in self.retracted_record_ids
        ]

        if not issuer_denouncements:
            return 1.0

        for den in issuer_denouncements:
            # Check 1: Does this denouncement have verified near-duplicate evidence?
            ev_factor = self.verify_denouncement_evidence(den)
            if ev_factor >= 1.0:
                alpha += 1.0
                continue

            # Check 2: Has any other trusted project also denounced this subject?
            other_denouncers = [
                r.issuer for r in self.records.values()
                if r.subject == den.subject and r.kind == RecordKind.DENOUNCE
                and r.issuer != issuer and r.record_id not in self.retracted_record_ids
                and self.get_transitive_trust(r.issuer) >= 0.5
            ]

            if other_denouncers:
                alpha += 1.0
            else:
                # Uncorroborated accusation
                beta += 1.0

        # Beta expectation: E[theta] = alpha / (alpha + beta)
        # Normalized by prior expectation 2/3 so unpenalized reliability is 1.0
        normalized = (alpha / (alpha + beta)) * 1.5
        return min(1.0, max(0.05, normalized))

    def process_campaign_autodenunciations(self, ts: Optional[float] = None) -> list[Record]:
        """Scans local fingerprint clusters and issues automated denouncements with evidence

        for accounts targeting >= 4 projects with >= 4 near-duplicate PRs within 48h.
        """
        all_fps = list(self.pr_fingerprints.values())
        clusters = cluster_near_duplicates(all_fps)
        _, auto_denounce_targets = identify_campaign_members(clusters)

        created_denouncements: list[Record] = []
        for account, evidence_ids in auto_denounce_targets.items():
            # Check if this node already has an active denouncement for this account
            already_denounced = any(
                r.issuer == self.project_id and r.kind == RecordKind.DENOUNCE and r.subject == account
                for r in self.records.values()
                if r.record_id not in self.retracted_record_ids
            )
            if not already_denounced:
                rec = self.denounce(
                    subject=account,
                    evidence=evidence_ids,
                    reason="Automated campaign denouncement: >=4 near-duplicate PRs across >=4 projects",
                    ts=ts,
                )
                created_denouncements.append(rec)

        return created_denouncements

    def evaluate(self, contributor: str, now: Optional[float] = None) -> EvaluationResult:
        """Evaluates a contributor's standing within the network.

        Evaluation rules:
        - One voice per issuer (latest active record).
        - Time decay: denounce half-life 120 days, vouch 365 days.
        - Noisy-OR aggregation for positive and negative scores.
        - Evidence factor: denouncement counts fully only if cited fingerprints are verified near-duplicates.
        - Issuer reliability: Beta(2,1)-style.
        - BLOCK only if project itself denounced, or at least 2 independent trusted issuers with
          combined weight >= 0.7 and neg > pos.
        - Contributor with no records gets PROBATION, never rejection.
        - Campaign membership gives HOLD (human triage), never BLOCK, and pos >= 0.6 is exempt.
        - Retraction support.
        """
        if now is None:
            now = time.time()

        # 1. Collect all non-retracted records regarding contributor
        subject_records = [
            r for r in self.records.values()
            if r.subject == contributor and r.record_id not in self.retracted_record_ids
        ]

        # 2. Check if project itself denounced the contributor
        own_denounce = [
            r for r in subject_records
            if r.issuer == self.project_id and r.kind == RecordKind.DENOUNCE
        ]
        is_own_denounced = len(own_denounce) > 0

        # 3. One voice per issuer: pick latest record per issuer
        records_by_issuer: dict[str, Record] = {}
        for r in subject_records:
            if r.kind in (RecordKind.VOUCH, RecordKind.DENOUNCE):
                if r.issuer not in records_by_issuer or r.ts > records_by_issuer[r.issuer].ts:
                    records_by_issuer[r.issuer] = r

        # 4. Transitive trust to all projects
        trust_map = self.compute_transitive_trust()

        # 5. Compute weights for vouchers and denouncers
        vouch_weights: list[float] = []
        denounce_weights: list[float] = []
        trusted_denouncers: list[str] = []

        details_vouchers: list[dict[str, Any]] = []
        details_denouncers: list[dict[str, Any]] = []

        for issuer, rec in records_by_issuer.items():
            issuer_trust = trust_map.get(issuer, 0.0)
            if issuer_trust <= 0.0:
                continue

            dt = max(0.0, now - rec.ts)
            rel = self.compute_issuer_reliability(issuer)

            if rec.kind == RecordKind.VOUCH:
                # Vouch time decay: 365-day half-life
                decay = 2.0 ** (-dt / HALF_LIFE_VOUCH_SECONDS)
                raw_score = float(rec.payload.get("score", 1.0))
                weight = issuer_trust * decay * rel * raw_score
                vouch_weights.append(weight)
                details_vouchers.append({
                    "issuer": issuer,
                    "trust": issuer_trust,
                    "decay": decay,
                    "reliability": rel,
                    "effective_weight": weight,
                })

            elif rec.kind == RecordKind.DENOUNCE:
                # Denounce time decay: 120-day half-life
                decay = 2.0 ** (-dt / HALF_LIFE_DENOUNCE_SECONDS)
                # Evidence factor
                ev_factor = self.verify_denouncement_evidence(rec)
                weight = issuer_trust * decay * rel * ev_factor
                denounce_weights.append(weight)

                details_denouncers.append({
                    "issuer": issuer,
                    "trust": issuer_trust,
                    "decay": decay,
                    "reliability": rel,
                    "evidence_factor": ev_factor,
                    "effective_weight": weight,
                })

                if issuer != self.project_id and issuer_trust >= 0.5 and weight > 0.0:
                    trusted_denouncers.append(issuer)

        # 6. Noisy-OR aggregation: P = 1 - prod(1 - w_i)
        pos = 1.0
        for w in vouch_weights:
            pos *= (1.0 - max(0.0, min(1.0, w)))
        pos = 1.0 - pos

        neg = 1.0
        for w in denounce_weights:
            neg *= (1.0 - max(0.0, min(1.0, w)))
        neg = 1.0 - neg

        # 7. Check campaign membership across all observed fingerprints
        all_fps = list(self.pr_fingerprints.values())
        clusters = cluster_near_duplicates(all_fps)
        campaign_members, _ = identify_campaign_members(clusters)
        is_campaign_member = contributor in campaign_members
        is_exempt_from_hold = is_campaign_member and (pos >= 0.60)

        # 8. Verdict assignment
        trusted_denouncers_count = len(trusted_denouncers)

        # BLOCK Rule:
        # Only if project itself denounced, OR at least 2 independent trusted issuers with
        # combined weight >= 0.7 and neg > pos
        if is_own_denounced:
            verdict = Verdict.BLOCK
            reason = "Direct project denouncement"
        elif trusted_denouncers_count >= 2 and neg >= 0.70 and neg > pos:
            verdict = Verdict.BLOCK
            reason = f"Corroborated by {trusted_denouncers_count} trusted projects (combined weight {neg:.3f} > {pos:.3f})"
        elif is_campaign_member and not is_exempt_from_hold:
            # Campaign membership alone gives HOLD (human triage), never BLOCK
            verdict = Verdict.HOLD
            reason = "Identified as campaign member; held for human review"
        elif not records_by_issuer and not is_campaign_member:
            # Contributor with no records gets PROBATION, never a rejection
            verdict = Verdict.PROBATION
            reason = "No network history; placed on probation"
        elif pos >= 0.60 and pos > neg:
            verdict = Verdict.TRUST
            reason = f"High positive trust score {pos:.3f}"
        elif pos >= 0.20 and pos >= neg:
            verdict = Verdict.ALLOW
            reason = f"Positive trust score {pos:.3f} meets allowance threshold"
        elif neg > pos:
            verdict = Verdict.FLAG
            reason = f"Negative signal {neg:.3f} exceeds positive {pos:.3f} (does not meet block threshold)"
        else:
            verdict = Verdict.PROBATION
            reason = "Neutral or insufficient trust signal"

        return EvaluationResult(
            contributor=contributor,
            verdict=verdict,
            pos=pos,
            neg=neg,
            reason=reason,
            trusted_denouncers_count=trusted_denouncers_count,
            is_campaign_member=is_campaign_member,
            is_exempt_from_hold=is_exempt_from_hold,
            details={
                "vouchers": details_vouchers,
                "denouncers": details_denouncers,
                "is_own_denounced": is_own_denounced,
            },
        )

