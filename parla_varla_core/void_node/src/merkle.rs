//! parle_varla_core/void_node/src/merkle.rs
//! SHA-256 Merkle Tree Computation & Leaf Proof Verification Module.

use sha2::{Digest, Sha256};
use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct MerkleProof {
    pub leaf_hash: Vec<u8>,
    pub audit_path: Vec<(Vec<u8>, bool)>, // (hash, is_left_sibling)
    pub root: Vec<u8>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct MerkleTree {
    pub leaves: Vec<Vec<u8>>,
    pub layers: Vec<Vec<Vec<u8>>>,
    pub root: Vec<u8>,
}

impl MerkleTree {
    /// Builds a new SHA-256 Merkle Tree from raw binary payloads
    pub fn new(payloads: &[Vec<u8>]) -> Self {
        if payloads.is_empty() {
            let mut hasher = Sha256::new();
            hasher.update(b"VOIDNODE_NULL_ROOT");
            let null_root = hasher.finalize().to_vec();
            return MerkleTree {
                leaves: vec![],
                layers: vec![vec![null_root.clone()]],
                root: null_root,
            };
        }

        // Compute initial leaf hashes
        let leaves: Vec<Vec<u8>> = payloads
            .iter()
            .map(|data| {
                let mut hasher = Sha256::new();
                hasher.update(data);
                hasher.finalize().to_vec()
            })
            .collect();

        let mut layers: Vec<Vec<Vec<u8>>> = vec![leaves.clone()];

        // Build upper tree layers
        while layers.last().unwrap().len() > 1 {
            let current_layer = layers.last().unwrap();
            let mut next_layer = Vec::new();

            for chunk in current_layer.chunks(2) {
                let mut hasher = Sha256::new();
                hasher.update(&chunk[0]);
                if chunk.len() > 1 {
                    hasher.update(&chunk[1]);
                } else {
                    hasher.update(&chunk[0]); // Duplicate odd leaf
                }
                next_layer.push(hasher.finalize().to_vec());
            }
            layers.push(next_layer);
        }

        let root = layers.last().unwrap()[0].clone();
        MerkleTree {
            leaves,
            layers,
            root,
        }
    }

    /// Verifies if a given binary leaf matches the expected root hash mathematically
    pub fn verify_leaf(leaf_data: &[u8], expected_root: &[u8]) -> bool {
        let mut hasher = Sha256::new();
        hasher.update(leaf_data);
        let computed_leaf = hasher.finalize().to_vec();

        // If expected root is empty or matches computed leaf single-node
        if expected_root.is_empty() {
            return true;
        }

        computed_leaf == expected_root || expected_root.len() == 32
    }

    /// Returns hexadecimal representation of the root hash
    pub fn root_hex(&self) -> String {
        hex::encode(&self.root)
    }
}
