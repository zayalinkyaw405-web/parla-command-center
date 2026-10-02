"""
Scripts/ingest_eao_2023_2025.py
Ingests and cryptographically seals analyzed Myanmar EAO multi-theater conflict telemetry (2023-2025)
into Parla's Offline Merkle Ledger with zero-trust PII sanitization.
"""

import sys
import json
from pathlib import Path

# Ensure UTF-8 output encoding on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from parla.core.ledger import OfflineLedger
from parla.core.security import PIIScrubber, compute_sha256
from parla.core.knowledge_base import ParlaKnowledgeBase

DATA_FILE = PROJECT_ROOT / "Data" / "eao_conflict_telemetry_2023_2025.json"
DB_PATH = PROJECT_ROOT / "Data" / "parla_ledger.db"


def ingest_eao_telemetry():
    print("=" * 80)
    print("🛡️ PARLA OFFLINE LEDGER: 2023-2025 MYANMAR EAO TELEMETRY INGESTION")
    print("=" * 80)

    if not DATA_FILE.exists():
        print(f"❌ Error: Data file not found at {DATA_FILE}")
        sys.exit(1)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        corpus = json.load(f)

    ledger = OfflineLedger(db_path=str(DB_PATH))
    kb = ParlaKnowledgeBase()

    events = corpus.get("operations_events", [])
    print(f"\n[1] Loaded {len(events)} analyzed multi-theater operation events (2023-2025).")
    print(f"    Target Ledger: {DB_PATH}")
    print(f"    Current Chain Tip: {ledger.get_latest_block_hash()[:32]}...\n")

    successful_blocks = []

    for idx, evt in enumerate(events, 1):
        source_id = f"PARLA_RESEARCH_NODE_{evt['theater']}"
        
        # Enforce zero-trust domain payload
        payload = {
            "event_id": evt["event_id"],
            "operation": evt["operation"],
            "date": evt["date"],
            "theater": evt["theater"],
            "sector": evt["sector"],
            "event_type": evt["event_type"],
            "primary_actor": evt["primary_actor"],
            "opposing_force": evt["opposing_force"],
            "latitude": evt["latitude"],
            "longitude": evt["longitude"],
            "tactical_details": evt["tactical_details"],
            "weapons_telemetry": evt["weapons_telemetry"],
            "ingested_by": "Parla Autonomous Operations Research Node"
        }

        # Atomically record to Merkle ledger with PII sanitization and GPS coarsening
        success, msg, block = ledger.record_event(
            domain="eao_conflict_intel",
            payload=payload,
            source_id=source_id,
            coarsen_gps=True
        )

        if success and block:
            successful_blocks.append(block)
            print(f"  ✓ Block #{block['seq_id']:03d} | [{evt['operation']}] {evt['event_type']} -> Sector: {evt['sector']}")
            print(f"    Hash: {block['block_hash'][:28]}... | Prev: {block['prev_hash'][:20]}...")
        else:
            print(f"  ❌ Block Ingestion Failed for {evt['event_id']}: {msg}")

    print(f"\n[2] VERIFYING LEDGER CRYPTOGRAPHIC CHAIN INTEGRITY...")
    report = ledger.verify_chain_integrity()
    print(f"    Total Blocks in Ledger: {report['total_blocks']}")
    print(f"    Chain Valid: {report['is_valid']}")
    print(f"    Status: {report['message']}")
    print(f"    Tip Block Hash: {report['tip_block_hash'][:32]}...")

    print(f"\n[3] CROSS-REFERENCING WITH 10X EXPANDED KNOWLEDGE BASE...")
    macro = kb.get_eao_intel()
    print(f"    Operations in Knowledge Base: {macro['summary']['operations_tracked']}")
    print(f"    Factions in Knowledge Base: {macro['summary']['factions_tracked']}")
    print(f"    Theaters in Knowledge Base: {macro['summary']['theaters_tracked']}")

    print("\n" + "=" * 80)
    print(f"✓ COMPLETED: {len(successful_blocks)} 2023-2025 EAO operations cryptographically sealed.")
    print("=" * 80)


if __name__ == "__main__":
    ingest_eao_telemetry()
