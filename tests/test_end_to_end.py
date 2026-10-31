"""Scaled-down end-to-end integration test for TrustNet."""

from __future__ import annotations

import time
import pytest

from trustmesh.node import Node, Verdict


def test_scaled_down_end_to_end_run() -> None:
    """Runs a scaled-down end-to-end scenario across 6 nodes.

    Scenario:
    - 4 Honest nodes (alpha, beta, gamma, delta)
    - 2 Sybil nodes (sybil1, sybil2)
    - 1 Campaign bot targeting 4 projects
    - 1 Honest newcomer targeting 1 project
    - 1 Smear victim targeted by sybils
    - Verifies gossip propagation, campaign detection, auto-denouncement, and final verdicts.
    """
    t_start = 1760000000.0

    # 1. Initialize nodes
    nodes = {
        "alpha": Node("alpha", seed="alpha_seed"),
        "beta": Node("beta", seed="beta_seed"),
        "gamma": Node("gamma", seed="gamma_seed"),
        "delta": Node("delta", seed="delta_seed"),
        "sybil1": Node("sybil1", seed="sybil1_seed"),
        "sybil2": Node("sybil2", seed="sybil2_seed"),
    }

    # 2. Wire topology
    t = t_start
    nodes["alpha"].declare_peer("beta", 0.90, ts=t)
    t += 1
    nodes["beta"].declare_peer("gamma", 0.85, ts=t)
    t += 1
    nodes["gamma"].declare_peer("delta", 0.85, ts=t)
    t += 1
    nodes["delta"].declare_peer("alpha", 0.85, ts=t)
    t += 1

    # Sybils trust each other
    nodes["sybil1"].declare_peer("sybil2", 1.0, ts=t)
    t += 1
    nodes["sybil2"].declare_peer("sybil1", 1.0, ts=t)
    t += 1

    # 3. Campaign bot submissions across 4 projects (within 12h)
    camp_text = "Fix minor typo in README documentation"
    for idx, p_id in enumerate(["alpha", "beta", "gamma", "delta"]):
        nodes[p_id].publish_pr_fingerprint(
            contributor="bot_x",
            pr_id=f"pr_bot_{p_id}",
            text=camp_text,
            additions=1,
            account_age_days=2.0,
            outcome="open",
            is_low_value=True,
            ts=t + (idx * 3600.0),
        )

    # Also 2 other companion bots in the campaign to establish multi-account cluster
    for other_b in ["bot_y", "bot_z"]:
        for idx, p_id in enumerate(["alpha", "beta", "gamma", "delta"]):
            nodes[p_id].publish_pr_fingerprint(
                contributor=other_b,
                pr_id=f"pr_{other_b}_{p_id}",
                text=camp_text,
                additions=1,
                account_age_days=2.0,
                outcome="open",
                is_low_value=True,
                ts=t + (idx * 3600.0) + 10.0,
            )

    # 4. Honest newcomer submits 1 PR to beta
    nodes["beta"].publish_pr_fingerprint(
        contributor="honest_newbie",
        pr_id="pr_newbie_1",
        text="Add comprehensive benchmark harness for core runtime",
        additions=120,
        account_age_days=45.0,
        outcome="open",
        is_low_value=False,
        ts=t + 15000.0,
    )

    # 5. Sybils smear innocent Alice
    nodes["sybil1"].denounce("alice_innocent", reason="Slander", ts=t + 16000.0)
    nodes["sybil2"].denounce("alice_innocent", reason="Slander", ts=t + 16010.0)

    # 6. Execute 2 rounds of gossip
    for _ in range(2):
        for n in nodes.values():
            n.gossip_round(nodes, random_count=2)

    # Process automated campaign denouncements at honest nodes
    t_eval = t + 24.0 * 3600.0
    for p_id in ["alpha", "beta", "gamma", "delta"]:
        nodes[p_id].process_campaign_autodenunciations(ts=t_eval)

    # Final gossip round to propagate auto-denouncements
    for n in nodes.values():
        n.gossip_round(nodes, random_count=2)

    # 7. Evaluate verdicts at observer node 'alpha'
    eval_camp = nodes["alpha"].evaluate("bot_x", now=t_eval + 3600.0)
    assert eval_camp.verdict in (Verdict.HOLD, Verdict.BLOCK)

    eval_newbie = nodes["alpha"].evaluate("honest_newbie", now=t_eval + 3600.0)
    assert eval_newbie.verdict == Verdict.PROBATION
    assert eval_newbie.verdict != Verdict.BLOCK

    eval_alice = nodes["alpha"].evaluate("alice_innocent", now=t_eval + 3600.0)
    assert eval_alice.verdict != Verdict.BLOCK
    assert eval_alice.neg == 0.0

