"""
TrustMesh Command-Line Interface (CLI).

Supports:
- trustmesh audit --network <path> --events <path> --inspecting-repo <repo_id> [--output <path>]
- trustmesh demo
- trustmesh --list-models / --version
"""

import argparse
import json
import sys
import time
import warnings
from pathlib import Path
from typing import List, Dict, Any, Optional

from trustmesh import __version__
from trustmesh.models import PREvent, get_model_registry
from trustmesh.graph import TrustNetwork
from trustmesh.campaign import CampaignDetector
from trustmesh.evaluator import TrustMeshEngine

# ANSI formatting
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
DIM = "\033[2m"


def load_network_from_json(network_path: Path) -> TrustNetwork:
    """Load TrustNetwork from a JSON topology file."""
    with open(network_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    network = TrustNetwork()

    # Load project peerings
    peerings = data.get("peerings") or data.get("edges") or []
    for edge in peerings:
        src = edge.get("source") or edge.get("source_id") or edge.get("from")
        tgt = edge.get("target") or edge.get("target_id") or edge.get("to")
        weight = float(edge.get("weight", 1.0))
        context = edge.get("context")
        if src and tgt:
            network.add_project_trust(src, tgt, weight=weight, context=context)

    # Load positive assertions (vouches)
    vouches = data.get("vouches") or []
    for v in vouches:
        proj = v.get("project") or v.get("project_id")
        contributor = v.get("contributor") or v.get("contributor_id")
        conf = float(v.get("confidence", 1.0))
        notes = v.get("notes")
        if proj and contributor:
            network.add_vouch(proj, contributor, confidence=conf, notes=notes)

    # Load negative assertions (denouncements)
    denouncements = data.get("denouncements") or []
    for d in denouncements:
        proj = d.get("project") or d.get("project_id")
        contributor = d.get("contributor") or d.get("contributor_id")
        sev = float(d.get("severity", 1.0))
        reason = d.get("reason", "")
        if proj and contributor:
            network.add_denouncement(proj, contributor, severity=sev, reason=reason)

    return network


def load_events_from_json(events_path: Path) -> List[PREvent]:
    """Load list of PREvents from a JSON file."""
    with open(events_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    raw_events = data.get("events") if isinstance(data, dict) else data
    if not isinstance(raw_events, list):
        raise ValueError(f"Invalid events JSON format in {events_path}; expected list or object with 'events'")

    events: List[PREvent] = []
    for item in raw_events:
        events.append(PREvent(**item))
    return events


def run_audit(network_path: str, events_path: str, inspecting_repo: str, output_path: Optional[str] = None) -> int:
    """Execute trust audit on pull request events."""
    net_p = Path(network_path)
    ev_p = Path(events_path)

    if not net_p.exists():
        print(f"{RED}Error: Network file '{network_path}' not found.{RESET}", file=sys.stderr)
        return 1
    if not ev_p.exists():
        print(f"{RED}Error: Events file '{events_path}' not found.{RESET}", file=sys.stderr)
        return 1

    network = load_network_from_json(net_p)
    events = load_events_from_json(ev_p)

    engine = TrustMeshEngine(network=network)

    # Filter events: audit all events or target repo events
    target_events = [ev for ev in events if ev.repo_id == inspecting_repo]
    if not target_events:
        # If no events explicitly match inspecting_repo, evaluate all events against inspecting_repo
        target_events = events

    print(f"\n{BOLD}{CYAN}{'=' * 82}{RESET}")
    print(f"{BOLD}{CYAN}   TrustMesh Audit Report — Evaluating for: {inspecting_repo}{RESET}")
    print(f"{DIM}   Scanned: {len(events)} total ecosystem events | Auditing: {len(target_events)} target submissions{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 82}{RESET}\n")

    decisions = []
    summary_counts = {
        "ALLOW_VOUCHED": 0,
        "QUARANTINE_DENOUNCED": 0,
        "QUARANTINE_CAMPAIGN": 0,
        "HONEST_NEWCOMER_TRIAGE": 0,
    }

    print("┌" + "─" * 80 + "┐")
    print(
        f"│ {BOLD}{'PR ID':<14} │ {'Contributor':<16} │ {'WoT':<5} │ {'Spam':<5} │ {'E[T]':<6} │ {'Verdict':<23}{RESET}│"
    )
    print("├" + "─" * 80 + "┤")

    for pr in target_events:
        decision = engine.audit_pull_request(inspecting_repo, pr, event_history=events)
        decisions.append(decision)
        verdict_str = str(decision.verdict)
        summary_counts[verdict_str] = summary_counts.get(verdict_str, 0) + 1

        wot_badge = f"{GREEN}YES{RESET}" if decision.is_vouched else f"{DIM}NO{RESET} "
        spam_badge = f"{RED}HIT{RESET}" if decision.is_campaign_member else f"{GREEN}CLR{RESET}"

        if verdict_str == "ALLOW_VOUCHED":
            v_badge = f"{GREEN}{BOLD}ALLOW_VOUCHED{RESET}"
        elif verdict_str == "QUARANTINE_DENOUNCED":
            v_badge = f"{RED}{BOLD}QUARANTINE_DENOUNCED{RESET}"
        elif verdict_str == "QUARANTINE_CAMPAIGN":
            v_badge = f"{MAGENTA}{BOLD}QUARANTINE_CAMPAIGN{RESET}"
        else:
            v_badge = f"{YELLOW}{BOLD}HONEST_NEWCOMER_TRIAGE{RESET}"

        pr_tag = pr.pr_id[:13]
        author_tag = pr.author[:15]
        print(
            f"│ {pr_tag:<14} │ {author_tag:<16} │ {wot_badge} │ {spam_badge} │ {decision.bayesian_expected_trust:<6.2f} │ {v_badge:<32}│"
        )
        print(f"│   └── {DIM}{decision.action_recommendation[:71]}{RESET}│")

    print("└" + "─" * 80 + "┘")

    print(f"\n{BOLD}Audit Summary Breakdown:{RESET}")
    print(f"  • {GREEN}ALLOW_VOUCHED:{RESET}          {summary_counts.get('ALLOW_VOUCHED', 0)}")
    print(f"  • {YELLOW}HONEST_NEWCOMER_TRIAGE:{RESET}  {summary_counts.get('HONEST_NEWCOMER_TRIAGE', 0)} (protected from auto-exclusion)")
    print(f"  • {MAGENTA}QUARANTINE_CAMPAIGN:{RESET}     {summary_counts.get('QUARANTINE_CAMPAIGN', 0)}")
    print(f"  • {RED}QUARANTINE_DENOUNCED:{RESET}     {summary_counts.get('QUARANTINE_DENOUNCED', 0)}")

    if output_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        export_doc = {
            "@context": "https://openvex.dev/ns/v0.2.0",
            "generator": f"TrustMesh CLI v{__version__}",
            "inspecting_repository": inspecting_repo,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_audited": len(decisions),
            "summary": summary_counts,
            "decisions": [
                {
                    "pr_id": d.pr_id,
                    "contributor_id": d.contributor_id,
                    "target_repo": d.target_repo,
                    "graph_trust_score": d.graph_trust_score,
                    "is_vouched": d.is_vouched,
                    "is_campaign_member": d.is_campaign_member,
                    "campaign_id": d.campaign_id,
                    "bayesian_expected_trust": d.bayesian_expected_trust,
                    "bayesian_uncertainty": d.bayesian_uncertainty,
                    "verdict": str(d.verdict),
                    "action_recommendation": d.action_recommendation,
                    "evidence_trace": d.evidence_trace,
                }
                for d in decisions
            ],
        }
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(export_doc, f, indent=2)
        print(f"\n{GREEN}✔ Audit artifact exported to:{RESET} {out_p.resolve()}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="trustmesh",
        description="TrustMesh: Decentralized Trust Network for Open Source Contributions",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--list-models", action="store_true", help="List registered local open models")

    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # Subcommand: audit
    audit_parser = subparsers.add_parser("audit", help="Audit PR submissions against a Web-of-Trust topology")
    audit_parser.add_argument("--network", required=True, help="Path to network topology JSON file")
    audit_parser.add_argument("--events", required=True, help="Path to PR events JSON file")
    audit_parser.add_argument("--inspecting-repo", required=True, help="Repository ID performing the audit")
    audit_parser.add_argument("--output", required=False, help="Path to export JSON audit report")

    # Subcommand: demo
    subparsers.add_parser("demo", help="Run the interactive 4-persona TrustMesh demo")

    args = parser.parse_args()

    if args.list_models:
        print("Registered Local Open-Weight Models:")
        for role, meta in get_model_registry().items():
            print(f"  - [{role}] {meta['model_id']} ({meta['runtime']}) on {meta['device']}")
        return 0

    if args.subcommand == "audit":
        return run_audit(
            network_path=args.network,
            events_path=args.events,
            inspecting_repo=args.inspecting_repo,
            output_path=args.output,
        )

    if args.subcommand == "demo":
        from demo_unified import main as demo_main
        return demo_main()

    # Default fallback
    print(f"TrustMesh v{__version__} - Decentralized Trust Network.")
    print("Run 'trustmesh audit --help' or 'trustmesh demo' for interactive verification.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
