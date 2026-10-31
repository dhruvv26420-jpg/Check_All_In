"""
Unit tests for TrustMesh Web-of-Trust Graph Engine.
"""

import pytest
from trustmesh import TrustNetwork


def test_direct_vouch():
    """Test 1: Direct vouch from inspecting project results in ALLOW."""
    net = TrustNetwork()
    net.add_vouch("Your-Project", "@dev-direct", confidence=0.9)

    result = net.evaluate_contributor("Your-Project", "@dev-direct")
    
    assert result.verdict == "ALLOW"
    assert result.verdict == "ALLOW_VOUCHED"
    assert result.is_vouched is True
    assert result.effective_trust == pytest.approx(0.9)
    assert len(result.denouncements_applied) == 0
    assert len(result.denouncements_ignored) == 0


def test_transitive_vouch():
    """Test 2: Transitive vouch (Your Project -> Project B -> @new-dev) results in ALLOW."""
    net = TrustNetwork()
    net.add_project_trust("Your-Project", "Project-B", weight=0.8)
    net.add_vouch("Project-B", "@new-dev", confidence=0.9)

    result = net.evaluate_contributor("Your-Project", "@new-dev")

    assert result.verdict == "ALLOW"
    assert result.verdict == "ALLOW_VOUCHED"
    assert result.effective_trust == pytest.approx(0.72)
    assert result.is_vouched is True
    assert len(result.denouncements_applied) == 0


def test_hackathon_slide_scenario_untrusted_denouncement():
    """
    Test 3: Hackathon Slide Scenario (Asymmetric Negative Isolation).
    - Your Project trusts Project B.
    - Your Project DOES NOT trust Project X.
    - Project B vouches for @new-dev.
    - Project X denounces @new-dev.
    - Expected: verdict == "ALLOW_VOUCHED", denouncements_ignored contains Project X, denouncements_applied is empty.
    """
    net = TrustNetwork()
    net.add_project_trust("Your-Project", "Project-B", weight=1.0)
    # Note: Your-Project DOES NOT trust Project-X (no peering edge added)

    net.add_vouch("Project-B", "@new-dev", confidence=1.0, notes="Core contributor in Project-B")
    net.add_denouncement("Project-X", "@new-dev", severity=1.0, reason="Sybil / spam report")

    result = net.evaluate_contributor("Your-Project", "@new-dev", trust_threshold=0.5)

    assert result.verdict == "ALLOW_VOUCHED"
    assert result.verdict == "ALLOW"
    assert "Project-X" in result.denouncements_ignored
    assert len(result.denouncements_applied) == 0
    assert result.effective_trust == pytest.approx(1.0)
    assert result.is_vouched is True


def test_trusted_peer_denouncement():
    """
    Test 4: Trusted peer denouncement results in QUARANTINE.
    - Your Project trusts Project C.
    - Project C denounces @bad-actor.
    - Expected: verdict == "QUARANTINE_DENOUNCED" / "QUARANTINE".
    """
    net = TrustNetwork()
    net.add_project_trust("Your-Project", "Project-C", weight=0.9)
    net.add_denouncement("Project-C", "@bad-actor", severity=0.9, reason="Supply chain vulnerability attempt")

    result = net.evaluate_contributor("Your-Project", "@bad-actor")

    assert result.verdict == "QUARANTINE"
    assert result.verdict == "QUARANTINE_DENOUNCED"
    assert "Project-C" in result.denouncements_applied
    assert len(result.denouncements_applied) == 1
    assert len(result.denouncements_ignored) == 0


def test_uncertain_newcomer():
    """Test 5: An unvouched and undenounced contributor is flagged as UNCERTAIN_NEWCOMER."""
    net = TrustNetwork()
    result = net.evaluate_contributor("Your-Project", "@stranger")

    assert result.verdict == "UNCERTAIN"
    assert result.verdict == "UNCERTAIN_NEWCOMER"
    assert result.is_vouched is False
    assert result.effective_trust == 0.0


def test_project_reputation_decay():
    """Test 6: Multi-hop project peering decay computation."""
    net = TrustNetwork()
    net.add_project_trust("Project-A", "Project-B", weight=0.9)
    net.add_project_trust("Project-B", "Project-C", weight=0.8)

    assert net.get_project_reputation("Project-A", "Project-A") == 1.0
    assert net.get_project_reputation("Project-A", "Project-B") == pytest.approx(0.9)
    assert net.get_project_reputation("Project-A", "Project-C") == pytest.approx(0.72)
    assert net.get_project_reputation("Project-A", "Unknown-Project") == 0.0
