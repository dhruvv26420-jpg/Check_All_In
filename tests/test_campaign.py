"""
Unit tests for TrustMesh Coordinated Spam Campaign Detector.
Verifies semantic clustering, temporal sliding windows, and Sybil wave detection.
"""

import time
import pytest

from trustmesh.models import PREvent
from trustmesh.campaign import CampaignDetector


def test_legitimate_distinct_prs():
    """
    Test 1: 5 distinct PRs with different features/diffs across different repos
    must NOT trigger any campaign alerts.
    """
    detector = CampaignDetector()
    base_time = time.time()

    legit_prs = [
        PREvent(
            pr_id="pr_legit_001",
            repo_id="org/mesh-core",
            author="core_maintainer_alice",
            account_age_days=180.0,
            timestamp=base_time,
            title="feat: implement localized trust propagation across peer vertices",
            diff_content="""
+def propagate_trust(weights: np.ndarray, adj: np.ndarray) -> np.ndarray:
+    return np.dot(adj, weights)
""",
            files_changed=["src/trustmesh/graph.py"],
        ),
        PREvent(
            pr_id="pr_legit_002",
            repo_id="org/storage-adapter",
            author="infra_bob",
            account_age_days=95.0,
            timestamp=base_time + 120.0,
            title="fix: database connection pool timeout on read-replica failover",
            diff_content="""
-    if conn.is_expired():
-        conn.reconnect()
+    if conn.is_expired():
+        conn.reconnect(timeout=30.0, retry=3)
""",
            files_changed=["adapters/postgres.py"],
        ),
        PREvent(
            pr_id="pr_legit_003",
            repo_id="org/ci-runners",
            author="devops_carol",
            account_age_days=400.0,
            timestamp=base_time + 300.0,
            title="ci: configure automated dependency security scans via bandit",
            diff_content="""
+      - name: Run security vulnerability audit
+        run: bandit -r src/ -ll -ii
""",
            files_changed=[".github/workflows/security.yml"],
        ),
        PREvent(
            pr_id="pr_legit_004",
            repo_id="org/crypto-primitives",
            author="systems_dave",
            account_age_days=620.0,
            timestamp=base_time + 500.0,
            title="perf: vectorize matrix multiplication using AVX-512 intrinsics in C++ core",
            diff_content="""
+    __m512d va = _mm512_loadu_pd(ptr_a + i);
+    __m512d vb = _mm512_loadu_pd(ptr_b + i);
+    __m512d vres = _mm512_fmadd_pd(va, vb, vzero);
""",
            files_changed=["native/simd.cpp"],
        ),
        PREvent(
            pr_id="pr_legit_005",
            repo_id="org/docs-portal",
            author="technical_writer_eve",
            account_age_days=310.0,
            timestamp=base_time + 700.0,
            title="docs: add architecture diagram and sequence flows for decentralized consensus",
            diff_content="""
+## Decentralized Consensus Flow
+```mermaid
+sequenceDiagram
+  Client->>PeerA: Vouch Query
+  PeerA->>PeerB: Route Request
+```
""",
            files_changed=["docs/architecture.md"],
        ),
    ]

    alerts, flagged_map = detector.analyze_events(legit_prs)
    assert len(alerts) == 0
    assert len(flagged_map) == 0


def test_coordinated_spam_burst_detected():
    """
    Test 2: Coordinated spam wave.
    38 simulated PR events with slight variations of a trivial typo/docstring diff
    from 3-day-old accounts hitting 38 distinct repos within 90 minutes.
    Must trigger an alert with cluster_size=38, affected_repos_count=38, mean_similarity >= 0.85.
    """
    detector = CampaignDetector(
        similarity_threshold=0.85,
        time_window_seconds=7200.0,
        min_cluster_size=4,
        min_repo_dispersion=3,
        max_account_age_days=7.0,
    )
    base_time = time.time()

    spam_title_variants = [
        "Fixed typo in README",
        "Fix minor typo in README.md",
        "Update docs header typo",
        "Fix typo in documentation",
        "Corrected typo in README file",
        "Minor typo correction in README.md",
        "Docs: fix typo in README",
    ]

    spam_diff_variants = [
        """
- The decentralized trust network are initialized automatically.
+ The decentralized trust network is initialized automatically.
- See docs/installation.md for details.
+ See docs/install.md for details.
""",
        """
- The decentralized trust network are initialized automatically.
+ The decentralized trust network is initialized automatically.
- Refer to docs/installation.md for setup instructions.
+ Refer to docs/install.md for setup instructions.
""",
        """
- The decentralized trust network are initialized.
+ The decentralized trust network is initialized.
- Check docs/installation.md.
+ Check docs/install.md.
""",
    ]

    burst_events = []
    for i in range(38):
        # 38 distinct repositories
        repo_id = f"community/open-project-{i:03d}"
        # 3-day-old newcomer accounts
        author = f"sybil_bot_{i:03d}"
        # Submissions spread over 90 minutes (5400 seconds)
        ts = base_time + (i * 5400.0 / 38.0)
        title = spam_title_variants[i % len(spam_title_variants)]
        diff = spam_diff_variants[i % len(spam_diff_variants)]

        event = PREvent(
            pr_id=f"pr_spam_{i:03d}",
            repo_id=repo_id,
            author=author,
            account_age_days=3.0,
            timestamp=ts,
            title=title,
            diff_content=diff,
            files_changed=["README.md"],
        )
        burst_events.append(event)

    alerts, flagged_map = detector.analyze_events(burst_events)

    assert len(alerts) == 1
    alert = alerts[0]
    assert alert.detected is True
    assert alert.cluster_size == 38
    assert alert.affected_repos_count == 38
    assert alert.mean_similarity >= 0.85
    assert alert.time_span_minutes <= 95.0
    assert len(flagged_map) == 38


def test_temporal_decay_filter():
    """
    Test 3: Temporal decay / isolation.
    The same 38 similar PRs, but timestamps are spread over 30 days
    (inter-arrival time ~19 hours >> 2-hour window).
    Must NOT trigger a coordinated burst alert.
    """
    detector = CampaignDetector(
        similarity_threshold=0.85,
        time_window_seconds=7200.0,  # 2 hours
        min_cluster_size=4,
        min_repo_dispersion=3,
        max_account_age_days=7.0,
    )
    base_time = time.time()

    spread_events = []
    for i in range(38):
        repo_id = f"community/open-project-{i:03d}"
        author = f"user_account_{i:03d}"
        # Spread evenly across 30 days (2,592,000 seconds)
        ts = base_time + (i * (30.0 * 86400.0) / 38.0)

        event = PREvent(
            pr_id=f"pr_spread_{i:03d}",
            repo_id=repo_id,
            author=author,
            account_age_days=3.0,
            timestamp=ts,
            title="Fixed typo in README",
            diff_content="- The trust network are initialized.\n+ The trust network is initialized.",
            files_changed=["README.md"],
        )
        spread_events.append(event)

    alerts, flagged_map = detector.analyze_events(spread_events)
    assert len(alerts) == 0
    assert len(flagged_map) == 0


# ==============================================================================
# MinHash & LSH Campaign Clustering Unit Tests
# ==============================================================================

from trustmesh.campaign import (
    FingerprintItem,
    cluster_near_duplicates,
    compute_minhash,
    identify_campaign_members,
    minhash_similarity,
    normalize_pr_text,
)
from trustmesh.node import Node, Verdict as NodeVerdict


