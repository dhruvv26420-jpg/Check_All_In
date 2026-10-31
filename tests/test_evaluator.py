"""
Unit tests for TrustMesh Unified Evaluation Engine & Bayesian Newcomer Triage.
"""

import time
import pytest

from trustmesh.models import PREvent
from trustmesh.evaluator import TrustMeshEngine


def test_vouched_contributor_fast_track():
    """
    Test 1: Provenance verified via transitive vouches results in ALLOW_VOUCHED
    with fast-track merge recommendation.
    """
    engine = TrustMeshEngine()
    engine.network.add_project_trust("Your-Project", "Project-B", weight=0.90)
    engine.network.add_vouch("Project-B", "alice_vouched", confidence=0.95)

    pr = PREvent(
        pr_id="pr_vouched_001",
        repo_id="Your-Project",
        author="alice_vouched",
        account_age_days=180.0,
        timestamp=time.time(),
        title="feat: implement core trust graph propagation routine",
        diff_content="+def propagate(): pass",
        files_changed=["src/trustmesh/graph.py"],
    )

    decision = engine.audit_pull_request("Your-Project", pr)

    assert decision.verdict == "ALLOW_VOUCHED"
    assert decision.is_vouched is True
    assert decision.is_campaign_member is False
    assert decision.graph_trust_score == pytest.approx(0.855, abs=0.01)
    assert decision.bayesian_expected_trust > 0.80
    assert "Fast-track merge" in decision.action_recommendation


def test_untrusted_denouncement_newcomer_protected():
    """
    Test 2: Untrusted Project X denounces clean newcomer -> HONEST_NEWCOMER_TRIAGE
    (hostile smear safely discarded via Asymmetric Negative Isolation).
    """
    engine = TrustMeshEngine()
    # Your-Project does NOT trust Project-X (no peering edge)
    engine.network.add_denouncement("Project-X", "charlie_clean", severity=1.0, reason="Malicious false claim")

    pr = PREvent(
        pr_id="pr_clean_002",
        repo_id="Your-Project",
        author="charlie_clean",
        account_age_days=4.0,
        timestamp=time.time(),
        title="fix: handle off-by-one boundary check in graph traversal",
        diff_content="""
-if i <= length:
+if i < length:
""",
        files_changed=["src/trustmesh/traversal.py"],
    )

    decision = engine.audit_pull_request("Your-Project", pr)

    assert decision.verdict == "HONEST_NEWCOMER_TRIAGE"
    assert decision.is_vouched is False
    assert decision.is_campaign_member is False
    assert "Route to standard human review" in decision.action_recommendation
    # Verify Project-X denouncement was noted as isolated/ignored in the trace
    assert any("Project-X" in trace for trace in decision.evidence_trace)


def test_sybil_bot_in_campaign_quarantined():
    """
    Test 3: Bot participating in a 38-PR cross-repo campaign -> QUARANTINE_CAMPAIGN.
    """
    engine = TrustMeshEngine()
    base_time = time.time()

    spam_titles = [
        "Fixed typo in README",
        "Fix minor typo in README.md",
        "Update docs header typo",
    ]

    spam_prs = []
    for i in range(38):
        pr = PREvent(
            pr_id=f"pr_spam_{i:03d}",
            repo_id=f"community/repo-{i:03d}",
            author=f"sybil_bot_{i:03d}",
            account_age_days=2.0,
            timestamp=base_time + (i * 3600.0 / 38.0),
            title=spam_titles[i % len(spam_titles)],
            diff_content="- The trust network are initialized.\n+ The trust network is initialized.",
            files_changed=["README.md"],
        )
        spam_prs.append(pr)

    target_pr = spam_prs[14]
    decision = engine.audit_pull_request("Your-Project", target_pr, event_history=spam_prs)

    assert decision.verdict == "QUARANTINE_CAMPAIGN"
    assert decision.is_campaign_member is True
    assert decision.campaign_id is not None
    assert "Auto-dismiss and flag" in decision.action_recommendation
    assert decision.bayesian_expected_trust < 0.20


def test_honest_cold_start_newcomer():
    """
    Test 4: Account with zero network history and novel PR -> HONEST_NEWCOMER_TRIAGE
    with expected trust ~0.50 and high epistemic uncertainty (Var ~0.0833).
    """
    engine = TrustMeshEngine()
    pr = PREvent(
        pr_id="pr_cold_start_001",
        repo_id="Your-Project",
        author="dave_cold_start",
        account_age_days=1.5,
        timestamp=time.time(),
        title="docs: improve contributor onboarding guidelines in README",
        diff_content="""
+### Quick Start
+```bash
+pip install -e .
+```
""",
        files_changed=["README.md"],
    )

    decision = engine.audit_pull_request("Your-Project", pr)

    assert decision.verdict == "HONEST_NEWCOMER_TRIAGE"
    assert decision.is_vouched is False
    assert decision.is_campaign_member is False
    assert decision.bayesian_expected_trust == pytest.approx(0.50, abs=0.01)
    assert decision.bayesian_uncertainty == pytest.approx(0.0833, abs=0.001)
    assert "Route to standard human review" in decision.action_recommendation
    assert "Do not block" in decision.action_recommendation

