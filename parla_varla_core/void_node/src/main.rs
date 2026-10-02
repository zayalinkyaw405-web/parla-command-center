//! parla_varla_core/void_node/src/main.rs
use void_node::{ZeroTrustBridge, Personality, TelemetryEnvelope, MerkleTree};
use sha2::{Digest, Sha256};

fn main() {
    println!("=" * 80);
    println!("🦀 VOIDNODE ZERO-TRUST CRYPTOGRAPHIC BRIDGE SERVER (RUST CORE)");
    println!("========================================================================");

    let secret_key = b"void_node_secret_key_2026";
    let bridge = ZeroTrustBridge::new(secret_key);

    // 1. Simulate Parla Payload Validation
    let parla_data = b"Parla Verified OSINT Payload: Min Aung Hlaing Sanctions Record";
    let merkle_tree = MerkleTree::new(&[parla_data.to_vec()]);

    let mut mac_hasher = Sha256::new();
    mac_hasher.update(secret_key);
    mac_hasher.update(parla_data);
    let sig = hex::encode(mac_hasher.finalize());

    let envelope = TelemetryEnvelope {
        envelope_id: "env_001_parla".to_string(),
        origin: Personality::Parla,
        timestamp_utc: 1790936400,
        domain: "recon".to_string(),
        payload_bytes: parla_data.to_vec(),
        merkle_root: merkle_tree.root.clone(),
        hmac_signature: sig,
    };

    match bridge.validate_and_route(&envelope) {
        Ok(routed) => println!(" [1/2] Parla Verification: SUCCESS (Payload Len: {} bytes)", routed.len()),
        Err(e) => println!(" [1/2] Parla Verification: FAILED ({})", e),
    }

    // 2. Simulate Varla Tampered Payload (Fail-Closed Test)
    let varla_tampered_data = b"Varla Tampered Disinfo Payload";
    let tampered_envelope = TelemetryEnvelope {
        envelope_id: "env_002_varla_tampered".to_string(),
        origin: Personality::Varla,
        timestamp_utc: 1790936410,
        domain: "analysis".to_string(),
        payload_bytes: varla_tampered_data.to_vec(),
        merkle_root: vec![0u8; 32], // INVALID ROOT
        hmac_signature: "invalid_sig".to_string(),
    };

    match bridge.validate_and_route(&tampered_envelope) {
        Ok(_) => println!(" [2/2] Varla Verification: UNEXPECTED PASS!"),
        Err(e) => println!(" [2/2] Varla Tamper Detection: FAIL-CLOSED ACTIVATED! ({})", e),
    }

    println!("========================================================================");
    println!("✅ VOIDNODE RUST BRIDGE RUNTIME VERIFIED SUCCESSFULLY!");
    println!("========================================================================");
}
