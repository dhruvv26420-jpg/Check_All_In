"""Unit tests for records module: cryptographic signatures, content-addressing,

key pinning, and hash-chain verification.
"""

from __future__ import annotations

import time
import pytest

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


def test_deterministic_keys() -> None:
    """Verifies that identical seeds produce identical Ed25519 public keys."""
    _, pub1 = generate_keypair("seed_alpha")
    _, pub2 = generate_keypair("seed_alpha")
    _, pub3 = generate_keypair("seed_beta")

    assert pub1 == pub2
    assert pub1 != pub3
    assert len(pub1) == 64  # 32 bytes hex


def test_record_creation_and_verification() -> None:
    """Verifies that a signed record passes cryptographic verification."""
    priv, pub = generate_keypair("seed_test")
    rec = create_record(
        issuer="project-A",
        private_key=priv,
        kind=RecordKind.VOUCH,
        subject="contributor-1",
        payload={"score": 0.95},
        prev="",
        ts=1000.0,
    )

    assert rec.issuer == "project-A"
    assert rec.issuer_key == pub
    assert rec.kind == RecordKind.VOUCH
    assert rec.verify() is True
    assert len(rec.record_id) == 64


def test_tampered_payload_rejected() -> None:
    """Verifies that altering record payload breaks content hash and signature."""
    priv, pub = generate_keypair("seed_tamper")
    rec = create_record(
        issuer="project-A",
        private_key=priv,
        kind=RecordKind.VOUCH,
        subject="contributor-1",
        payload={"score": 0.50},
    )

    # Tamper with payload
    tampered_dict = rec.to_dict()
    tampered_dict["payload"]["score"] = 1.0

    # Deserializing with mismatched record_id raises ContentHashMismatchError
    with pytest.raises(ContentHashMismatchError):
        Record.from_dict(tampered_dict)

    # Directly creating Record with altered payload but original signature fails verify()
    tampered_rec = Record(
        issuer=rec.issuer,
        issuer_key=rec.issuer_key,
        kind=rec.kind,
        subject=rec.subject,
        ts=rec.ts,
        payload={"score": 1.0},
        prev=rec.prev,
        sig=rec.sig,
    )
    with pytest.raises(InvalidSignatureError):
        tampered_rec.verify()


def test_tampered_signature_rejected() -> None:
    """Verifies that corrupted signature bytes are rejected."""
    priv, pub = generate_keypair("seed_sig")
    rec = create_record(
        issuer="project-A",
        private_key=priv,
        kind=RecordKind.DENOUNCE,
        subject="bad-actor",
        payload={"reason": "spam"},
    )

    # Flip characters in signature
    bad_sig = ("00" if rec.sig[:2] != "00" else "ff") + rec.sig[2:]
    bad_rec = Record(
        issuer=rec.issuer,
        issuer_key=rec.issuer_key,
        kind=rec.kind,
        subject=rec.subject,
        ts=rec.ts,
        payload=rec.payload,
        prev=rec.prev,
        sig=bad_sig,
    )
    with pytest.raises(InvalidSignatureError):
        bad_rec.verify()


def test_hash_chain_gap_detected() -> None:
    """Verifies that missing or invalid prev hash links are detected by verify_chain."""
    priv, _ = generate_keypair("seed_chain")

    r1 = create_record("project-A", priv, RecordKind.VOUCH, "user-1", {}, prev="", ts=100.0)
    r2 = create_record("project-A", priv, RecordKind.VOUCH, "user-2", {}, prev=r1.record_id, ts=110.0)
    # r3 has broken prev pointer
    r3 = create_record("project-A", priv, RecordKind.VOUCH, "user-3", {}, prev="wrong_hash_gap", ts=120.0)

    assert verify_chain([r1, r2]) is True

    with pytest.raises(HashChainError, match="Hash-chain gap"):
        verify_chain([r1, r2, r3])


def test_hash_chain_monotonic_timestamp() -> None:
    """Verifies that records with backward timestamps in chain fail verification."""
    priv, _ = generate_keypair("seed_ts")

    r1 = create_record("project-A", priv, RecordKind.VOUCH, "user-1", {}, prev="", ts=200.0)
    # r2 has timestamp earlier than r1
    r2 = create_record("project-A", priv, RecordKind.VOUCH, "user-2", {}, prev=r1.record_id, ts=150.0)

    with pytest.raises(HashChainError, match="Non-monotonic timestamp"):
        verify_chain([r1, r2])


def test_chain_issuer_key_mismatch() -> None:
    """Verifies that an issuer attempting to change public key in chain raises KeyImpersonationError."""
    priv1, pub1 = generate_keypair("seed_one")
    priv2, pub2 = generate_keypair("seed_two")

    r1 = create_record("project-A", priv1, RecordKind.VOUCH, "user-1", {}, prev="", ts=100.0)
    # r2 forged by key2 claiming to be project-A
    r2 = create_record("project-A", priv2, RecordKind.VOUCH, "user-2", {}, prev=r1.record_id, ts=110.0)

    with pytest.raises(KeyImpersonationError):
        verify_chain([r1, r2])

