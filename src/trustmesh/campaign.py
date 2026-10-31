from __future__ import annotations
"""
TrustMesh Coordinated Spam Campaign Detector.

Core implementation for Hack Day Sonipat:
Problem 07: Decentralized Trust Network for Open Source

Key Architectural Capabilities:
- Spatiotemporal Diff Clustering over Sliding Windows:
  Tracks PR arrival streams within temporal sliding windows (default: delta_t <= 2 hours),
  building adjacency graphs where edges represent high semantic cosine similarity
  (default: >= 0.85) and small time deltas.
- Open-Weight Semantic Vector Embeddings:
  Converts PR diffs, titles, and file paths into 384-dimensional dense semantic vectors
  using local sentence-transformers/all-MiniLM-L6-v2 on CPU (zero cloud AI APIs).
- Multi-Repository Dispersion & Account Age Heuristics:
  Identifies coordinated Sybil attacks by flagging clusters spanning multiple distinct
  repositories from suspicious newcomer accounts (account age <= 7 days).
"""

import dataclasses
import hashlib
import math
import random
import re
import warnings
from typing import List, Tuple, Dict, Optional, Any
import numpy as np
import networkx as nx

# Suppress urllib3 LibreSSL platform warnings on macOS
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")
warnings.filterwarnings("ignore", message=".*urllib3 v2 only supports OpenSSL.*")

from trustmesh.models import PREvent, CampaignAlert


class CampaignDetector:
    """
    Detects coordinated multi-repository spam waves and Sybil PR campaigns for Problem 07.
    
    Utilizes:
    - Spatiotemporal Diff Clustering over Sliding Windows:
      Partitions incoming pull requests into temporal sliding windows (delta_t <= 2 hours)
      and extracts dense connected components based on cosine similarity.
    - Local Open-Weight Embeddings:
      Leverages sentence-transformers/all-MiniLM-L6-v2 on CPU with offline TF-IDF fallback.
    - Dispersion & Anomaly Heuristics:
      Evaluates cross-repo dispersion, cluster size thresholds, and newcomer account age.
    
    Attributes:
        model_name: HuggingFace model identifier for local SentenceTransformer.
        similarity_threshold: Minimum cosine similarity to link two submissions.
        time_window_seconds: Maximum time span for a coordinated burst (default: 2h).
        min_cluster_size: Minimum number of submissions to classify as a campaign.
        min_repo_dispersion: Minimum number of distinct repositories targeted.
        max_account_age_days: Upper bound for suspicious newcomer accounts (default: 7d).
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        similarity_threshold: float = 0.85,
        time_window_seconds: float = 7200.0,
        min_cluster_size: int = 4,
        min_repo_dispersion: int = 3,
        max_account_age_days: float = 7.0,
    ):
        self.model_name = model_name
        self.similarity_threshold = similarity_threshold
        self.time_window_seconds = time_window_seconds
        self.min_cluster_size = min_cluster_size
        self.min_repo_dispersion = min_repo_dispersion
        self.max_account_age_days = max_account_age_days

        self._model = None
        self._model_load_attempted = False
        self._offline_vectorizer = None
        self._embedding_cache: Dict[str, np.ndarray] = {}
        self._analysis_cache: Dict[int, Tuple[List[CampaignAlert], Dict[str, str]]] = {}

    def _get_model(self) -> Optional[Any]:
        """Lazy load SentenceTransformer on CPU."""
        if not self._model_load_attempted:
            self._model_load_attempted = True
            try:
                from sentence_transformers import SentenceTransformer
                try:
                    self._model = SentenceTransformer(self.model_name, device="cpu", local_files_only=True)
                except Exception:
                    self._model = SentenceTransformer(self.model_name, device="cpu")
            except Exception:
                self._model = None
        return self._model

    def _format_text(self, pr: PREvent) -> str:
        """Format PR event into semantic text for embedding."""
        files_str = " ".join(pr.files_changed) if pr.files_changed else "none"
        diff_snippet = pr.diff_content[:1500] if pr.diff_content else ""
        return f"Title: {pr.title}\nFiles: {files_str}\nDiff:\n{diff_snippet}"

    def embed_pr(self, pr: PREvent) -> np.ndarray:
        """
        Embed a single PR into a normalized feature vector.
        Uses SentenceTransformer if available, or offline fallback vectorizer.
        """
        text = self._format_text(pr)
        model = self._get_model()
        if model is not None:
            try:
                emb = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
                return np.asarray(emb, dtype=np.float32)
            except Exception as exc:
                # Log error and proceed to offline deterministic vectorizer fallback
                _ = exc

        # Offline fallback embedding (character & word n-gram hashing / TF-IDF)
        return self._offline_embed_single(text)

    def embed_batch(self, events: List[PREvent]) -> np.ndarray:
        """
        Embed a batch of PR events into a normalized 2D numpy array (N x D),
        using embedding cache where available.
        """
        if not events:
            return np.empty((0, 384), dtype=np.float32)

        # Check cached embeddings
        uncached_indices = []
        uncached_texts = []
        embs_dict: Dict[int, np.ndarray] = {}

        for idx, pr in enumerate(events):
            cache_key = f"{pr.pr_id}_{pr.title}_{pr.diff_content[:100]}"
            if cache_key in self._embedding_cache:
                embs_dict[idx] = self._embedding_cache[cache_key]
            else:
                uncached_indices.append((idx, cache_key))
                uncached_texts.append(self._format_text(pr))

        if uncached_texts:
            model = self._get_model()
            computed_embs = None
            if model is not None:
                try:
                    computed_embs = model.encode(uncached_texts, convert_to_numpy=True, normalize_embeddings=True)
                    computed_embs = np.asarray(computed_embs, dtype=np.float32)
                except Exception:
                    computed_embs = None

            if computed_embs is None:
                try:
                    from sklearn.feature_extraction.text import TfidfVectorizer
                    vectorizer = TfidfVectorizer(
                        analyzer="char_wb",
                        ngram_range=(3, 5),
                        sublinear_tf=True,
                        min_df=1,
                    )
                    matrix = vectorizer.fit_transform(uncached_texts).toarray().astype(np.float32)
                    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
                    norms[norms == 0] = 1.0
                    computed_embs = matrix / norms
                except Exception:
                    computed_embs = np.vstack([self._offline_embed_single(t) for t in uncached_texts])

            for (orig_idx, key), emb in zip(uncached_indices, computed_embs):
                self._embedding_cache[key] = emb
                embs_dict[orig_idx] = emb

        ordered_embs = [embs_dict[i] for i in range(len(events))]
        return np.vstack(ordered_embs)

    def _offline_embed_single(self, text: str, dim: int = 384) -> np.ndarray:
        """
        Lightweight deterministic feature hashing vectorizer for offline environments.
        Computes character 3-grams hashed into a dim-dimensional vector with L2 normalization.
        """
        vec = np.zeros(dim, dtype=np.float32)
        words = text.lower().split()
        for word in words:
            # Word hashing
            idx = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16) % dim
            vec[idx] += 1.0
            # Character trigrams
            for i in range(len(word) - 2):
                tri = word[i : i + 3]
                t_idx = int(hashlib.md5(tri.encode("utf-8")).hexdigest(), 16) % dim
                vec[t_idx] += 0.5

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec

    def analyze_events(
        self,
        events: List[PREvent],
    ) -> Tuple[List[CampaignAlert], Dict[str, str]]:
        """
        Analyzes a batch of PR events for coordinated spam campaigns.
        """
        if len(events) < self.min_cluster_size:
            return [], {}

        events_key = hash(tuple(pr.pr_id for pr in events))
        if events_key in self._analysis_cache:
            return self._analysis_cache[events_key]

        embeddings = self.embed_batch(events)
        n = len(events)

        # Pairwise cosine similarity matrix (dot product of L2-normalized vectors)
        sim_matrix = np.clip(np.dot(embeddings, embeddings.T), 0.0, 1.0)

        # Build graph connecting events that are both temporally and semantically close
        graph = nx.Graph()
        for i in range(n):
            graph.add_node(i)

        for i in range(n):
            for j in range(i + 1, n):
                sim = float(sim_matrix[i, j])
                time_delta = abs(events[i].timestamp - events[j].timestamp)
                if sim >= self.similarity_threshold and time_delta <= self.time_window_seconds:
                    graph.add_edge(i, j, similarity=sim, time_delta=time_delta)

        alerts: List[CampaignAlert] = []
        flagged_pr_map: Dict[str, str] = {}

        for component in nx.connected_components(graph):
            cluster_indices = list(component)
            cluster_events = [events[idx] for idx in cluster_indices]

            # Heuristic 1: Cluster size
            if len(cluster_events) < self.min_cluster_size:
                continue

            # Heuristic 2: Repository dispersion
            repos = sorted(list(set(pr.repo_id for pr in cluster_events)))
            if len(repos) < self.min_repo_dispersion:
                continue

            # Heuristic 3: Temporal span within cluster
            timestamps = [pr.timestamp for pr in cluster_events]
            min_ts = min(timestamps)
            max_ts = max(timestamps)
            time_span_seconds = max_ts - min_ts
            time_span_minutes = round(time_span_seconds / 60.0, 2)

            if time_span_seconds > self.time_window_seconds:
                # Outside sliding window
                continue

            # Heuristic 4: Account age check (newcomer accounts)
            account_ages = [pr.account_age_days for pr in cluster_events]
            mean_age = float(np.mean(account_ages))
            if mean_age > self.max_account_age_days:
                continue

            # Calculate mean similarity among members
            if len(cluster_indices) > 1:
                sub_sims = [
                    sim_matrix[i, j]
                    for idx_a, i in enumerate(cluster_indices)
                    for j in cluster_indices[idx_a + 1 :]
                ]
                mean_sim = float(np.mean(sub_sims)) if sub_sims else 1.0
            else:
                mean_sim = 1.0

            authors = sorted(list(set(pr.author for pr in cluster_events)))
            pr_ids = sorted([pr.pr_id for pr in cluster_events])

            # Generate deterministic campaign identifier
            campaign_hash = hashlib.sha256(
                f"{len(cluster_events)}:{'-'.join(repos)}:{min_ts}:{max_ts}".encode()
            ).hexdigest()[:12]
            campaign_id = f"camp_{campaign_hash}"

            evidence = (
                f"Coordinated spam burst detected: {len(cluster_events)} near-identical PRs "
                f"hitting {len(repos)} distinct repositories within {time_span_minutes:.1f} minutes. "
                f"Mean semantic similarity: {mean_sim:.3f}. "
                f"Average account age: {mean_age:.1f} days."
            )

            alert = CampaignAlert(
                detected=True,
                campaign_id=campaign_id,
                cluster_size=len(cluster_events),
                affected_repos_count=len(repos),
                affected_repos=repos,
                flagged_authors=authors,
                mean_similarity=round(mean_sim, 4),
                time_span_minutes=time_span_minutes,
                evidence_summary=evidence,
            )
            alerts.append(alert)

            for pr in cluster_events:
                flagged_pr_map[pr.pr_id] = campaign_id

        self._analysis_cache[events_key] = (alerts, flagged_pr_map)
        return alerts, flagged_pr_map


# ==============================================================================
# Deterministic 64-Permutation MinHash & LSH Clustering Engine
# ==============================================================================
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any",
    "are", "aren't", "as", "at", "be", "because", "been", "before", "being", "below",
    "between", "both", "but", "by", "can", "cannot", "could", "couldn't", "did", "didn't",
    "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for",
    "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having",
    "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", "i", "if",
    "in", "into", "is", "isn't", "it", "its", "itself", "just", "me", "more", "most",
    "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
    "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should",
    "shouldn't", "so", "some", "such", "than", "that", "the", "their", "theirs", "them",
    "themselves", "then", "there", "these", "they", "this", "those", "through", "to",
    "too", "under", "until", "up", "very", "was", "wasn't", "we", "were", "weren't",
    "what", "when", "where", "which", "while", "who", "whom", "why", "with", "won't",
    "would", "wouldn't", "you", "your", "yours", "yourself", "yourselves",
    "minor", "quick", "small", "simple", "little", "file", "files", "wording", "text", "various",
}

# Synonym folding map to collapse common semantic variations in PR templates
SYNONYM_FOLDING = {
    "fix": "fix", "fixed": "fix", "fixing": "fix", "correct": "fix", "corrected": "fix",
    "correcting": "fix", "patch": "fix", "patched": "fix", "patching": "fix", "repair": "fix",
    "resolve": "fix", "resolved": "fix", "resolving": "fix",
    "clean": "fix", "cleanup": "fix", "cleaning": "fix", "update": "fix", "updated": "fix",
    "updating": "fix", "modify": "fix", "modified": "fix", "bump": "fix", "bumped": "fix",
    "revise": "fix", "change": "fix", "changed": "fix", "improve": "fix", "improved": "fix",
    "typo": "typo", "typos": "typo", "spelling": "typo", "misspell": "typo", "misspelling": "typo",
    "grammar": "typo", "grammatical": "typo", "error": "typo", "errors": "typo",
    "mistake": "typo", "mistakes": "typo",
    "readme": "doc", "readmes": "doc", "doc": "doc", "docs": "doc", "documentation": "doc",
    "markdown": "doc", "manual": "doc",
    "add": "add", "added": "add", "adding": "add", "append": "add", "include": "add",
    "remove": "remove", "removed": "remove", "delete": "remove", "deleted": "remove",
}

NUM_PERMUTATIONS = 64
MERSENNE_PRIME = 2147483647  # 2^31 - 1
LSH_NUM_BANDS = 16
LSH_ROWS_PER_BAND = 4  # 16 * 4 = 64


def _generate_minhash_coefficients(seed: int = 42) -> list[tuple[int, int]]:
    """Generates 64 deterministic (a, b) hash parameter pairs for MinHash permutations."""
    rng = random.Random(seed)
    coeffs = []
    for _ in range(NUM_PERMUTATIONS):
        a = rng.randint(1, MERSENNE_PRIME - 1)
        b = rng.randint(0, MERSENNE_PRIME - 1)
        coeffs.append((a, b))
    return coeffs


MINHASH_COEFFS = _generate_minhash_coefficients(seed=42)


def normalize_pr_text(text: str) -> list[str]:
    """Normalizes PR text through tokenization, stopword removal, synonym folding, and deduplication."""
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    raw_tokens = cleaned.split()

    normalized_tokens: list[str] = []
    for tok in raw_tokens:
        if tok in STOPWORDS or len(tok) < 2:
            continue
        folded = SYNONYM_FOLDING.get(tok, tok)
        # Avoid duplicate consecutive tokens (e.g. documentation readme -> doc doc -> doc)
        if not normalized_tokens or normalized_tokens[-1] != folded:
            normalized_tokens.append(folded)

    return normalized_tokens


def generate_shingles(tokens: list[str]) -> set[str]:
    """Generates 1-gram and order-invariant pairwise co-occurrence shingles from normalized tokens."""
    if not tokens:
        return set()

    shingles = set(tokens)
    # Order-invariant pair shingles within a short context window
    for i in range(len(tokens)):
        for j in range(i + 1, min(i + 3, len(tokens))):
            t1, t2 = tokens[i], tokens[j]
            shingles.add(f"{min(t1, t2)}_{max(t1, t2)}")
    return shingles


def compute_minhash(text_or_shingles: str | list[str] | set[str]) -> list[int]:
    """Computes a 64-permutation MinHash signature for text or pre-extracted shingles."""
    if isinstance(text_or_shingles, str):
        tokens = normalize_pr_text(text_or_shingles)
        shingles = generate_shingles(tokens)
    elif isinstance(text_or_shingles, list):
        shingles = generate_shingles(text_or_shingles)
    else:
        shingles = text_or_shingles

    if not shingles:
        return [0] * NUM_PERMUTATIONS

    signature = [MERSENNE_PRIME] * NUM_PERMUTATIONS
    for shingle in shingles:
        # 32-bit integer hash of shingle
        h = int(hashlib.md5(shingle.encode("utf-8")).hexdigest()[:8], 16)
        for i, (a, b) in enumerate(MINHASH_COEFFS):
            val = (a * h + b) % MERSENNE_PRIME
            if val < signature[i]:
                signature[i] = val

    return signature


def minhash_similarity(sig_a: list[int], sig_b: list[int]) -> float:
    """Estimates Jaccard similarity between two 64-dim MinHash signatures."""
    if len(sig_a) != NUM_PERMUTATIONS or len(sig_b) != NUM_PERMUTATIONS:
        raise ValueError(f"MinHash signatures must have length {NUM_PERMUTATIONS}")

    matches = sum(1 for a, b in zip(sig_a, sig_b) if a == b)
    return matches / float(NUM_PERMUTATIONS)


@dataclasses.dataclass
class FingerprintItem:
    """Represents a PR fingerprint and its associated metadata."""

    record_id: str
    project: str
    contributor: str
    text: str
    minhash: list[int]
    account_age_days: float
    additions: int
    timestamp: float
    outcome: str = "open"
    is_low_value: bool = False

    @classmethod
    def from_record_payload(
        cls,
        record_id: str,
        subject: str,
        ts: float,
        payload: dict[str, Any],
    ) -> FingerprintItem:
        minhash = payload.get("minhash")
        if not minhash:
            minhash = compute_minhash(payload.get("text", ""))

        additions = int(payload.get("additions", 0))
        is_low_val = payload.get("is_low_value", additions <= 5)

        return cls(
            record_id=record_id,
            project=str(payload.get("project", "")),
            contributor=subject,
            text=str(payload.get("text", "")),
            minhash=minhash,
            account_age_days=float(payload.get("account_age_days", 365.0)),
            additions=additions,
            timestamp=float(ts),
            outcome=str(payload.get("outcome", "open")),
            is_low_value=bool(is_low_val),
        )


@dataclasses.dataclass
class CampaignCluster:
    """A cluster of near-duplicate PRs submitted within a 48h temporal window."""

    cluster_id: str
    items: list[FingerprintItem]
    project_count: int
    account_count: int
    burst_density: float
    account_newness: float
    low_value_ratio: float
    merged_ratio: float
    cluster_score: float
    is_campaign: bool

    def accounts(self) -> set[str]:
        return {item.contributor for item in self.items}

    def projects(self) -> set[str]:
        return {item.project for item in self.items}


def cluster_near_duplicates(
    fingerprints: list[FingerprintItem],
    time_window_seconds: float = 48.0 * 3600.0,
    sim_threshold: float = 0.65,
) -> list[CampaignCluster]:
    """Clusters near-duplicate PRs within a 48-hour window using MinHash + LSH candidate pairing."""
    if not fingerprints:
        return []

    # 1. LSH Banding index
    buckets: dict[tuple[int, tuple[int, ...]], list[int]] = {}
    for idx, fp in enumerate(fingerprints):
        for band in range(LSH_NUM_BANDS):
            start = band * LSH_ROWS_PER_BAND
            end = start + LSH_ROWS_PER_BAND
            band_key = (band, tuple(fp.minhash[start:end]))
            buckets.setdefault(band_key, []).append(idx)

    # 2. Candidate pair discovery
    candidate_pairs: set[tuple[int, int]] = set()
    for bucket_indices in buckets.values():
        if len(bucket_indices) > 1:
            for i in range(len(bucket_indices)):
                for j in range(i + 1, len(bucket_indices)):
                    idx1 = bucket_indices[i]
                    idx2 = bucket_indices[j]
                    if idx1 > idx2:
                        idx1, idx2 = idx2, idx1
                    candidate_pairs.add((idx1, idx2))

    # 3. Adjacency graph construction: within 48h and similarity >= threshold
    adj: dict[int, set[int]] = {i: set() for i in range(len(fingerprints))}
    for idx1, idx2 in candidate_pairs:
        fp1 = fingerprints[idx1]
        fp2 = fingerprints[idx2]

        if abs(fp1.timestamp - fp2.timestamp) <= time_window_seconds:
            sim = minhash_similarity(fp1.minhash, fp2.minhash)
            if sim >= sim_threshold:
                adj[idx1].add(idx2)
                adj[idx2].add(idx1)

    # 4. Connected components
    visited: set[int] = set()
    raw_clusters: list[list[FingerprintItem]] = []
    for i in range(len(fingerprints)):
        if i in visited:
            continue
        comp_indices = []
        queue = [i]
        visited.add(i)
        while queue:
            curr = queue.pop(0)
            comp_indices.append(curr)
            for neighbor in adj[curr]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        # We consider clusters with >= 2 linked items, or all items
        if len(comp_indices) >= 2:
            raw_clusters.append([fingerprints[k] for k in comp_indices])

    # 5. Score clusters
    scored_clusters: list[CampaignCluster] = []
    for c_idx, items in enumerate(raw_clusters):
        scored = score_cluster(f"cluster_{c_idx+1}", items)
        scored_clusters.append(scored)

    return scored_clusters


def score_cluster(cluster_id: str, items: list[FingerprintItem]) -> CampaignCluster:
    """Scores a cluster on project breadth, account count, burst density, newness, and low-value diffs."""
    total_items = len(items)
    distinct_projects = {item.project for item in items if item.project}
    distinct_accounts = {item.contributor for item in items if item.contributor}

    timestamps = [item.timestamp for item in items]
    time_span_seconds = max(1800.0, max(timestamps) - min(timestamps))
    time_span_hours = time_span_seconds / 3600.0

    # Burst density: PRs per hour within the active burst
    burst_density = total_items / time_span_hours

    # Account newness: fraction of PRs from accounts younger than 30 days
    young_accounts = sum(1 for item in items if item.account_age_days < 30.0)
    account_newness = young_accounts / float(total_items)

    # Low-value diffs: fraction of PRs marked low-value or additions <= 5
    low_val_count = sum(1 for item in items if item.is_low_value or item.additions <= 5)
    low_value_ratio = low_val_count / float(total_items)

    # Merged discount: fraction of PRs successfully merged by maintainers
    merged_count = sum(1 for item in items if item.outcome == "merged")
    merged_ratio = merged_count / float(total_items)

    # Low-value requirement:
    # A legitimate documentation sprint by established people will have low_value_ratio < 0.40
    # or account_newness < 0.25 (trusted established contributors).
    has_low_value_signal = low_value_ratio >= 0.40

    if not has_low_value_signal or account_newness < 0.25:
        # Exempt: Legitimate documentation sprint or established contributors
        cluster_score = 0.0
        is_campaign = False
    else:
        breadth_score = min(1.0, len(distinct_projects) / 4.0)
        account_score = min(1.0, len(distinct_accounts) / 4.0)
        newness_score = account_newness
        diff_score = low_value_ratio

        base_suspicion = (
            breadth_score * 0.35 +
            account_score * 0.35 +
            newness_score * 0.15 +
            diff_score * 0.15
        )

        burst_factor = min(2.0, 1.0 + (burst_density / 5.0))
        # Merged PRs discount suspicion significantly (up to 80% discount)
        merged_discount = max(0.1, 1.0 - (merged_ratio * 0.8))

        cluster_score = min(1.0, base_suspicion * burst_factor * merged_discount)

        # Coordinated campaign criteria:
        # >= 3 distinct projects, >= 3 distinct accounts, low-value signal present, score >= 0.50
        is_campaign = (
            len(distinct_projects) >= 3 and
            len(distinct_accounts) >= 3 and
            cluster_score >= 0.50
        )

    return CampaignCluster(
        cluster_id=cluster_id,
        items=items,
        project_count=len(distinct_projects),
        account_count=len(distinct_accounts),
        burst_density=burst_density,
        account_newness=account_newness,
        low_value_ratio=low_value_ratio,
        merged_ratio=merged_ratio,
        cluster_score=cluster_score,
        is_campaign=is_campaign,
    )


def identify_campaign_members(
    clusters: list[CampaignCluster],
) -> tuple[set[str], dict[str, list[str]]]:
    """Identifies campaign member accounts and accounts eligible for auto-denounce with evidence.

    Rule 1: Treat an account as a campaign member only with >=3 PRs in >=3 projects.
    Rule 2: Auto-denounce with evidence at >=4 PRs in >=4 projects.
    """
    campaign_members: set[str] = set()
    auto_denounce_targets: dict[str, list[str]] = {}

    for cluster in clusters:
        if not cluster.is_campaign:
            continue

        # Group PRs in the campaign cluster by contributor
        prs_by_account: dict[str, list[FingerprintItem]] = {}
        for item in cluster.items:
            prs_by_account.setdefault(item.contributor, []).append(item)

        for account, items in prs_by_account.items():
            distinct_projects = {it.project for it in items if it.project}
            num_prs = len(items)
            num_projs = len(distinct_projects)

            # >= 3 PRs in >= 3 projects => Campaign Member
            if num_prs >= 3 and num_projs >= 3:
                campaign_members.add(account)

            # >= 4 PRs in >= 4 projects => Auto-denounce with evidence
            if num_prs >= 4 and num_projs >= 4:
                evidence_ids = [it.record_id for it in items]
                auto_denounce_targets[account] = evidence_ids

    return campaign_members, auto_denounce_targets

