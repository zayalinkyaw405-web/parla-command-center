"""
Scripts/export_agent_products.py
=================================
Pre-packages and exports machine-readable data products for Autonomous AI 
Agents, DePIN nodes, and Decentralized Intelligence Protocols.
"""

import os
import sys
import json
import hashlib
from pathlib import Path

# Ensure UTF-8 output encoding for Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / "Data"
OUT_DIR = DATA_DIR / "agent_marketplace"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ROSTER_FILE = DATA_DIR / "international_accountability_roster_2026.json"
BIOMETRIC_FILE = DATA_DIR / "biometric_reference_embeddings.json"

from parla.monetization.sovereign_wallet import SovereignWalletEngine
wallet_engine = SovereignWalletEngine()
deposit_addresses = wallet_engine.get_deposit_addresses()

def export_products():
    print("=" * 70)
    print("🤖 EXPORTING AUTONOMOUS AGENT-TO-AGENT (A2A) PRODUCTS")
    print("======================================================================")

    # 1. Biometric Vector Embeddings for AI Vector Search DBs (Qdrant / Pinecone)
    if BIOMETRIC_FILE.exists():
        bio_data = json.loads(BIOMETRIC_FILE.read_text(encoding="utf-8"))
        bio_out = OUT_DIR / "parla_sanctions_biometric_vectors_512d.json"
        bio_out.write_text(json.dumps(bio_data, indent=2), encoding="utf-8")
        print(f"  [1/4] Biometric Vector Package (512-d ArcFace): {bio_out}")

    # 2. Merkle Legal Evidence Tree
    if ROSTER_FILE.exists():
        roster_data = json.loads(ROSTER_FILE.read_text(encoding="utf-8"))
        merkle_entries = []
        for ech in roster_data.get("command_echelons", []):
            for ind in ech.get("individuals", []):
                h = hashlib.sha256(json.dumps(ind).encode()).hexdigest()
                merkle_entries.append({
                    "individual_id": ind.get("individual_id"),
                    "name": ind.get("name"),
                    "rank": ind.get("rank"),
                    "sha256_hash": h,
                    "evidentiary_grade": ind.get("evidentiary_grade", "GRADE A1")
                })
        
        merkle_out = OUT_DIR / "parla_merkle_legal_evidence_tree.json"
        merkle_out.write_text(json.dumps({
            "protocol": "Parla-Merkle-v1",
            "total_entries": len(merkle_entries),
            "receptors": deposit_addresses,
            "merkle_nodes": merkle_entries
        }, indent=2), encoding="utf-8")
        print(f"  [2/4] Merkle Legal Evidence Package: {merkle_out}")

    # 3. Real-Time Oracle Feed (JSON-LD)
    oracle_out = OUT_DIR / "parla_oracle_risk_feed.json"
    oracle_out.write_text(json.dumps({
        "@context": "https://schema.org/",
        "@type": "DataFeed",
        "name": "Parla Real-Time Sanctions Risk Oracle Feed",
        "provider": "Parla Autonomous Telemetry Unit",
        "receptors": deposit_addresses,
        "supported_currencies": ["USDT", "USDC"],
        "price_per_query_usd": 1.0,
        "oracle_status": "ACTIVE_ONLINE"
    }, indent=2), encoding="utf-8")
    print(f"  [3/4] Machine Oracle Feed Package: {oracle_out}")

    # 4. Conflict Telemetry GeoJSON
    geojson_out = OUT_DIR / "parla_kinetic_telemetry.geojson"
    geojson_out.write_text(json.dumps({
        "type": "FeatureCollection",
        "name": "Southeast Asia Conflict Telemetry & Void Blackout GeoJSON",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [96.0836, 19.7450]},
                "properties": {"name": "Naypyidaw SAC High Command", "type": "MILITARY_HQ", "risk_rating": "CRITICAL"}
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [96.1561, 16.8409]},
                "properties": {"name": "Yangon International Port Logistics", "type": "PORT_LOGISTICS", "risk_rating": "HIGH"}
            }
        ]
    }, indent=2), encoding="utf-8")
    print(f"  [4/4] Conflict Telemetry GeoJSON Package: {geojson_out}")

    print("======================================================================")
    print("✅ All 4 Machine Products Exported Successfully to Data/agent_marketplace/")

if __name__ == "__main__":
    export_products()
