#!/usr/bin/env python3
"""
TrustMesh Interactive Local Demo — Hack Day Sonipat Scenario
Simulates Asymmetric Negative Isolation on a 3-project decentralized trust topology.
"""

import sys
from pathlib import Path

# Ensure src/ and .venv site-packages are on sys.path
REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "src"))

# Support running directly via `python3 demo_local.py` even without activating .venv
venv_site_pattern = REPO_ROOT / ".venv" / "lib"
if venv_site_pattern.is_dir():
    for site_pkg in venv_site_pattern.glob("python*/site-packages"):
        if str(site_pkg) not in sys.path:
            sys.path.insert(1, str(site_pkg))

from trustmesh import TrustNetwork

# ANSI terminal colors
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
DIM = "\033[2m"


def main():
    print(f"\n{BOLD}{CYAN}{'=' * 75}{RESET}")
    print(f"{BOLD}{CYAN}   TrustMesh — Decentralized Trust Network for Open Source{RESET}")
    print(f"{DIM}   Hack Day Sonipat (Problem 07) — Interactive Engine Demo{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 75}{RESET}\n")

    # 1. Initialize Network
    net = TrustNetwork()

    # 2. Build 3-Project Topology
    # Your-Project trusts Project-B (verified partner)
    # Your-Project DOES NOT trust Project-X (untrusted/adversarial entity)
    inspecting_project = "Your-Project"
    contributor = "@new-dev"

    print(f"{BOLD}[1] Building Web-of-Trust Topology:{RESET}")
    net.add_project_trust(inspecting_project, "Project-B", weight=0.95, context="Verified upstream dependency")
    print(f"  • {GREEN}✓ Peered:{RESET} {inspecting_project} ──(weight: 0.95)──> Project-B")
    print(f"  • {YELLOW}⚠ Unpeered:{RESET} Project-X has NO trust edge from {inspecting_project} (Reputation: 0.00)")

    # 3. Register Positive Signal (Vouch)
    print(f"\n{BOLD}[2] Registering Contributor Signals:{RESET}")
    vouch = net.add_vouch(
        "Project-B",
        contributor,
        confidence=0.90,
        notes="Consistently delivers high-quality PRs with 100% test coverage",
    )
    print(f"  • {GREEN}✓ Positive Vouch:{RESET} Project-B vouched for {contributor} (Confidence: 0.90)")

    # 4. Register Negative Signal (Malicious Denouncement from Project-X)
    denounce = net.add_denouncement(
        "Project-X",
        contributor,
        severity=1.00,
        reason="Alleged Sybil / spam contributor without evidence",
    )
    print(f"  • {RED}✗ Hostile Denouncement:{RESET} Project-X denounced {contributor} (Severity: 1.00)")

    # 5. Execute Evaluation with Asymmetric Negative Isolation
    print(f"\n{BOLD}[3] Executing Trust Evaluation from perspective of '{inspecting_project}':{RESET}")
    trust_threshold = 0.50
    audit = net.evaluate_contributor(inspecting_project, contributor, trust_threshold=trust_threshold)

    # 6. Render Colorized Evaluation Table
    verdict_color = GREEN if "ALLOW" in audit.verdict else (RED if "QUARANTINE" in audit.verdict else YELLOW)
    verdict_badge = f"{verdict_color}{BOLD}[ {audit.verdict} ]{RESET}"

    ignored_summary = (
        f"{YELLOW}Project-X (Severity: 1.0, Filter: Denouncer untrusted by local project [Reputation: 0.00]){RESET}"
        if audit.denouncements_ignored
        else "None"
    )

    print("\n" + "┌" + "─" * 73 + "┐")
    print(f"│ {BOLD}AUDIT SUMMARY & ASYMMETRIC NEGATIVE ISOLATION RESULTS{RESET}{' ' * 23}│")
    print("├" + "─" * 73 + "┤")
    print(f"│  {BOLD}Contributor ID:{RESET}             {CYAN}{audit.contributor_id:<46}{RESET}│")
    print(f"│  {BOLD}Inspecting Project:{RESET}         {inspecting_project:<46}│")
    print(f"│  {BOLD}Trust Threshold:{RESET}            {trust_threshold:<46}│")
    print(f"│  {BOLD}Effective Transitive Trust:{RESET} {GREEN}{audit.effective_trust:<46}{RESET}│")
    print(f"│  {BOLD}Inherited Vouch Path:{RESET}       {inspecting_project} -> Project-B (0.95) -> {contributor} (0.90)   │")
    print("├" + "─" * 73 + "┤")
    print(f"│  {BOLD}Denouncements Applied:{RESET}      {len(audit.denouncements_applied):<46}│")
    print(f"│  {BOLD}Denouncements Ignored:{RESET}      {len(audit.denouncements_ignored):<46}│")
    for ignored in audit.denouncements_ignored:
        msg = f"  └── {YELLOW}Ignored from '{ignored.project_id}': {ignored.reason[:32]}...{RESET}"
        print(f"│{msg:<83}│")
    print("├" + "─" * 73 + "┤")
    print(f"│  {BOLD}Final Evaluation Verdict:{RESET}   {verdict_badge:<55}│")
    print("└" + "─" * 73 + "┘")

    print(f"\n{BOLD}{GREEN}✔ Analysis Complete:{RESET} Hostile denouncement was safely isolated because Project-X")
    print(f"  lacks a trusted path from {inspecting_project}. {contributor} is approved via Project-B's vouch.\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
