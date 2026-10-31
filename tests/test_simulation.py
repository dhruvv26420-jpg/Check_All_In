"""
TrustMesh 50-Repository Ecosystem Simulation Test.

Simulates 50 repositories, honest newcomers, trusted peers, and a 38-PR coordinated
Sybil spam campaign, asserting 100% TPR for spam, 0% FPR for newcomers, and 100%
neutralization of adversarial denouncements.
"""

import time
import pytest
from trustmesh.models import PREvent
from trustmesh.graph import TrustNetwork
from trustmesh.evaluator import TrustMeshEngine


def test_50_repo_ecosystem_simulation():
    """
    Constructs a 50-repository network with 120 PR events:
    - 10 core peer projects (high mutual trust)
    - 35 neutral projects
    - 5 untrusted / adversarial nodes
    - 70 legitimate PRs from vouched / repeat contributors
    - 12 genuine first-time newcomers
    - 38-PR coordinated Sybil campaign
    """
    base_time = time.time() - 3600.0
    network = TrustNetwork()
    inspecting_repo = "core_repo_00"

    # 1. Build 50-Repository Network Topology
    core_repos = [f"core_repo_{i:02d}" for i in range(10)]
    neutral_repos = [f"neutral_repo_{i:02d}" for i in range(35)]
    adversarial_repos = [f"adversarial_repo_{i:02d}" for i in range(5)]
    all_repos = core_repos + neutral_repos + adversarial_repos
    assert len(all_repos) == 50

    # Peer core repositories together with high trust (0.85 - 0.98)
    for i in range(len(core_repos)):
        for j in range(i + 1, min(i + 4, len(core_repos))):
            network.add_project_trust(core_repos[i], core_repos[j], weight=0.92, context="Core peering")
            network.add_project_trust(core_repos[j], core_repos[i], weight=0.92, context="Core peering")

    # Connect neutral repos with sparse links to core
    for i, n_repo in enumerate(neutral_repos):
        gateway_core = core_repos[i % len(core_repos)]
        network.add_project_trust(gateway_core, n_repo, weight=0.65, context="Neutral ecosystem project")

    # Adversarial nodes have NO incoming trust edges from core repos (Reputation = 0.0)

    # 2. Register Network Assertions
    # Core repos vouch for 10 established contributors
    established_devs = [f"established_dev_{i:02d}" for i in range(10)]
    for i, dev in enumerate(established_devs):
        vouching_repo = core_repos[(i + 1) % len(core_repos)]
        network.add_vouch(vouching_repo, dev, confidence=0.90, notes="Verified core contributor")

    # Adversarial nodes attempt to denounce 5 honest newcomers with hostile smear reports
    newcomer_devs = [f"newcomer_dev_{i:02d}" for i in range(12)]
    for i in range(5):
        network.add_denouncement(
            adversarial_repos[i],
            newcomer_devs[i],
            severity=1.00,
            reason="Adversarial malicious report attempting newcomer exclusion",
        )

    # 3. Ingest 120 Pull Request Events
    pr_events = []

    # Category A: 70 Legitimate PRs from established / vouched developers
    distinct_titles = [
        "feat: optimize sparse matrix multiplication in graph traversal",
        "fix: race condition in asynchronous connection pool reconnect",
        "perf: vectorize cosine similarity using AVX2 SIMD instructions",
        "docs: update API documentation for zero-trust token exchange",
        "refactor: modularize cryptographic verification routines",
        "ci: add automated reproducible builds with deterministic hashes",
        "test: add fuzzing harness for packet serialization boundary checks",
    ]
    for i in range(70):
        dev = established_devs[i % len(established_devs)]
        repo = core_repos[i % len(core_repos)]
        pr = PREvent(
            pr_id=f"pr_legit_{i:03d}",
            repo_id=repo,
            author=dev,
            account_age_days=120.0 + (i * 2.0),
            timestamp=base_time + (i * 45.0),
            title=f"{distinct_titles[i % len(distinct_titles)]} (v{i})",
            diff_content=f"// Implementation diff for feature batch {i}\n+int execute_batch_{i}() {{ return 0; }}",
            files_changed=[f"src/subsystem_{i % 5}.py"],
        )
        pr_events.append(pr)

    # Category B: 12 Genuine First-Time Newcomers (Novel, diverse contributions)
    newcomer_titles = [
        "docs: fix broken hyperlink in installation guide",
        "fix: typo in CLI error message flag validation",
        "feat: add export to JSON formatting option in reporter",
        "docs: clarify local setup requirements for macOS ARM64",
        "fix: handle empty input array gracefully in sanitizer",
        "chore: update outdated license notice in header",
        "test: add unit test for edge case in null parser",
        "docs: fix code example indentation in README",
        "fix: remove deprecated argument warning in logger",
        "style: format code according to PEP 8 standards",
        "docs: add troubleshooting section for OpenSSL compatibility",
        "refactor: simplify conditional branching in status check",
    ]
    newcomer_prs = []
    for i, dev in enumerate(newcomer_devs):
        repo = all_repos[i % len(all_repos)]
        pr = PREvent(
            pr_id=f"pr_newcomer_{i:03d}",
            repo_id=repo,
            author=dev,
            account_age_days=2.5 + (i * 0.3),
            timestamp=base_time + 1000.0 + (i * 120.0),
            title=newcomer_titles[i],
            diff_content=f"+# Contribution by {dev}\n-Old line {i}\n+New corrected line {i}",
            files_changed=["docs/guide.md" if i % 2 == 0 else "src/utils.py"],
        )
        pr_events.append(pr)
        newcomer_prs.append(pr)

    # Category C: 38-PR Coordinated Sybil Campaign
    # 38 distinct repositories hit in 45 minutes by 2-day-old accounts with near-identical diff
    spam_prs = []
    spam_targets = neutral_repos[:35] + core_repos[1:4]  # 38 distinct repositories
    assert len(spam_targets) == 38
    for i in range(38):
        bot_author = f"sybil_bot_{i:03d}"
        pr = PREvent(
            pr_id=f"pr_spam_{i:03d}",
            repo_id=spam_targets[i],
            author=bot_author,
            account_age_days=1.8,
            timestamp=base_time + 1500.0 + (i * 2700.0 / 38.0),  # within 45 minutes
            title="Fixed typo in README",
            diff_content="""
- The trust network are initialized automatically.
+ The trust network is initialized automatically.
- See docs/installation.md for details.
+ See docs/install.md for details.
""",
            files_changed=["README.md"],
        )
        pr_events.append(pr)
        spam_prs.append(pr)

    assert len(pr_events) == 120

    # 4. Execute Full Ecosystem Audit
    engine = TrustMeshEngine(network=network, trust_threshold=0.5)

    spam_caught = 0
    newcomers_quarantined = 0
    newcomers_triaged = 0
    legit_allowed = 0

    for pr in pr_events:
        decision = engine.audit_pull_request(inspecting_repo, pr, event_history=pr_events)

        if pr.pr_id.startswith("pr_spam_"):
            if decision.verdict == "QUARANTINE_CAMPAIGN":
                spam_caught += 1
        elif pr.pr_id.startswith("pr_newcomer_"):
            if "QUARANTINE" in decision.verdict:
                newcomers_quarantined += 1
            if decision.verdict == "HONEST_NEWCOMER_TRIAGE":
                newcomers_triaged += 1
        elif pr.pr_id.startswith("pr_legit_"):
            if decision.verdict == "ALLOW_VOUCHED":
                legit_allowed += 1

    # 5. Assert Ecosystem Invariants
    # Invariant 1: 100% True Positive Rate for spam burst
    tpr_spam = spam_caught / 38.0
    assert tpr_spam == 1.0, f"Expected 100% spam detection, got {tpr_spam * 100}% ({spam_caught}/38)"

    # Invariant 2: 0% False Positive Rate for newcomers (zero honest newcomers quarantined)
    fpr_newcomers = newcomers_quarantined / 12.0
    assert fpr_newcomers == 0.0, f"Expected 0% newcomer quarantine, got {newcomers_quarantined} quarantined"
    assert newcomers_triaged == 12, f"Expected all 12 newcomers routed to triage, got {newcomers_triaged}"

    # Invariant 3: Untrusted denouncements 100% neutralized
    # The 5 newcomers attacked by adversarial repos were NOT blocked
    attacked_newcomers = newcomer_prs[:5]
    for pr in attacked_newcomers:
        d = engine.audit_pull_request(inspecting_repo, pr, event_history=pr_events)
        assert d.verdict == "HONEST_NEWCOMER_TRIAGE"
        assert d.is_campaign_member is False
        assert any("adversarial_repo_" in trace for trace in d.evidence_trace)

    print("\nSimulation Metrics Verified:")
    print(f"  • Coordinated Spam TPR: {tpr_spam * 100:.1f}% (38/38 detected)")
    print(f"  • Newcomer Triage FPR:  {fpr_newcomers * 100:.1f}% (0/12 false positives)")
    print(f"  • Untrusted Denouncements Neutralized: 100% (5/5 isolated)")

