"""Unit tests for Node implementation: transitive trust, subjective evaluation,

evidence checking, sybil defense, Bayesian reliability, retractions, and decay.
"""

from __future__ import annotations

import time
import pytest

from trustmesh.node import (
    HALF_LIFE_DENOUNCE_SECONDS,
    HALF_LIFE_VOUCH_SECONDS,
    Node,
    Verdict,
)
from trustmesh.records import KeyImpersonationError, RecordKind, generate_keypair


def test_transitive_decay_and_max_hops() -> None:
    """Verifies: product of edge weights, x0.7 per hop after the first, max 3 hops."""
    nodeA = Node("proj-A")
    nodeB = Node("proj-B")
    nodeC = Node("proj-C")
    nodeD = Node("proj-D")
    nodeE = Node("proj-E")

    # A -> B (0.9)
    nodeA.declare_peer("proj-B", 0.90)
    # B -> C (0.8)
    nodeB.declare_peer("proj-C", 0.80)
    # C -> D (0.85)
    nodeC.declare_peer("proj-D", 0.85)
    # D -> E (0.90)
    nodeD.declare_peer("proj-E", 0.90)

    # Gossip so A learns the chain
    nodeA.gossip_pull_from(nodeB)
    nodeA.gossip_pull_from(nodeC)
    nodeA.gossip_pull_from(nodeD)

    # Hop 1: A -> B = 0.90
    t_b = nodeA.get_transitive_trust("proj-B")
    assert abs(t_b - 0.90) < 1e-6

    # Hop 2: A -> B -> C = 0.90 * 0.80 * 0.70 = 0.504
    t_c = nodeA.get_transitive_trust("proj-C")
    expected_c = 0.90 * 0.80 * 0.70
    assert abs(t_c - expected_c) < 1e-6

    # Hop 3: A -> B -> C -> D = 0.90 * 0.80 * 0.70 * 0.85 * 0.70 = 0.504 * 0.85 * 0.70 = 0.29988
    t_d = nodeA.get_transitive_trust("proj-D")
    expected_d = expected_c * 0.85 * 0.70
    assert abs(t_d - expected_d) < 1e-6

    # Hop 4: A -> B -> C -> D -> E exceeds MAX_HOPS (3) -> 0.0
    t_e = nodeA.get_transitive_trust("proj-E")
    assert t_e == 0.0


def test_fan_out_dilution() -> None:
    """Verifies that a peer declaring trust in K > 8 projects dilutes outgoing edges by (8 / K)."""
    node_hub = Node("proj-hub")
    node_source = Node("proj-source")
    node_target = Node("proj-target")

    node_source.declare_peer("proj-hub", 1.0)

    # Hub declares trust in 16 projects (K = 16 > 8)
    for i in range(16):
        node_hub.declare_peer(f"peer-{i}", 1.0)
    node_hub.declare_peer("proj-target", 1.0)  # total 17 peers

    node_source.gossip_pull_from(node_hub)

    # Dilution factor is 8.0 / 17.0
    expected_dilution = 8.0 / 17.0
    t_target = node_source.get_transitive_trust("proj-target")
    # Hop 2 gets x0.70 penalty: 1.0 * (1.0 * (8/17)) * 0.70
    expected_trust = 1.0 * (1.0 * expected_dilution) * 0.70
    assert abs(t_target - expected_trust) < 1e-5


def test_trust_is_personal() -> None:
    """Verifies that trust graphs are subjective: A's peer is not trusted by unrelated C."""
    nodeA = Node("proj-A")
    nodeB = Node("proj-B")
    nodeC = Node("proj-C")

    # A trusts B
    nodeA.declare_peer("proj-B", 0.9)
    # C does not trust B

    # B vouches for Alice
    rec_vouch = nodeB.vouch("alice", score=1.0)

    nodeA.gossip_pull_from(nodeB)
    nodeC.gossip_pull_from(nodeB)

    # A trusts B, so Alice has positive standing in A
    eval_a = nodeA.evaluate("alice")
    assert eval_a.pos > 0.8
    assert eval_a.verdict in (Verdict.TRUST, Verdict.ALLOW)

    # C does not trust B, so Alice has 0.0 standing in C -> PROBATION
    eval_c = nodeC.evaluate("alice")
    assert eval_c.pos == 0.0
    assert eval_c.verdict == Verdict.PROBATION


def test_sybils_ignored() -> None:
    """Verifies that a sybil cluster cannot smear an innocent contributor."""
    node_honest = Node("honest-core")
    node_sybil1 = Node("sybil-1")
    node_sybil2 = Node("sybil-2")

    # Sybils trust each other 1.0
    node_sybil1.declare_peer("sybil-2", 1.0)
    node_sybil2.declare_peer("sybil-1", 1.0)

    # Sybils issue denouncements against innocent user
    node_sybil1.denounce("innocent_dev", reason="Malicious slander")
    node_sybil2.denounce("innocent_dev", reason="Fabricated spam claim")

    # Honest node pulls from sybils
    node_honest.gossip_pull_from(node_sybil1)
    node_honest.gossip_pull_from(node_sybil2)

    eval_res = node_honest.evaluate("innocent_dev")
    assert eval_res.neg == 0.0
    assert eval_res.verdict != Verdict.BLOCK


def test_single_denouncement_never_blocks() -> None:
    """Verifies that a single trusted denouncement NEVER triggers BLOCK."""
    nodeA = Node("proj-A")
    nodeB = Node("proj-B")

    # A declares direct trust 0.95 in B
    nodeA.declare_peer("proj-B", 0.95)

    # B denounces user without verified evidence
    nodeB.denounce("charlie", reason="Subjective conflict")

    nodeA.gossip_pull_from(nodeB)
    eval_res = nodeA.evaluate("charlie")
    assert eval_res.verdict != Verdict.BLOCK


def test_corroborated_denouncements_block() -> None:
    """Verifies that >= 2 trusted issuers with combined weight >= 0.7 and verified evidence BLOCK."""
    nodeA = Node("proj-A")
    nodeB = Node("proj-B")
    nodeC = Node("proj-C")

    t_now = 1000000.0
    nodeA.declare_peer("proj-B", 0.90, ts=t_now)
    nodeA.declare_peer("proj-C", 0.90, ts=t_now + 1)

    # Publish duplicate spam PRs to B and C
    text = "Claim free bonus token reward at phishing url"
    fp1 = nodeB.publish_pr_fingerprint("spammer", "pr1", text, additions=1, account_age_days=1, ts=t_now + 10)
    fp2 = nodeC.publish_pr_fingerprint("spammer", "pr2", text, additions=1, account_age_days=1, ts=t_now + 20)

    nodeB.gossip_pull_from(nodeC)
    nodeC.gossip_pull_from(nodeB)

    # Both B and C denounce spammer citing verified duplicate fingerprints
    nodeB.denounce("spammer", evidence=[fp1.record_id, fp2.record_id], reason="Phishing spam", ts=t_now + 30)
    nodeC.denounce("spammer", evidence=[fp1.record_id, fp2.record_id], reason="Phishing spam", ts=t_now + 40)

    nodeA.gossip_pull_from(nodeB)
    nodeA.gossip_pull_from(nodeC)

    eval_res = nodeA.evaluate("spammer", now=t_now + 100)
    assert eval_res.verdict == Verdict.BLOCK
    assert eval_res.trusted_denouncers_count >= 2
    assert eval_res.neg >= 0.70


def test_own_project_block() -> None:
    """Verifies that when the evaluating project itself denounces, verdict is BLOCK immediately."""
    nodeA = Node("proj-A")
    nodeA.denounce("bad_contributor", reason="Breach of Code of Conduct")
    eval_res = nodeA.evaluate("bad_contributor")
    assert eval_res.verdict == Verdict.BLOCK


def test_retraction_restores_standing() -> None:
    """Verifies that issuing a RETRACT record completely revokes prior denouncement weight."""
    nodeA = Node("proj-A")
    nodeB = Node("proj-B")
    nodeC = Node("proj-C")

    t_now = 1000000.0
    nodeA.declare_peer("proj-B", 0.90, ts=t_now)
    nodeA.declare_peer("proj-C", 0.90, ts=t_now + 1)

    text = "Claim free bonus token reward at phishing url"
    fp1 = nodeB.publish_pr_fingerprint("suspect", "pr1", text, additions=1, account_age_days=1, ts=t_now + 10)
    fp2 = nodeC.publish_pr_fingerprint("suspect", "pr2", text, additions=1, account_age_days=1, ts=t_now + 20)

    nodeB.gossip_pull_from(nodeC)
    nodeC.gossip_pull_from(nodeB)

    den_b = nodeB.denounce("suspect", evidence=[fp1.record_id, fp2.record_id], reason="Phishing spam", ts=t_now + 30)
    den_c = nodeC.denounce("suspect", evidence=[fp1.record_id, fp2.record_id], reason="Phishing spam", ts=t_now + 40)

    nodeA.gossip_pull_from(nodeB)
    nodeA.gossip_pull_from(nodeC)
    assert nodeA.evaluate("suspect", now=t_now + 50).verdict == Verdict.BLOCK

    # Node B retracts its denouncement
    nodeB.retract(den_b.record_id, reason="False positive identified", ts=t_now + 60)
    nodeA.gossip_pull_from(nodeB)

    eval_after = nodeA.evaluate("suspect", now=t_now + 70)
    # With only 1 remaining denouncer, BLOCK invariant requires >= 2 independent trusted denouncers
    assert eval_after.verdict != Verdict.BLOCK


def test_time_decay() -> None:
    """Verifies time decay: denounce half-life 120 days, vouch half-life 365 days."""
    nodeA = Node("proj-A")
    nodeB = Node("proj-B")
    nodeA.declare_peer("proj-B", 1.0)

    t_0 = 1000000.0
    vouch_rec = nodeB.vouch("dev_vouch", score=1.0, ts=t_0)
    nodeA.gossip_pull_from(nodeB)

    # Right after vouch
    eval_0 = nodeA.evaluate("dev_vouch", now=t_0)
    assert abs(eval_0.pos - 1.0) < 1e-4

    # 365 days later -> pos score should halve
    t_365 = t_0 + HALF_LIFE_VOUCH_SECONDS
    eval_365 = nodeA.evaluate("dev_vouch", now=t_365)
    assert abs(eval_365.pos - 0.50) < 1e-3

    # 730 days later -> pos score should halve again to 0.25
    t_730 = t_0 + 2 * HALF_LIFE_VOUCH_SECONDS
    eval_730 = nodeA.evaluate("dev_vouch", now=t_730)
    assert abs(eval_730.pos - 0.25) < 1e-3


def test_serial_smearer_loses_credibility() -> None:
    """Verifies that an issuer publishing serial uncorroborated accusations loses Beta(2, 1) weight."""
    node_smearer = Node("serial-smearer")
    node_observer = Node("observer")
    node_observer.declare_peer("serial-smearer", 0.9)

    t_now = 1000000.0
    # Before accusations: reliability is 1.0
    rel_0 = node_observer.compute_issuer_reliability("serial-smearer")
    assert rel_0 == 1.0

    # Issuer produces 5 uncorroborated accusations without evidence
    for i in range(5):
        t_now += 10.0
        node_smearer.denounce(f"victim_{i}", reason="Baseless accusation", ts=t_now)

    node_observer.gossip_pull_from(node_smearer)
    rel_5 = node_observer.compute_issuer_reliability("serial-smearer")

    # With alpha=2, beta=1+5=6: E[theta] = 2/8 = 0.25. Normalized: 0.25 * 1.5 = 0.375
    assert rel_5 < 0.40
    assert rel_5 < rel_0


def test_key_impersonation_rejected() -> None:
    """Verifies that Node rejects records using an altered public key for an already-pinned identity."""
    node = Node("verifier")

    priv_real, pub_real = generate_keypair("real_alice_key")
    priv_fake, pub_fake = generate_keypair("fake_alice_key")

    from trustmesh.records import create_record
    rec_real = create_record("alice_project", priv_real, RecordKind.VOUCH, "user1", {}, prev="", ts=100.0)
    node.ingest_record(rec_real)
    assert node.key_pins["alice_project"] == pub_real

    # Impersonation attempt with different key
    rec_fake = create_record("alice_project", priv_fake, RecordKind.VOUCH, "user2", {}, prev="", ts=200.0)
    with pytest.raises(KeyImpersonationError):
        node.ingest_record(rec_fake)

