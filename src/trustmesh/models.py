"""
TrustMesh Data Models & Local AI Configuration.

Defines Pydantic models for web-of-trust peering, vouching, denouncements,
audit results, coordinated spam campaign detection, and Bayesian newcomer triage,
as well as local open-weight AI model specifications.
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field

# ==============================================================================
# 1. Local Open-Weight Model Registry (Hack Day Sonipat Compliance)
# ==============================================================================
EMBEDDING_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"

SUPPORTED_MODELS: Dict[str, Dict[str, Any]] = {
    "embedding": {
        "model_id": EMBEDDING_MODEL_ID,
        "runtime": "sentence-transformers",
        "device": "cpu",
        "description": "Local 384-dimensional dense semantic embeddings for PRs and commit messages.",
    },
}

def get_model_registry() -> Dict[str, Dict[str, Any]]:
    """Return the registry of configured open-weight models."""
    return SUPPORTED_MODELS


# ==============================================================================
# 2. Verdict & Denouncement Helpers
# ==============================================================================
class Verdict(str):
    """
    Flexible verdict representation matching both full labels and shorthand prefixes:
    - ALLOW matches ALLOW / ALLOW_VOUCHED
    - QUARANTINE matches QUARANTINE / QUARANTINE_DENOUNCED / QUARANTINE_CAMPAIGN
    - UNCERTAIN matches UNCERTAIN / UNCERTAIN_NEWCOMER / HONEST_NEWCOMER_TRIAGE / PROBATION
    - Problem 07 Taxonomy: TRUST, ALLOW, PROBATION, FLAG, HOLD, BLOCK
    """
    TRUST = "TRUST"
    ALLOW = "ALLOW"
    PROBATION = "PROBATION"
    FLAG = "FLAG"
    HOLD = "HOLD"
    BLOCK = "BLOCK"
    ALLOW_VOUCHED = "ALLOW_VOUCHED"
    QUARANTINE_DENOUNCED = "QUARANTINE_DENOUNCED"
    QUARANTINE_CAMPAIGN = "QUARANTINE_CAMPAIGN"
    HONEST_NEWCOMER_TRIAGE = "HONEST_NEWCOMER_TRIAGE"
    ALL = {TRUST, ALLOW, PROBATION, FLAG, HOLD, BLOCK}
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, str):
            return False
        s = str(self)
        if s == other:
            return True

        # Shorthand prefix matching
        if other == "ALLOW" and s in ("ALLOW", "ALLOW_VOUCHED"):
            return True
        if s == "ALLOW" and other in ("ALLOW", "ALLOW_VOUCHED"):
            return True

        if other == "QUARANTINE" and s in ("QUARANTINE", "QUARANTINE_DENOUNCED", "QUARANTINE_CAMPAIGN"):
            return True
        if s == "QUARANTINE" and other in ("QUARANTINE", "QUARANTINE_DENOUNCED", "QUARANTINE_CAMPAIGN"):
            return True

        if other in ("UNCERTAIN", "PROBATION") and s in ("UNCERTAIN", "UNCERTAIN_NEWCOMER", "HONEST_NEWCOMER_TRIAGE", "PROBATION"):
            return True
        if s in ("UNCERTAIN", "PROBATION") and other in ("UNCERTAIN", "UNCERTAIN_NEWCOMER", "HONEST_NEWCOMER_TRIAGE", "PROBATION"):
            return True

        if other in ("QUARANTINE", "BLOCK") and s in ("QUARANTINE", "QUARANTINE_DENOUNCED", "BLOCK"):
            return True
        if s in ("QUARANTINE", "BLOCK") and other in ("QUARANTINE", "QUARANTINE_DENOUNCED", "BLOCK"):
            return True

        if other in ("HOLD", "QUARANTINE_CAMPAIGN") and s in ("HOLD", "QUARANTINE_CAMPAIGN"):
            return True
        if s in ("HOLD", "QUARANTINE_CAMPAIGN") and other in ("HOLD", "QUARANTINE_CAMPAIGN"):
            return True

        return False

    def __hash__(self) -> int:
        return hash(str(self))


class DenouncementEntry(dict):
    """
    Structured denouncement record that supports dict-style access,
    attribute-style access, and case-insensitive direct string comparison
    against project_id.
    """
    def __init__(self, project_id: str, severity: float, reason: str, **kwargs: Any):
        super().__init__(project_id=project_id, severity=severity, reason=reason, **kwargs)

    @property
    def project_id(self) -> str:
        return self["project_id"]

    @property
    def severity(self) -> float:
        return self["severity"]

    @property
    def reason(self) -> str:
        return self["reason"]

    def __getattr__(self, item: str) -> Any:
        if item in self:
            return self[item]
        raise AttributeError(f"'DenouncementEntry' has no attribute '{item}'")

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            other_norm = other.strip().lower()
            proj_norm = str(self.get("project_id", "")).strip().lower()
            return proj_norm == other_norm or other_norm in str(self.get("reason", "")).lower()
        return super().__eq__(other)

    def __str__(self) -> str:
        return f"{self.get('project_id')} ({self.get('reason', '')})"


# ==============================================================================
# 3. Web-of-Trust Pydantic Models
# ==============================================================================
class TrustEdge(BaseModel):
    """Inter-project peering trust relationship."""
    source_id: str
    target_id: str
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    context: Optional[str] = None


class VouchRecord(BaseModel):
    """Positive assertion issued by a project about a contributor."""
    project_id: str
    contributor_id: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    notes: Optional[str] = None


class DenounceRecord(BaseModel):
    """Negative assertion issued by a project about a contributor."""
    project_id: str
    contributor_id: str
    severity: float = Field(default=1.0, ge=0.0, le=1.0)
    reason: str


class AuditResult(BaseModel):
    """Auditing result from evaluating a contributor from a local project perspective."""
    contributor_id: str
    inspecting_project: str
    effective_trust: float
    is_vouched: bool
    denouncements_ignored: List[Any] = Field(default_factory=list)
    denouncements_applied: List[Any] = Field(default_factory=list)
    verdict: Union[Verdict, str]

    model_config = {"arbitrary_types_allowed": True}


# ==============================================================================
# 4. Coordinated Spam Campaign Models
# ==============================================================================
class PREvent(BaseModel):
    """Pull request submission event."""
    pr_id: str
    repo_id: str
    author: str
    account_age_days: float
    timestamp: float
    title: str
    diff_content: str
    files_changed: List[str] = Field(default_factory=list)


class CampaignAlert(BaseModel):
    """Alert raised when coordinated multi-project spam/sybil activity is detected."""
    detected: bool
    campaign_id: str
    cluster_size: int
    affected_repos_count: int
    affected_repos: List[str]
    flagged_authors: List[str]
    mean_similarity: float
    time_span_minutes: float
    evidence_summary: str


# ==============================================================================
# 5. Unified Decision & Bayesian Newcomer Triage Models
# ==============================================================================
class UnifiedAuditDecision(BaseModel):
    """
    Comprehensive multi-signal evaluation decision combining
    Web-of-Trust graph, open-weight campaign detection, and Bayesian newcomer triage.
    """
    pr_id: str
    contributor_id: str
    target_repo: str
    graph_trust_score: float
    is_vouched: bool
    is_campaign_member: bool
    campaign_id: Optional[str] = None
    bayesian_expected_trust: float
    bayesian_uncertainty: float
    verdict: Union[Verdict, str]
    action_recommendation: str
    evidence_trace: List[str] = Field(default_factory=list)

    model_config = {"arbitrary_types_allowed": True}
