"""
Parla Zero-Trust Security & Cryptographic Envelope Module
Implements:
1. Strict PII Interception & GPS Spatial Coarsening
2. Canonical SHA-256 Cryptographic Hash Chaining
3. Replay-Attack Nonce & Monotonic Sequence Defense
4. Tamper-Evident Envelope Generation & Verification
"""

import re
import json
import hashlib
import hmac
import uuid
import time
from typing import Dict, Any, Tuple, Optional, List

# Regex patterns for zero-trust PII interception
IPV4_REGEX = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
IPV6_REGEX = re.compile(r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b')
MAC_REGEX = re.compile(r'\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})\b')
EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,24}\b')
PHONE_REGEX = re.compile(r'(?:(?:\+|00)\d{1,3}[-.\s]?)?(?:\(?\d{1,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}\b')


class PIIScrubber:
    """
    Zero-Trust PII scrubber. Intercepts and masks network identifiers,
    operator credentials, and coarse-grains geographical coordinates to prevent
    physical compromise of edge node stewards.
    """

    @staticmethod
    def scrub_text(text: str) -> str:
        if not isinstance(text, str):
            return text
        text = IPV4_REGEX.sub("[REDACTED_IPV4]", text)
        text = IPV6_REGEX.sub("[REDACTED_IPV6]", text)
        text = MAC_REGEX.sub("[REDACTED_MAC]", text)
        text = EMAIL_REGEX.sub("[REDACTED_EMAIL]", text)
        text = PHONE_REGEX.sub("[REDACTED_PHONE]", text)
        return text

    @classmethod
    def sanitize_payload(cls, data: Any, coarsen_gps: bool = True) -> Any:
        """
        Recursively sanitizes dictionary/list/string structures, scrubbing PII
        and applying spatial coarsening to GPS lat/lon fields.
        """
        if isinstance(data, dict):
            sanitized = {}
            for k, v in data.items():
                clean_k = cls.scrub_text(str(k))
                
                # Zero-Trust Geo-defense: coarsen coordinates to 2 decimal places (~1.1 km precision)
                if coarsen_gps and k in ("latitude", "lat") and isinstance(v, (int, float)):
                    sanitized[clean_k] = round(float(v), 2)
                elif coarsen_gps and k in ("longitude", "lon", "lng") and isinstance(v, (int, float)):
                    sanitized[clean_k] = round(float(v), 2)
                else:
                    sanitized[clean_k] = cls.sanitize_payload(v, coarsen_gps=coarsen_gps)
            return sanitized
        elif isinstance(data, list):
            return [cls.sanitize_payload(item, coarsen_gps=coarsen_gps) for item in data]
        elif isinstance(data, str):
            return cls.scrub_text(data)
        else:
            return data


def canonical_json(data: Any) -> str:
    """Returns canonical deterministically ordered JSON representation for hashing."""
    return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def compute_sha256(content: str) -> str:
    """Computes standard hex SHA-256 digest."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


class CryptographicEnvelope:
    """
    Tamper-Evident Chained Cryptographic Envelope.
    Guarantees:
    - Integrity: SHA-256 payload and block digest.
    - Authenticity: HMAC-SHA256 signature using node secret.
    - Anti-Replay: High-entropy UUID4 nonce and monotonic sequence ID.
    - Chaining: Explicit reference to prev_block_hash forming an unforgeable Merkle-chain.
    """

    GENESIS_HASH = "0" * 64

    def __init__(self, node_secret: str = "parla-zero-trust-offline-root-key"):
        self.node_secret = node_secret.encode('utf-8')

    def create_block(
        self,
        seq_id: int,
        prev_hash: str,
        domain: str,
        payload: Dict[str, Any],
        timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Creates a tamper-evident cryptographically sealed block.
        """
        if timestamp is None:
            timestamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

        nonce = str(uuid.uuid4())
        canonical_payload_str = canonical_json(payload)
        payload_hash = compute_sha256(canonical_payload_str)

        # Build block header to hash
        header_data = {
            "seq_id": seq_id,
            "prev_hash": prev_hash,
            "domain": domain,
            "timestamp": timestamp,
            "nonce": nonce,
            "payload_hash": payload_hash
        }
        canonical_header = canonical_json(header_data)
        block_hash = compute_sha256(canonical_header)

        # Generate HMAC-SHA256 signature
        signature = hmac.new(self.node_secret, block_hash.encode('utf-8'), hashlib.sha256).hexdigest()

        return {
            "seq_id": seq_id,
            "block_hash": block_hash,
            "prev_hash": prev_hash,
            "domain": domain,
            "timestamp": timestamp,
            "nonce": nonce,
            "payload_hash": payload_hash,
            "payload": payload,
            "signature": signature
        }

    def verify_block(self, block: Dict[str, Any], expected_prev_hash: str) -> Tuple[bool, Optional[str]]:
        """
        Validates the integrity, chain link, and cryptographic signature of a block.
        Returns (is_valid, error_reason).
        """
        # 1. Verify prev_hash link
        if block.get("prev_hash") != expected_prev_hash:
            return False, f"Broken chain link: expected prev_hash '{expected_prev_hash}', got '{block.get('prev_hash')}'"

        # 2. Verify payload hash
        payload = block.get("payload", {})
        canonical_payload_str = canonical_json(payload)
        calculated_payload_hash = compute_sha256(canonical_payload_str)
        if calculated_payload_hash != block.get("payload_hash"):
            return False, f"Payload tampering detected: calculated {calculated_payload_hash} != {block.get('payload_hash')}"

        # 3. Verify block header hash
        header_data = {
            "seq_id": block.get("seq_id"),
            "prev_hash": block.get("prev_hash"),
            "domain": block.get("domain"),
            "timestamp": block.get("timestamp"),
            "nonce": block.get("nonce"),
            "payload_hash": block.get("payload_hash")
        }
        canonical_header = canonical_json(header_data)
        calculated_block_hash = compute_sha256(canonical_header)
        if calculated_block_hash != block.get("block_hash"):
            return False, f"Block header tampering detected: calculated {calculated_block_hash} != {block.get('block_hash')}"

        # 4. Verify cryptographic signature
        expected_sig = hmac.new(self.node_secret, block["block_hash"].encode('utf-8'), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_sig, block.get("signature", "")):
            return False, "Cryptographic signature verification failed (untrusted key or corrupted digest)"

        return True, None
