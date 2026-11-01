"""
TrustMesh Unified Evaluation Engine & Bayesian Newcomer Triage.

Core implementation for Hack Day Sonipat:
Problem 07: Decentralized Trust Network for Open Source

Key Architectural Capabilities:
- Bayesian Cold-Start Newcomer Triage with Beta(alpha, beta) Epistemic Uncertainty:
  Quantifies uncertainty for first-time contributors using a Beta-Binomial conjugate update:
  alpha = alpha_0 + w_vouch, beta = beta_0 + w_denounce.
  When network history is 0, E[T] = 0.5 and Var(T) = 0.0833 (high entropy).
  Safeguards honest newcomers from automatic exclusion, routing them to low-friction
  human review rather than quarantine.
- Transitive Trust Decay via Multi-Hop Peering:
  Evaluates established contributor provenance across multi-hop project peering edges.
- Asymmetric Negative Isolation:
  Quarantines hostile untrusted denouncements so malicious entities cannot poison
  a newcomer's or peer's reputation.
- Spatiotemporal Diff Clustering over Sliding Windows:
  Pre-filters incoming pull requests through 2-hour sliding window semantic clustering
  (SentenceTransformers all-MiniLM-L6-v2) to quarantine coordinated Sybil spam bursts.
"""

import math
from typing import List, Tuple, Dict, Optional, Any
import numpy as np

from trustmesh.models import (
    PREvent,
    CampaignAlert,
    AuditResult,
    UnifiedAuditDecision,
    Verdict,
)
from trustmesh.graph import TrustNetwork
from trustmesh.campaign import CampaignDetector


class TrustMeshEngine:
    """
    Unified Trust & Triage Engine for Problem 07.
    
    Synthesizes:
    1. Spatiotemporal Diff Clustering over Sliding Windows (SentenceTransformers all-MiniLM-L6-v2):
       Scans PR streams for coordinated Sybil campaigns using dense embeddings.
    2. Transitive Trust Decay via Multi-Hop Peering & Asymmetric Negative Isolation:
       Propagates vouches and quarantines hostile untrusted denouncements.
    3. Bayesian Cold-Start Newcomer Triage with Beta(alpha, beta) Epistemic Uncertainty:
       Quantifies epistemic variance to protect legitimate first-time contributors.
    """

    def __init__(
        self,
        network: Optional[TrustNetwork] = None,
        detector: Optional[CampaignDetector] = None,
        trust_threshold: float = 0.5,
    ):
        self.network = network if network is not None else TrustNetwork()
        self.detector = detector if detector is not None else CampaignDetector()
        self.trust_threshold = trust_threshold

    def compute_bayesian_trust(
        self,
        vouches_weight: float = 0.0,
        denounces_weight: float = 0.0,
        prior_alpha: float = 1.0,
        prior_beta: float = 1.0,
    ) -> Tuple[float, float]:
        """
        Computes Beta-Binomial conjugate Bayesian posterior expected trust and epistemic uncertainty.

        alpha = prior_alpha + vouches_weight
        beta  = prior_beta + denounces_weight

        Expected Trust:
            E[T] = alpha / (alpha + beta)
        Epistemic Uncertainty (Variance):
            Var(T) = (alpha * beta) / ((alpha + beta)^2 * (alpha + beta + 1))

        When history is 0 (vouches=0, denounces=0):
            alpha = 1.0, beta = 1.0 -> E[T] = 0.5, Var(T) = 1/12 = 0.0833
        """
        alpha = max(0.001, prior_alpha + max(0.0, float(vouches_weight)))
        beta = max(0.001, prior_beta + max(0.0, float(denounces_weight)))

        total = alpha + beta
        expected_trust = alpha / total
        try:
            variance = (alpha * beta) / ((total ** 2) * (total + 1.0))
        except OverflowError:
            variance = 0.0

        if math.isnan(expected_trust):
            expected_trust = 0.0
        if math.isnan(variance):
            variance = 0.0

        return round(float(expected_trust), 4), round(float(variance), 4)

    def audit_pull_request(
        self,
        inspecting_repo: str,
        pr: PREvent,
        event_history: Optional[List[PREvent]] = None,
    ) -> UnifiedAuditDecision:
        """
        Performs a full multi-signal audit on a pull request:
        
        Step 1: Ingest into CampaignDetector to scan for coordinated cross-repo spam bursts.
        Step 2: If clean of campaigns, evaluate contributor provenance in the Web-of-Trust network.
        Step 3: If newcomer with zero reputation, apply Bayesian uncertainty update and route to maintainer triage.
        """
        history = list(event_history) if event_history is not None else []
        if not any(item.pr_id == pr.pr_id for item in history):
            history.append(pr)

        evidence_trace: List[str] = []

        # ======================================================================
        # Step 1: Scan for Coordinated Spam Waves (SentenceTransformers)
        # ======================================================================
        alerts, flagged_map = self.detector.analyze_events(history)
        is_campaign_member = pr.pr_id in flagged_map
        campaign_id = flagged_map.get(pr.pr_id)

        if is_campaign_member and campaign_id:
            matching_alert = next((a for a in alerts if a.campaign_id == campaign_id), None)
            sim_score = matching_alert.mean_similarity if matching_alert else 0.95
            repos_count = matching_alert.affected_repos_count if matching_alert else 0
            cluster_size = matching_alert.cluster_size if matching_alert else 0

            # Bayesian update heavily penalized by campaign affinity
            exp_trust, uncertainty = self.compute_bayesian_trust(
                vouches_weight=0.0,
                denounces_weight=12.0 * sim_score,
            )

            evidence_trace.append(f"Flagged as participant in coordinated Sybil campaign '{campaign_id}'.")
            evidence_trace.append(
                f"Cluster: {cluster_size} near-identical PRs across {repos_count} repositories."
            )
            evidence_trace.append(f"Semantic similarity: {sim_score:.3f} via all-MiniLM-L6-v2 embeddings.")
            evidence_trace.append(
                f"Bayesian posterior trust collapsed to {exp_trust:.4f} (Var: {uncertainty:.4f})."
            )

            return UnifiedAuditDecision(
                pr_id=pr.pr_id,
                contributor_id=pr.author,
                target_repo=inspecting_repo,
                graph_trust_score=0.0,
                is_vouched=False,
                is_campaign_member=True,
                campaign_id=campaign_id,
                bayesian_expected_trust=exp_trust,
                bayesian_uncertainty=uncertainty,
                verdict=Verdict("QUARANTINE_CAMPAIGN"),
                action_recommendation="Auto-dismiss and flag cluster author",
                evidence_trace=evidence_trace,
            )

        # ======================================================================
        # Step 2: Web-of-Trust Graph Analysis & Asymmetric Negative Isolation
        # ======================================================================
        graph_audit = self.network.evaluate_contributor(
            inspecting_repo,
            pr.author,
            trust_threshold=self.trust_threshold,
        )

        graph_trust = graph_audit.effective_trust
        is_vouched = graph_audit.is_vouched
        denouncements_applied = graph_audit.denouncements_applied
        denouncements_ignored = graph_audit.denouncements_ignored

        # Case 2A: Trusted peer denouncement confirmed
        if len(denouncements_applied) > 0:
            total_severity = sum(float(d.severity) for d in denouncements_applied)
            exp_trust, uncertainty = self.compute_bayesian_trust(
                vouches_weight=graph_trust,
                denounces_weight=total_severity * 6.0,
            )

            evidence_trace.append(
                f"Contributor denounced by {len(denouncements_applied)} verified peer project(s)."
            )
            for den in denouncements_applied:
                evidence_trace.append(
                    f"Denouncement from '{den.project_id}': {den.reason} (Severity: {den.severity:.2f})"
                )
            if denouncements_ignored:
                evidence_trace.append(
                    f"Discarded {len(denouncements_ignored)} hostile denouncements via Asymmetric Negative Isolation."
                )

            return UnifiedAuditDecision(
                pr_id=pr.pr_id,
                contributor_id=pr.author,
                target_repo=inspecting_repo,
                graph_trust_score=graph_trust,
                is_vouched=is_vouched,
                is_campaign_member=False,
                campaign_id=None,
                bayesian_expected_trust=exp_trust,
                bayesian_uncertainty=uncertainty,
                verdict=Verdict("QUARANTINE_DENOUNCED"),
                action_recommendation="Block PR: Contributor denounced by trusted peer",
                evidence_trace=evidence_trace,
            )

        # Case 2B: Provenance verified via transitive vouches
        if is_vouched:
            exp_trust, uncertainty = self.compute_bayesian_trust(
                vouches_weight=graph_trust * 8.0,
                denounces_weight=0.0,
            )

            evidence_trace.append(
                f"Verified contributor via transitive Web-of-Trust (effective trust: {graph_trust:.4f})."
            )
            evidence_trace.append("Passed local semantic spam filter: 0 cluster matches.")
            if denouncements_ignored:
                for ign in denouncements_ignored:
                    evidence_trace.append(
                        f"Isolated and discarded untrusted denouncement from '{ign.project_id}' ({ign.filter_reason})."
                    )
            evidence_trace.append(
                f"Bayesian confidence high (E[T]: {exp_trust:.4f}, Var: {uncertainty:.4f})."
            )

            return UnifiedAuditDecision(
                pr_id=pr.pr_id,
                contributor_id=pr.author,
                target_repo=inspecting_repo,
                graph_trust_score=graph_trust,
                is_vouched=True,
                is_campaign_member=False,
                campaign_id=None,
                bayesian_expected_trust=exp_trust,
                bayesian_uncertainty=uncertainty,
                verdict=Verdict("ALLOW_VOUCHED"),
                action_recommendation="Fast-track merge: Provenance verified via Web-of-Trust",
                evidence_trace=evidence_trace,
            )

        # ======================================================================
        # Step 3: Honest Newcomer Scenario (Bayesian Uncertainty Triage)
        # ======================================================================
        # First-time contributor with zero prior vouches and zero active denouncements.
        exp_trust, uncertainty = self.compute_bayesian_trust(
            vouches_weight=0.0,
            denounces_weight=0.0,
        )

        evidence_trace.append("Zero prior reputation records in Web-of-Trust (cold-start newcomer).")
        evidence_trace.append("Passed semantic spam filter: no coordinated burst affinity.")
        if denouncements_ignored:
            for ign in denouncements_ignored:
                evidence_trace.append(
                    f"Asymmetric Negative Isolation protected newcomer: ignored hostile claim from untrusted '{ign.project_id}'."
                )
        evidence_trace.append(
            f"Bayesian Triage: E[T]={exp_trust:.2f}, High Epistemic Uncertainty (Var={uncertainty:.4f})."
        )
        evidence_trace.append("Applying non-exclusionary Hack Day Sonipat Problem 07 fairness policy.")

        return UnifiedAuditDecision(
            pr_id=pr.pr_id,
            contributor_id=pr.author,
            target_repo=inspecting_repo,
            graph_trust_score=graph_trust,
            is_vouched=False,
            is_campaign_member=False,
            campaign_id=None,
            bayesian_expected_trust=exp_trust,
            bayesian_uncertainty=uncertainty,
            verdict=Verdict("HONEST_NEWCOMER_TRIAGE"),
            action_recommendation="Route to standard human review queue. Do not block. Contributor exhibits no malicious cluster affinity.",
            evidence_trace=evidence_trace,
        )

