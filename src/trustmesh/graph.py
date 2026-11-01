"""
TrustMesh Web-of-Trust Graph Engine.

Core implementation for Hack Day Sonipat:
Problem 07: Decentralized Trust Network for Open Source

Key Architectural Capabilities:
- Transitive Trust Decay via Multi-Hop Peering:
  Computes continuous trust attenuation across decentralized project-to-project graphs,
  mapping edge weights to lowest-attenuation paths via Dijkstra negative-log transforms.
- Asymmetric Negative Isolation:
  Protects contributors against Sybil smear campaigns by quarantining hostile untrusted
  denouncements. Negative assertions from unpeered or untrusted projects are isolated
  into `denouncements_ignored` and cannot unilaterally degrade a contributor's reputation.
- Inter-Project Peering & Contributor Signals:
  Manages directed graph layers for peerings, vouches, and denouncements.
"""

import math
from typing import Dict, List, Optional, Any, Union
import networkx as nx

from trustmesh.models import (
    TrustEdge,
    VouchRecord,
    DenounceRecord,
    AuditResult,
    Verdict,
    DenouncementEntry,
)


class TrustNetwork:
    """
    Decentralized Web-of-Trust Graph Engine for Problem 07.
    
    Implements:
    - Transitive Trust Decay via Multi-Hop Peering:
      Computes transitive trust product along optimal peering paths.
    - Asymmetric Negative Isolation:
      Quarantines hostile untrusted denouncements by validating denouncer
      reputation against local project trust thresholds.
    
    Maintains:
    - project_graph: Directed graph of inter-project peering relationships.
    - contributor_graph: Multi-directed graph of positive vouches and negative denouncements.
    """

    def __init__(self):
        self.project_graph: nx.DiGraph = nx.DiGraph()
        self.contributor_graph: nx.MultiDiGraph = nx.MultiDiGraph()
        self.vouches: List[VouchRecord] = []
        self.denouncements: List[DenounceRecord] = []

    def add_project_trust(
        self,
        source_project: str,
        target_project: str,
        weight: float = 1.0,
        context: Optional[str] = None,
    ) -> TrustEdge:
        """
        Registers an inter-project peering trust relationship.
        
        Args:
            source_project: Identifier of the trusting project.
            target_project: Identifier of the trusted project.
            weight: Trust weight in [0.0, 1.0].
            context: Optional context description (e.g. shared organization, code dependency).
        """
        weight_clamped = max(0.0, min(1.0, float(weight)))
        # -log(w) represents attenuation distance: 1.0 -> 0.0 distance, 0.0 -> inf
        safe_w = max(weight_clamped, 1e-9)
        neg_log_w = -math.log(safe_w)

        self.project_graph.add_edge(
            source_project,
            target_project,
            weight=weight_clamped,
            neg_log_weight=neg_log_w,
            context=context,
        )

        edge = TrustEdge(
            source_id=source_project,
            target_id=target_project,
            weight=weight_clamped,
            context=context,
        )
        return edge

    def add_vouch(
        self,
        project: str,
        contributor: str,
        confidence: float = 1.0,
        notes: Optional[str] = None,
    ) -> VouchRecord:
        """
        Registers a positive assertion (vouch) from a project about a contributor.
        """
        conf_clamped = max(0.0, min(1.0, float(confidence)))
        record = VouchRecord(
            project_id=project,
            contributor_id=contributor,
            confidence=conf_clamped,
            notes=notes,
        )
        self.vouches.append(record)
        self.contributor_graph.add_edge(
            project,
            contributor,
            key=f"vouch_{len(self.vouches)}",
            signal_type="vouch",
            confidence=conf_clamped,
            notes=notes,
        )
        return record

    def add_denouncement(
        self,
        project: str,
        contributor: str,
        severity: float = 1.0,
        reason: str = "",
    ) -> DenounceRecord:
        """
        Registers a negative assertion (denouncement) from a project about a contributor.
        """
        sev_clamped = max(0.0, min(1.0, float(severity)))
        record = DenounceRecord(
            project_id=project,
            contributor_id=contributor,
            severity=sev_clamped,
            reason=reason,
        )
        self.denouncements.append(record)
        self.contributor_graph.add_edge(
            project,
            contributor,
            key=f"denounce_{len(self.denouncements)}",
            signal_type="denounce",
            severity=sev_clamped,
            reason=reason,
        )
        return record

    def _find_project_node(self, project_id: str) -> Optional[str]:
        """Case-insensitive and whitespace-tolerant project node lookup."""
        target = project_id.strip().lower()
        for node in self.project_graph.nodes:
            if str(node).strip().lower() == target:
                return node
        return None

    def get_project_reputation(
        self,
        inspecting_project: str,
        target_project: str,
    ) -> float:
        """
        Computes transitive trust from inspecting_project to target_project
        using shortest path decay (product of edge weights along lowest-attenuation path).
        Returns 0.0 if unreachable.
        """
        if inspecting_project.strip().lower() == target_project.strip().lower():
            return 1.0

        src_node = self._find_project_node(inspecting_project)
        tgt_node = self._find_project_node(target_project)

        if src_node is None or tgt_node is None:
            return 0.0

        if not nx.has_path(self.project_graph, src_node, tgt_node):
            return 0.0

        try:
            # Shortest path on neg_log_weight minimizes sum(-log(w)), maximizing prod(w)
            path = nx.shortest_path(
                self.project_graph,
                source=src_node,
                target=tgt_node,
                weight="neg_log_weight",
            )
            accumulated_trust = 1.0
            for u, v in zip(path[:-1], path[1:]):
                edge_weight = self.project_graph[u][v].get("weight", 1.0)
                accumulated_trust *= float(edge_weight)

            return max(0.0, min(1.0, float(accumulated_trust)))
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return 0.0

    def evaluate_contributor(
        self,
        inspecting_project: str,
        contributor_id: str,
        trust_threshold: float = 0.5,
    ) -> AuditResult:
        """
        Evaluates a contributor from the local perspective of inspecting_project.
        
        Calculates:
        - Positive trust propagated through all vouched paths:
          effective_trust = max(T(inspecting, P) * confidence)
        - Asymmetric Negative Isolation:
          For each denouncement from Project X, verify T(inspecting, X).
          If T(inspecting, X) < trust_threshold -> ignore denouncement (denouncer untrusted).
          If T(inspecting, X) >= trust_threshold -> apply denouncement.
        - Verdict:
          * denouncements_applied non-empty -> QUARANTINE_DENOUNCED
          * effective_trust >= trust_threshold -> ALLOW_VOUCHED
          * otherwise -> UNCERTAIN_NEWCOMER
        """
        target_contrib = contributor_id.strip().lower()

        # 1. Evaluate positive vouches
        relevant_vouches = [
            v for v in self.vouches
            if v.contributor_id.strip().lower() == target_contrib
        ]
        path_trust_scores: List[float] = []

        for vouch in relevant_vouches:
            proj_rep = self.get_project_reputation(inspecting_project, vouch.project_id)
            propagated_confidence = proj_rep * vouch.confidence
            path_trust_scores.append(propagated_confidence)

        effective_trust = max(path_trust_scores) if path_trust_scores else 0.0
        is_vouched = effective_trust >= trust_threshold

        # 2. Evaluate negative denouncements with Asymmetric Negative Isolation
        relevant_denouncements = [
            d for d in self.denouncements
            if d.contributor_id.strip().lower() == target_contrib
        ]
        denouncements_ignored: List[DenouncementEntry] = []
        denouncements_applied: List[DenouncementEntry] = []

        for den in relevant_denouncements:
            denouncer_rep = self.get_project_reputation(inspecting_project, den.project_id)
            if denouncer_rep < trust_threshold:
                # Discard denouncement from untrusted source
                entry = DenouncementEntry(
                    project_id=den.project_id,
                    severity=den.severity,
                    reason=den.reason or "Denouncer is untrusted by local project",
                    denouncer_reputation=denouncer_rep,
                    filter_reason="Denouncer is untrusted by local project",
                )
                denouncements_ignored.append(entry)
            else:
                # Validated denouncement from a trusted peer
                entry = DenouncementEntry(
                    project_id=den.project_id,
                    severity=den.severity,
                    reason=den.reason,
                    denouncer_reputation=denouncer_rep,
                )
                denouncements_applied.append(entry)

        # 3. Verdict Determination
        if len(denouncements_applied) > 0:
            verdict = Verdict("QUARANTINE_DENOUNCED")
        elif effective_trust >= trust_threshold:
            verdict = Verdict("ALLOW_VOUCHED")
        else:
            verdict = Verdict("UNCERTAIN_NEWCOMER")

        return AuditResult(
            contributor_id=contributor_id,
            inspecting_project=inspecting_project,
            effective_trust=round(effective_trust, 4),
            is_vouched=is_vouched,
            denouncements_ignored=denouncements_ignored,
            denouncements_applied=denouncements_applied,
            verdict=verdict,
        )
