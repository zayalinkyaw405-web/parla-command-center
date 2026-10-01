"""
inject_osint_events.py
Injects 10 signed, PII-redacted OSINT events into the ledger.
"""

import sqlite3
import json
import hmac
import hashlib
from datetime import datetime, timedelta
import random

DB_PATH = "c:/Users/james/VuZiNat/iot_agent/Data/parla_ledger.db"
SECRET_KEY = b"parla_osint_nlp_offline_key_2026"

# Mock OSINT events with varying regions and threats
MOCK_EVENTS = [
    {"event_type": "AIRSTRIKE", "region_hash": "8f7e6d5c4b3a2918", "timeframe": "2026-09-28", "confidence": 0.85},
    {"event_type": "AIRSTRIKE", "region_hash": "8f7e6d5c4b3a2918", "timeframe": "2026-09-29", "confidence": 0.90},
    {"event_type": "GROUND_CONFLICT", "region_hash": "3a4b5c6d7e8f9012", "timeframe": "2026-09-27", "confidence": 0.75},
    {"event_type": "DISPLACEMENT", "region_hash": "1b2c3d4e5f6a7b8c", "timeframe": "2026-09-26", "confidence": 0.60},
    {"event_type": "AIRSTRIKE", "region_hash": "9f8e7d6c5b4a3928", "timeframe": "2026-09-25", "confidence": 0.80},
    {"event_type": "HUMANITARIAN_CRISIS", "region_hash": "2c3d4e5f6a7b8c9d", "timeframe": "2026-09-24", "confidence": 0.70},
    {"event_type": "GROUND_CONFLICT", "region_hash": "8f7e6d5c4b3a2918", "timeframe": "2026-09-23", "confidence": 0.65},
    {"event_type": "AIRSTRIKE", "region_hash": "4d5e6f7a8b9c0d1e", "timeframe": "2026-09-22", "confidence": 0.88},
    {"event_type": "DISPLACEMENT", "region_hash": "3a4b5c6d7e8f9012", "timeframe": "2026-09-21", "confidence": 0.55},
    {"event_type": "HUMANITARIAN_CRISIS", "region_hash": "9f8e7d6c5b4a3928", "timeframe": "2026-09-20", "confidence": 0.72},
]

def inject_events():
    print("=" * 60)
    print("📥 INJECTING OSINT EVENTS INTO LEDGER")
    print("=" * 60)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get current tip hash
    cursor.execute("SELECT block_hash FROM ledger_blocks ORDER BY seq_id DESC LIMIT 1")
    last_block = cursor.fetchone()
    prev_hash = last_block[0] if last_block else "GENESIS"
    
    print(f"\n[1] Current ledger tip: {prev_hash[:32]}...")
    print(f"[2] Injecting {len(MOCK_EVENTS)} OSINT events...\n")
    
    for i, event in enumerate(MOCK_EVENTS, 1):
        # Create payload
        payload = {
            "status": "PROCESSED",
            "event": event,
            "source_text_hash": hashlib.sha256(f"mock_osint_{i}".encode()).hexdigest()
        }
        
        payload_json = json.dumps(payload, sort_keys=True)
        payload_hash = hashlib.sha256(payload_json.encode()).hexdigest()
        
        # Generate signature
        signature = hmac.new(SECRET_KEY, payload_json.encode(), hashlib.sha256).hexdigest()
        
        # Generate block hash
        timestamp = datetime.now().isoformat()
        nonce = hashlib.sha256(f"{prev_hash}{timestamp}{i}".encode()).hexdigest()[:16]
        block_data = f"{prev_hash}{payload_hash}{timestamp}{nonce}"
        block_hash = hashlib.sha256(block_data.encode()).hexdigest()
        
        # Insert into ledger
        cursor.execute("""
            INSERT INTO ledger_blocks 
            (block_hash, prev_hash, domain, timestamp, nonce, payload_hash, payload_json, signature, sync_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            block_hash,
            prev_hash,
            "osint_nlp",
            timestamp,
            nonce,
            payload_hash,
            payload_json,
            signature,
            "SYNCED"
        ))
        
        prev_hash = block_hash
        print(f"  ✓ Block {i}: {event['event_type']} → Region {event['region_hash'][:8]}... (Risk: {event['confidence']:.2f})")
    
    conn.commit()
    conn.close()
    
    print(f"\n{'=' * 60}")
    print(f"✓ SUCCESS: {len(MOCK_EVENTS)} OSINT events injected")
    print(f"✓ New ledger tip: {prev_hash[:32]}...")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    inject_events()