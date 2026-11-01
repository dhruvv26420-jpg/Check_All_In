import math
import time
import pytest
import numpy as np
from trustmesh.models import PREvent
from trustmesh.graph import TrustNetwork
from trustmesh.campaign import CampaignDetector
from trustmesh.evaluator import TrustMeshEngine

# ==============================================================================
# 1. COMPROMISED CREDENTIALS (VOUCH VS. CAMPAIGN PRECEDENCE)
# ==============================================================================

def test_compromised_vouched_account_in_campaign_is_quarantined():
    """A vouched developer caught participating in an active bot campaign MUST be quarantined."""
    net = TrustNetwork()
    net.add_project_trust("Your-Project", "Project-B", 1.0)
    net.add_vouch("Project-B", "compromised_alice", 1.0)

    detector = CampaignDetector(min_cluster_size=3, min_repo_dispersion=2)
    engine = TrustMeshEngine(net, detector)

    now = time.time()
    events = [
        PREvent(
            pr_id="pr_alice_spam",
            repo_id="Your-Project",
            author="compromised_alice",
            account_age_days=100.0,
            timestamp=now,
            title="Coordinated exploit update",
            diff_content="malicious payload injected into root"
        ),
        PREvent(
            pr_id="pr_bot_2",
            repo_id="Target-Repo-2",
            author="bot_2",
            account_age_days=2.0,
            timestamp=now + 10,
            title="Coordinated exploit update",
            diff_content="malicious payload injected into root"
        ),
        PREvent(
            pr_id="pr_bot_3",
            repo_id="Target-Repo-3",
            author="bot_3",
            account_age_days=2.0,
            timestamp=now + 20,
            title="Coordinated exploit update",
            diff_content="malicious payload injected into root"
        )
    ]

    decision = engine.audit_pull_request("Your-Project", events[0], events)
    assert decision.verdict == "QUARANTINE_CAMPAIGN"
    assert "ALLOW" not in decision.verdict
    assert decision.is_campaign_member is True


# ==============================================================================
# 2. OUT-OF-ORDER EVENT INGESTION
# ==============================================================================

def test_out_of_order_event_timestamps():
    """Events arriving in non-chronological order must still form a valid cluster."""
    detector = CampaignDetector(min_cluster_size=3, min_repo_dispersion=2, time_window_seconds=3600.0)
    now = time.time()

    # Inverted order: t+200, t+0, t+100
    events = [
        PREvent(
            pr_id="pr_unordered_3",
            repo_id="Repo-Z",
            author="bot_c",
            account_age_days=1.0,
            timestamp=now + 200,
            title="Syn Flood Doc Update",
            diff_content="exact attack patch payload"
        ),
        PREvent(
            pr_id="pr_unordered_1",
            repo_id="Repo-X",
            author="bot_a",
            account_age_days=1.0,
            timestamp=now,
            title="Syn Flood Doc Update",
            diff_content="exact attack patch payload"
        ),
        PREvent(
            pr_id="pr_unordered_2",
            repo_id="Repo-Y",
            author="bot_b",
            account_age_days=1.0,
            timestamp=now + 100,
            title="Syn Flood Doc Update",
            diff_content="exact attack patch payload"
        )
    ]

    alerts, pr_map = detector.analyze_events(events)
    assert len(alerts) == 1
    assert alerts[0].detected is True
    assert len(pr_map) == 3


# ==============================================================================
# 3. IDENTITY NORMALIZATION (CASING & SPACES)
# ==============================================================================

def test_handle_normalization_prevents_denouncement_evasion():
    """Attacker using differing uppercase/lowercase handles must not bypass quarantine."""
    net = TrustNetwork()
    net.add_project_trust("Your-Project", "Project-C", 1.0)
    # Denounce in lowercase
    net.add_denouncement("Project-C", "malicious_dev", 1.0, "Verified bad actor")

    # Ingest PR in uppercase
    audit_upper = net.evaluate_contributor("Your-Project", "MALICIOUS_DEV")
    
    # Check if handle matching handles case insensitivity
    applied = (
        len(audit_upper.denouncements_applied) > 0 or 
        audit_upper.verdict == "QUARANTINE_DENOUNCED"
    )
    assert applied, "Case discrepancy allowed denounced entity to evade quarantine."


# ==============================================================================
# 4. RAW BINARY / NULL-BYTE DIFF INGESTION
# ==============================================================================

def test_null_byte_and_binary_diff_safety():
    """Ensure raw binary payloads with null bytes (\x00) do not crash tokenizer."""
    detector = CampaignDetector()
    binary_diff = "diff --git a/binary.bin b/binary.bin\n\x00\x00\x01\x02\xff\xfe\x00\x1b"
    
    pr = PREvent(
        pr_id="pr_bin",
        repo_id="Repo-1",
        author="fuzzer",
        account_age_days=5.0,
        timestamp=time.time(),
        title="feat: raw asset",
        diff_content=binary_diff
    )
    
    # Must encode without raising ValueError
    vec = detector.embed_pr(pr)
    assert vec is not None
    assert len(vec) > 0


# ==============================================================================
# 5. NAN / DATA-POISONING ATTACK RESILIENCE
# ==============================================================================

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


# ==============================================================================
# 6. BAYESIAN EXTREME FLOAT NUMERICAL STABILITY
# ==============================================================================

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


# ==============================================================================
# 7. NAMESPACE SEPARATION (PROJECT VS. CONTRIBUTOR IDENTITY OVERLAP)
# ==============================================================================

def test_graph_node_identity_overlap_does_not_cross_wire():
    """A contributor with the exact same name as a trusted project must not inherit project trust."""
    net = TrustNetwork()
    net.add_project_trust("Your-Project", "Peer-Project", 1.0)
    
    result = net.evaluate_contributor("Your-Project", contributor_id="Your-Project")
    
    assert result.verdict == "UNCERTAIN_NEWCOMER"
    assert result.effective_trust == 0.0

