"""
Final-Boss Edge Case Test Suite for TrustMesh.

Validates:
1. NaN / data-poisoning resilience in CampaignDetector (adversarial account_age_days).
2. Numerical stability in Bayesian epistemic uncertainty calculations under extreme float evidence.
3. Separation of concern between Project Graph Peering and Contributor Graph Identity namespaces.
"""

import math
import time
import pytest
import numpy as np
from trustmesh.models import PREvent
from trustmesh.graph import TrustNetwork
from trustmesh.campaign import CampaignDetector
from trustmesh.evaluator import TrustMeshEngine


def test_nan_account_age_does_not_shield_campaign():
    """An attacker injecting NaN account age must not bypass the campaign detector."""
    detector = CampaignDetector(min_cluster_size=3, min_repo_dispersion=2)
    now = time.time()
    
    events = [
        PREvent(pr_id="pr_1", repo_id="R1", author="bot1", account_age_days=1.0, timestamp=now, title="Spam", diff_content="payload"),
        PREvent(pr_id="pr_2", repo_id="R2", author="bot2", account_age_days=1.0, timestamp=now, title="Spam", diff_content="payload"),
        PREvent(pr_id="pr_3", repo_id="R3", author="bot3", account_age_days=float("nan"), timestamp=now, title="Spam", diff_content="payload")
    ]
    
    alerts, pr_map = detector.analyze_events(events)
    assert len(alerts) == 1, "CRITICAL: NaN injection shielded campaign from detection"
    assert alerts[0].detected is True


def test_bayesian_extreme_float_evidence():
    """Ensure massive amounts of evidence don't trigger OverflowError or NaN in variance."""
    net = TrustNetwork()
    detector = CampaignDetector()
    engine = TrustMeshEngine(net, detector)

    exp, var = engine.compute_bayesian_trust(vouches_weight=0.0, denounces_weight=100000.0)
    
    assert exp < 0.001
    assert var < 0.001
    assert not math.isnan(exp)
    assert not math.isnan(var)


def test_graph_node_identity_overlap_does_not_cross_wire():
    """A contributor with the exact same name as a trusted project must not inherit project trust."""
    net = TrustNetwork()
    net.add_project_trust("Your-Project", "Peer-Project", 1.0)
    
    result = net.evaluate_contributor("Your-Project", contributor_id="Your-Project")
    
    assert result.verdict == "UNCERTAIN_NEWCOMER"
    assert result.effective_trust == 0.0

