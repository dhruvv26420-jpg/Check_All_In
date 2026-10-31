"""
TrustMesh: Decentralized Cryptographic Trust Network for Open Source Contributions.
"""

from trustmesh.models import (
    TrustEdge,
    VouchRecord,
    DenounceRecord,
    AuditResult,
    Verdict,
    PREvent,
    CampaignAlert,
    UnifiedAuditDecision,
)
from trustmesh.graph import TrustNetwork
from trustmesh.campaign import (
    CampaignDetector,
    CampaignCluster,
    FingerprintItem,
    cluster_near_duplicates,
    compute_minhash,
    identify_campaign_members,
    minhash_similarity,
    normalize_pr_text,
)
from trustmesh.evaluator import TrustMeshEngine
from trustmesh.node import EvaluationResult, Node
from trustmesh.records import (
    ContentHashMismatchError,
    HashChainError,
    InvalidSignatureError,
    KeyImpersonationError,
    Record,
    RecordError,
    RecordKind,
    create_record,
    generate_keypair,
    verify_chain,
)

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "TrustNetwork",
    "CampaignDetector",
    "TrustMeshEngine",
    "TrustEdge",
    "VouchRecord",
    "DenounceRecord",
    "AuditResult",
    "Verdict",
    "PREvent",
    "CampaignAlert",
    "UnifiedAuditDecision",
    "Record",
    "RecordKind",
    "create_record",
    "verify_chain",
    "generate_keypair",
    "RecordError",
    "InvalidSignatureError",
    "ContentHashMismatchError",
    "KeyImpersonationError",
    "HashChainError",
    "Node",
    "EvaluationResult",
    "compute_minhash",
    "minhash_similarity",
    "normalize_pr_text",
    "cluster_near_duplicates",
    "identify_campaign_members",
    "CampaignCluster",
    "FingerprintItem",
]
