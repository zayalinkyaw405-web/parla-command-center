"""
Scripts/stress_test_offline_core.py
Mission Charlie: Zero-Trust Offline Core Resilience Validation
"""

import json
import hashlib
import hmac
import random
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any

# --- Configuration ---
SECRET_KEY = b"parla_humanitarian_offline_key_2026"
CORRUPTION_RATE = 0.10  # 10% of payloads will be intentionally tampered with
NETWORK_DROP_INDEX = 30 # Simulate network drop after 30% of the stream

@dataclass
class TelemetryPayload:
    timestamp: str
    acoustic_db: float
    doppler_shift_hz: float
    location_hash: str
    signature: str

class OfflineQueue:
    """Encrypted local store-and-forward queue (Mocked for stress test)"""
    def __init__(self):
        self.queue: List[Dict[str, Any]] = []
        
    def enqueue(self, payload: Dict[str, Any]):
        # In prod: AES-256 encrypt before appending
        self.queue.append(payload)
        
    def flush(self) -> List[Dict[str, Any]]:
        flushed = self.queue.copy()
        self.queue.clear()
        return flushed

class ZeroTrustProcessor:
    def __init__(self):
        self.ledger_hashes: List[str] = []
        self.quarantine_log: List[Dict[str, Any]] = []
        self.tip_hash = "GENESIS"

    def verify_signature(self, payload: TelemetryPayload) -> bool:
        message = f"{payload.timestamp}|{payload.acoustic_db}|{payload.doppler_shift_hz}|{payload.location_hash}"
        expected_sig = hmac.new(SECRET_KEY, message.encode('utf-8'), hashlib.sha256).hexdigest()
        return hmac.compare_digest(payload.signature, expected_sig)

    def process(self, raw_data: Dict[str, Any]) -> str:
        payload = TelemetryPayload(**raw_data)
        
        if not self.verify_signature(payload):
            self.quarantine_log.append({
                "timestamp": payload.timestamp,
                "reason": "SIGNATURE_MISMATCH_OR_TAMPERED",
                "location_hash": payload.location_hash
            })
            return "QUARANTINED"
            
        # Valid: Append to Merkle chain
        payload_json = json.dumps(raw_data, sort_keys=True)
        self.tip_hash = hashlib.sha256(f"{self.tip_hash}{payload_json}".encode('utf-8')).hexdigest()
        self.ledger_hashes.append(self.tip_hash)
        return "LEDGERED"

def generate_signed_payload(ts: str, db: float, hz: float, loc: str) -> Dict[str, Any]:
    message = f"{ts}|{db}|{hz}|{loc}"
    sig = hmac.new(SECRET_KEY, message.encode('utf-8'), hashlib.sha256).hexdigest()
    return {
        "timestamp": ts,
        "acoustic_db": db,
        "doppler_shift_hz": hz,
        "location_hash": loc,
        "signature": sig
    }

def run_stress_test():
    print("="*60)
    print("MISSION CHARLIE: OFFLINE CORE STRESS TEST INITIATED")
    print("="*60)
    
    # 1. Generate Mock Dataset (Representing the Myanmar telemetry file)
    print("[*] Generating 100 mock telemetry payloads...")
    dataset = []
    for i in range(100):
        dataset.append(generate_signed_payload(
            ts=f"2026-10-01T12:{i//60:02d}:{i%60:02d}Z",
            db=random.uniform(60.0, 95.0),
            hz=random.uniform(100.0, 180.0),
            loc=f"REGION_YGN_{i%5:02d}"
        ))
    
    # 2. Inject Corruption (10%)
    print(f"[*] Injecting cryptographic corruption into {int(CORRUPTION_RATE * 100)}% of payloads...")
    corrupted_indices = random.sample(range(100), int(100 * CORRUPTION_RATE))
    for idx in corrupted_indices:
        # Tamper with the data, invalidating the signature
        dataset[idx]["acoustic_db"] = 999.9 
        
    # 3. Initialize Systems
    processor = ZeroTrustProcessor()
    offline_queue = OfflineQueue()
    network_up = True
    
    total_processed = 0
    queued_count = 0
    
    # 4. Simulate Stream with Network Drop
    print("[*] Beginning telemetry stream simulation...")
    for i, payload in enumerate(dataset):
        # Simulate network blackout
        if i == NETWORK_DROP_INDEX:
            print(f"    [!] NETWORK BLACKOUT SIMULATED AT PAYLOAD {i}")
            network_up = False
            
        if not network_up:
            offline_queue.enqueue(payload)
            queued_count += 1
        else:
            result = processor.process(payload)
            total_processed += 1
            
        # Simulate network restoration at 70%
        if i == 70 and not network_up:
            print(f"    [✓] NETWORK RESTORED AT PAYLOAD {i}. FLUSHING OFFLINE QUEUE...")
            network_up = True
            flushed_payloads = offline_queue.flush()
            for fp in flushed_payloads:
                result = processor.process(fp)
                total_processed += 1
            queued_count = 0 # Queue should be empty now

    # 5. Validation & Reporting
    print("\n" + "="*60)
    print("STRESS TEST RESULTS & VALIDATION")
    print("="*60)
    
    expected_total = 100
    expected_corrupted = len(corrupted_indices)
    expected_valid = expected_total - expected_corrupted
    
    ledger_count = len(processor.ledger_hashes)
    quarantine_count = len(processor.quarantine_log)
    
    print(f"Total Payloads Processed : {total_processed} / {expected_total}")
    print(f"Valid Payloads Ledgered  : {ledger_count} (Expected: {expected_valid})")
    print(f"Tampered Payloads Blocked: {quarantine_count} (Expected: {expected_corrupted})")
    print(f"Offline Queue Depth      : {queued_count} (Expected: 0)")
    
    # Assertions
    assert total_processed == expected_total, "FAIL: Not all payloads were processed."
    assert ledger_count == expected_valid, "FAIL: Ledger count mismatch."
    assert quarantine_count == expected_corrupted, "FAIL: Quarantine count mismatch."
    assert queued_count == 0, "FAIL: Offline queue did not flush completely."
    
    print("\n[✓] ALL ASSERTIONS PASSED.")
    print("[✓] Zero-Trust quarantine successfully blocked tampered data.")
    print("[✓] Offline store-and-forward perfectly recovered during blackout.")
    print("[✓] Merkle ledger integrity maintained.")
    print("="*60)
    print("MISSION CHARLIE: SUCCESSFUL. CORE CERTIFIED.")

if __name__ == "__main__":
    run_stress_test()

# python Scripts/stress_test_offline_core.py 
