//! parla_varla_core/void_node/src/lib.rs
pub mod merkle;
pub mod bridge;

pub use merkle::MerkleTree;
pub use bridge::{ZeroTrustBridge, Personality, TelemetryEnvelope, VoidNodeError};
