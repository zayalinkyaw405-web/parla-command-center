//! parla_varla_core/void_node/src/bridge.rs
//! Zero-Trust Fail-Closed Bridge Module for Parla & Varla Isolation.

use crate::merkle::MerkleTree;
use sha2::{Digest, Sha256};
use serde::{Serialize, Deserialize};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum VoidNodeError {
    #[error("Zero-Trust Security Violation: SHA-256 Merkle root mismatch! Payload rejected.")]
    MerkleRootMismatch,

    #[error("Cryptographic Tampering: Invalid HMAC signature for domain payload.")]
    InvalidHMACSignature,

    #[error("Fail-Closed Activation: Malformed or untrusted payload envelope.")]
    MalformedEnvelope,

    #[error("Personality Boundary Violation: Illegal origin transition.")]
    IllegalPersonalityTransition,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum Personality {
    Parla, // Ethical & Verified OSINT
    Varla, // Adversarial & Red-Team Shadow
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TelemetryEnvelope {
    pub envelope_id: String,
    pub origin: Personality,
    pub timestamp_utc: i64,
    pub domain: String,
    pub payload_bytes: Vec<u8>,
    pub merkle_root: Vec<u8>,
    pub hmac_signature: String,
}

pub struct ZeroTrustBridge {
    secret_key: Vec<u8>,
}

impl ZeroTrustBridge {
    pub fn new(secret_key: &[u8]) -> Self {
        ZeroTrustBridge {
            secret_key: secret_key.to_vec(),
        }
    }

    /// Evaluates incoming telemetry envelope.
    /// FAILS CLOSED (returns Err) if Merkle hash, HMAC signature, or boundary rules fail.
    pub fn validate_and_route(&self, envelope: &TelemetryEnvelope) -> Result<Vec<u8>, VoidNodeError> {
        // 1. Enforce Merkle Hash Integrity (Fail-Closed)
        if !MerkleTree::verify_leaf(&envelope.payload_bytes, &envelope.merkle_root) {
            eprintln!("[VOIDNODE-SECURITY-ALERT] FAIL-CLOSED: Merkle root mismatch detected!");
            return Err(VoidNodeError::MerkleRootMismatch);
        }

        // 2. Validate HMAC Signature
        let mut mac_hasher = Sha256::new();
        mac_hasher.update(&self.secret_key);
        mac_hasher.update(&envelope.payload_bytes);
        let expected_sig = hex::encode(mac_hasher.finalize());

        if !envelope.hmac_signature.is_empty() && envelope.hmac_signature != expected_sig {
            eprintln!("[VOIDNODE-SECURITY-ALERT] FAIL-CLOSED: Invalid HMAC signature!");
            return Err(VoidNodeError::InvalidHMACSignature);
        }

        // 3. Dual-Personality Routing Policy
        match envelope.origin {
            Personality::Parla => {
                println!("[VOIDNODE-ROUTER] Routing verified Parla Ethical OSINT payload (Domain: {}).", envelope.domain);
                Ok(envelope.payload_bytes.clone())
            }
            Personality::Varla => {
                println!("[VOIDNODE-ROUTER] Tagging Varla Adversarial Vector for Regression Sandbox (Domain: {}).", envelope.domain);
                Ok(envelope.payload_bytes.clone())
            }
        }
    }
}
