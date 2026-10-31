"""Cryptographically signed, content-addressed records for the trust network.

Implements Ed25519 signature verification, deterministic key generation from seeds,
content addressing with SHA-256, and per-issuer hash-chain integrity verification.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import time
from typing import Any, Optional

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519


class RecordError(Exception):
    """Base exception for record validation errors."""


class InvalidSignatureError(RecordError):
    """Raised when an Ed25519 signature is invalid."""


class ContentHashMismatchError(RecordError):
    """Raised when a record ID does not match the canonical content hash."""


class KeyImpersonationError(RecordError):
    """Raised when an issuer key differs from the pinned identity key."""


class HashChainError(RecordError):
    """Raised when a hash chain link is missing or broken."""


class RecordKind:
    """Standard record types within the trust network."""

    VOUCH = "vouch"
    DENOUNCE = "denounce"
    RETRACT = "retract"
    TRUST_PEER = "trust_peer"
    PR_FINGERPRINT = "pr_fingerprint"

    ALL = {VOUCH, DENOUNCE, RETRACT, TRUST_PEER, PR_FINGERPRINT}


@dataclasses.dataclass(frozen=True)
class Record:
    """An immutable, content-addressed, Ed25519-signed record."""

    issuer: str
    issuer_key: str
    kind: str
    subject: str
    ts: float
    payload: dict[str, Any]
    prev: Optional[str] = ""
    sig: str = ""

    @property
    def record_id(self) -> str:
        """Content-addressed identifier: SHA-256 over canonical content bytes."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

    def canonical_bytes(self) -> bytes:
        """Returns deterministic canonical UTF-8 bytes of the content (excluding signature)."""
        body = {
            "issuer": str(self.issuer),
            "issuer_key": str(self.issuer_key).lower(),
            "kind": str(self.kind),
            "payload": self.payload,
            "prev": str(self.prev or ""),
            "subject": str(self.subject),
            "ts": float(self.ts),
        }
        return json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def verify(self) -> bool:
        """Verifies record schema, Ed25519 public key, and cryptographic signature."""
        if self.kind not in RecordKind.ALL:
            raise RecordError(f"Unsupported record kind '{self.kind}'")

        if not self.issuer_key or len(self.issuer_key) != 64:
            raise RecordError(f"Invalid issuer public key length: {len(self.issuer_key)}")

        if not self.sig or len(self.sig) != 128:
            raise InvalidSignatureError("Signature must be a 128-character hex string (64 bytes)")

        try:
            pub_bytes = bytes.fromhex(self.issuer_key)
            sig_bytes = bytes.fromhex(self.sig)
        except ValueError as err:
            raise RecordError(f"Malformed hex encoding in key or signature: {err}") from err

        try:
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)
            public_key.verify(sig_bytes, self.canonical_bytes())
        except InvalidSignature as err:
            raise InvalidSignatureError(f"Signature verification failed for record {self.record_id}") from err

        return True

    def to_dict(self) -> dict[str, Any]:
        """Serializes the record to a standard dictionary."""
        return {
            "record_id": self.record_id,
            "issuer": self.issuer,
            "issuer_key": self.issuer_key,
            "kind": self.kind,
            "subject": self.subject,
            "ts": self.ts,
            "payload": self.payload,
            "prev": self.prev or "",
            "sig": self.sig,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Record:
        """Reconstructs a record from a dictionary."""
        rec = cls(
            issuer=str(data["issuer"]),
            issuer_key=str(data["issuer_key"]).lower(),
            kind=str(data["kind"]),
            subject=str(data["subject"]),
            ts=float(data["ts"]),
            payload=dict(data.get("payload", {})),
            prev=str(data.get("prev", "") or ""),
            sig=str(data.get("sig", "")),
        )
        if "record_id" in data and data["record_id"] != rec.record_id:
            raise ContentHashMismatchError(
                f"Supplied record_id {data['record_id']} does not match computed {rec.record_id}"
            )
        return rec


def generate_keypair(
    seed: Optional[str | bytes] = None,
) -> tuple[ed25519.Ed25519PrivateKey, str]:
    """Generates an Ed25519 private key and hex-encoded public key.

    If seed is supplied, key derivation is completely deterministic.
    """
    if seed is None:
        seed_bytes = os.urandom(32)
    elif isinstance(seed, str):
        seed_bytes = hashlib.sha256(seed.encode("utf-8")).digest()
    elif isinstance(seed, bytes):
        if len(seed) == 32:
            seed_bytes = seed
        else:
            seed_bytes = hashlib.sha256(seed).digest()
    else:
        raise TypeError("Seed must be str, bytes, or None")

    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(seed_bytes)
    pub_key = private_key.public_key()
    pub_hex = pub_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    ).hex()

    return private_key, pub_hex


def create_record(
    issuer: str,
    private_key: ed25519.Ed25519PrivateKey,
    kind: str,
    subject: str,
    payload: dict[str, Any],
    prev: Optional[str] = "",
    ts: Optional[float] = None,
) -> Record:
    """Constructs and signs a new Record."""
    if ts is None:
        ts = time.time()

    pub_hex = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    ).hex()

    unsigned_rec = Record(
        issuer=issuer,
        issuer_key=pub_hex,
        kind=kind,
        subject=subject,
        ts=ts,
        payload=payload,
        prev=prev or "",
        sig="",
    )

    sig_bytes = private_key.sign(unsigned_rec.canonical_bytes())
    signed_rec = Record(
        issuer=issuer,
        issuer_key=pub_hex,
        kind=kind,
        subject=subject,
        ts=ts,
        payload=payload,
        prev=prev or "",
        sig=sig_bytes.hex(),
    )
    return signed_rec


def verify_chain(records: list[Record]) -> bool:
    """Verifies that a sequence of records forms an unbroken cryptographic hash chain.

    Requirements:
    1. Every record has a valid signature.
    2. All records share the same issuer and issuer_key.
    3. Each record (after index 0) references the prior record's record_id via prev.
    4. Timestamps are non-decreasing.
    """
    if not records:
        return True

    expected_issuer = records[0].issuer
    expected_key = records[0].issuer_key

    for i, rec in enumerate(records):
        rec.verify()

        if rec.issuer != expected_issuer:
            raise HashChainError(
                f"Chain issuer mismatch at index {i}: expected '{expected_issuer}', got '{rec.issuer}'"
            )

        if rec.issuer_key != expected_key:
            raise KeyImpersonationError(
                f"Chain issuer key mismatch at index {i}: expected '{expected_key}', got '{rec.issuer_key}'"
            )

        if i > 0:
            prev_rec = records[i - 1]
            if rec.prev != prev_rec.record_id:
                raise HashChainError(
                    f"Hash-chain gap at index {i}: record prev '{rec.prev}' does not match prior record_id '{prev_rec.record_id}'"
                )
            if rec.ts < prev_rec.ts:
                raise HashChainError(
                    f"Non-monotonic timestamp at index {i}: {rec.ts} < {prev_rec.ts}"
                )

    return True

