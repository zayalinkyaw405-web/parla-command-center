"""
stress_test.py
Full System Stress Test: 150+ Events Across Both Domains
Tests: OSINT NLP, Industrial Processor, Feedback Loop, Risk Mapper, Ledger Integrity
"""

import sys
import os
import time
import json
import random
import hashlib
import hmac
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

from parla.domains.osint_nlp import OSINTEventExtractor, generate_osint_signature
from parla.domains.industrial import IndustrialProcessor
from parla.core.feedback_loop import FeedbackLoop
from parla.domains.risk_mapper import RegionalRiskMapper
import numpy as np

DB_PATH = Path(__file__).parent / "Data" / "parla_ledger.db"

# FIX 1: Two separate keys for two domains
OSINT_SECRET_KEY = b"parla-zero-trust-offline-root-key"
INDUSTRIAL_SECRET_KEY = b"parla_industrial_offline_key_2026"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

print("=" * 80)
print("[PARLA] FULL SYSTEM STRESS TEST")
print("=" * 80)
print(f"Start Time: {datetime.now().isoformat()}")
print(f"Database: {DB_PATH}")

# Get initial ledger state
conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM ledger_blocks")
initial_blocks = cursor.fetchone()[0]
conn.close()
print(f"Initial Ledger State: {initial_blocks} blocks")

# ============================================================
# TEST 1: OSINT NLP Stress Test (100 events)
# ============================================================
print("\n" + "=" * 80)
print("[TEST 1] OSINT NLP STRESS TEST: 100 Events")
print("=" * 80)

extractor = OSINTEventExtractor()
osint_success = 0
osint_fail = 0
osint_quarantined = 0

# Generate 100 diverse OSINT events with realistic PII
osint_templates = [
    ("Multiple airstrikes reported in {region} with civilian casualties. Contact: {name} at {phone}", "Sagaing"),
    ("Jet fighter bombed {region} hospital. Eyewitness: {name}, email {email}", "Rakhine"),
    ("Air strike on {region} market. {name} ({phone}) confirmed 12 dead", "Shan"),
    ("Su-30 dropped cluster munitions on {region}. {name} reports {phone} injured", "Kachin"),
    ("Clashes in {region} between junta soldiers and PDF. {name} ({email}) reports heavy fighting", "Magway"),
    ("Firefight in {region}. {name} says {phone} civilians trapped", "Mandalay"),
    ("Ground offensive in {region}. {name} at {phone} confirms displacement", "Kayah"),
    ("{name} reports 500 IDPs fled {region}. Contact: {email}", "Kayin"),
    ("Refugees from {region} crossing border. {name} ({phone}) coordinating aid", "Chin"),
    ("Medical shortage in {region}. {name} ({email}) appeals for supplies", "Sagaing"),
    ("Aid blocked in {region}. {name} at {phone} says civilians starving", "Rakhine"),
    ("School bombed in {region}. {name} ({phone}) reports 20 students injured", "Shan"),
    ("Power grid hit in {region}. {name} ({email}) confirms blackout", "Mandalay"),
]

regions = ["Sagaing", "Rakhine", "Shan", "Kachin", "Chin", "Kayah", "Kayin", "Magway", "Mandalay", "Yangon"]
names = ["Dr. Aung", "Ko Myo", "Ma Thida", "U Hla", "Daw Tin", "Ko Zaw", "Ma Nwe", "U Kyaw"]

start_time = time.time()

for i in range(100):
    template, default_region = random.choice(osint_templates)
    region = random.choice(regions)
    name = random.choice(names)
    phone = f"+95-{random.randint(9, 99)}-{random.randint(100000, 999999)}"
    email = f"{name.lower().replace(' ', '.').replace('dr.', '').replace('ko ', '').replace('ma ', '').replace('u ', '').replace('daw ', '')}@test.org"
    
    text = template.format(region=region, name=name, phone=phone, email=email)
    
    # FIX 2: Use OSINT_SECRET_KEY explicitly
    signature = generate_osint_signature(text, secret_key=OSINT_SECRET_KEY)
    
    result = extractor.process_osint_payload(
        raw_text=text,
        signature=signature,
        source_id=f"STRESS_TEST_{i:03d}"
    )
    
    if result['status'] == 'SEALED':
        osint_success += 1
    elif result['status'] == 'DROPPED_AND_QUARANTINED':
        osint_quarantined += 1
    else:
        osint_fail += 1

osint_duration = time.time() - start_time
osint_rate = 100 / osint_duration if osint_duration > 0 else 0

print(f"\n✓ OSINT Events Processed: 100")
print(f"  ├─ Sealed: {osint_success}")
print(f"  ├─ Quarantined: {osint_quarantined}")
print(f"  ├─ Failed: {osint_fail}")
print(f"  └─ Rate: {osint_rate:.1f} events/sec")

# ============================================================
# TEST 2: Industrial Processor Stress Test (50 events)
# ============================================================
print("\n" + "=" * 80)
print("[TEST 2] INDUSTRIAL PROCESSOR STRESS TEST: 50 Events")
print("=" * 80)

industrial = IndustrialProcessor()
ind_success = 0
ind_fail = 0

start_time = time.time()

for i in range(50):
    machine_id = f"PUMP-{random.randint(1, 10):03d}"
    
    # Generate vibration data (mix of normal and anomalous)
    if i < 35:
        # Normal operation
        vibration = np.random.normal(0, 0.5, 1000)
        temperature = 45.0 + random.uniform(-5, 5)
    else:
        # Anomalous (bearing degradation)
        t = np.linspace(0, 1, 1000)
        vibration = (
            np.random.normal(0, 0.5, 1000) +
            2.0 * np.sin(2 * np.pi * 50 * t) +
            1.5 * np.sin(2 * np.pi * 10 * t)
        )
        temperature = 68.0 + random.uniform(-3, 3)
    
    # Generate signature
    payload = {
        "machine_id": machine_id,
        "vibration_data": vibration.tolist(),
        "temperature": temperature
    }
    payload_json = json.dumps(payload, sort_keys=True)
    
    # FIX 3: Use INDUSTRIAL_SECRET_KEY explicitly
    signature = hmac.new(INDUSTRIAL_SECRET_KEY, payload_json.encode(), hashlib.sha256).hexdigest()
    
    result = industrial.process_telemetry(
        machine_id=machine_id,
        vibration_data=vibration,
        temperature=temperature,
        signature=signature
    )
    
    if result['status'] == 'PROCESSED':
        ind_success += 1
    else:
        ind_fail += 1

ind_duration = time.time() - start_time
ind_rate = 50 / ind_duration if ind_duration > 0 else 0

print(f"\n✓ Industrial Events Processed: 50")
print(f"  ├─ Processed: {ind_success}")
print(f"  ├─ Failed: {ind_fail}")
print(f"  └─ Rate: {ind_rate:.1f} events/sec")

# ============================================================
# TEST 3: Feedback Loop Stress Test (20 feedback entries)
# ============================================================
print("\n" + "=" * 80)
print("[TEST 3] FEEDBACK LOOP STRESS TEST: 20 Feedback Entries")
print("=" * 80)

feedback = FeedbackLoop()
fb_success = 0

start_time = time.time()

event_types = ["AIRSTRIKE", "GROUND_CONFLICT", "UAV_DRONE", "DISPLACEMENT"]
for i in range(20):
    alert_id = f"STRESS-ALERT-{i:03d}"
    event_type = random.choice(event_types)
    confidence = random.uniform(0.6, 0.95)
    action = random.choice(["CONFIRM", "REJECT"])
    reason = "Stress test feedback"
    
    result = feedback.record_feedback(
        alert_id=alert_id,
        event_type=event_type,
        original_confidence=confidence,
        operator_action=action,
        operator_reason=reason
    )
    
    if result['status'] == 'SUCCESS':
        fb_success += 1

fb_duration = time.time() - start_time

print(f"\n✓ Feedback Entries Recorded: 20")
print(f"  ├─ Success: {fb_success}")
print(f"  └─ Rate: {20 / fb_duration:.1f} entries/sec")

# Check calibrated thresholds
thresholds = feedback.get_current_thresholds()
print(f"\n✓ Dynamic Thresholds Calibrated: {len(thresholds)} event types")
for evt, thresh in list(thresholds.items())[:5]:
    print(f"  └─ {evt}: >= {thresh}")

# ============================================================
# TEST 4: Risk Mapper Validation
# ============================================================
print("\n" + "=" * 80)
print("[TEST 4] RISK MAPPER VALIDATION")
print("=" * 80)

mapper = RegionalRiskMapper()
start_time = time.time()
report = mapper.calculate_regional_risk(days=90)
mapper_duration = time.time() - start_time

print(f"\n✓ Risk Report Generated in {mapper_duration:.3f} seconds")
print(f"  ├─ Regions Monitored: {report['total_regions_monitored']}")
print(f"  ├─ Analysis Window: {report['analysis_window_days']} days")
if report['regions']:
    top_region = report['regions'][0]
    print(f"  └─ Highest Risk Region: {top_region['region_hash']}")
    print(f"     ├─ Risk Score: {top_region['risk_score']}")
    print(f"     ├─ Total Events: {top_region['total_events']}")
    print(f"     └─ Primary Threat: {max(top_region['event_breakdown'], key=top_region['event_breakdown'].get)}")

# ============================================================
# TEST 5: Ledger Integrity Validation
# ============================================================
print("\n" + "=" * 80)
print("[TEST 5] LEDGER INTEGRITY VALIDATION")
print("=" * 80)

conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM ledger_blocks")
final_blocks = cursor.fetchone()[0]

cursor.execute("SELECT domain, COUNT(*) FROM ledger_blocks GROUP BY domain")
domain_counts = cursor.fetchall()

cursor.execute("SELECT seq_id, block_hash, prev_hash FROM ledger_blocks ORDER BY seq_id")
blocks = cursor.fetchall()

# Validate chain integrity
chain_valid = True
for i in range(1, len(blocks)):
    prev_hash = blocks[i][2]
    expected_prev = blocks[i-1][1]
    if prev_hash != expected_prev:
        chain_valid = False
        break

conn.close()

blocks_added = final_blocks - initial_blocks

print(f"\n✓ Ledger Integrity Check")
print(f"  ├─ Initial Blocks: {initial_blocks}")
print(f"  ├─ Final Blocks: {final_blocks}")
print(f"  ├─ Blocks Added: {blocks_added}")
print(f"  ├─ Chain Valid: {'✓ YES' if chain_valid else '✗ NO'}")
print(f"  └─ Domain Distribution:")
for domain, count in domain_counts:
    print(f"     ├─ {domain}: {count} blocks")

# ============================================================
# FINAL REPORT
# ============================================================
print("\n" + "=" * 80)
print("📊 STRESS TEST FINAL REPORT")
print("=" * 80)

total_events = 100 + 50 + 20
total_success = osint_success + ind_success + fb_success
total_fail = osint_fail + ind_fail + (20 - fb_success)

print(f"\n✓ Total Events Injected: {total_events}")
print(f"  ├─ OSINT NLP: 100 ({osint_success} sealed, {osint_quarantined} quarantined, {osint_fail} failed)")
print(f"  ├─ Industrial: 50 ({ind_success} processed, {ind_fail} failed)")
print(f"  └─ Feedback: 20 ({fb_success} recorded)")
print(f"\n✓ Success Rate: {total_success}/{total_events} ({100 * total_success / total_events:.1f}%)")
print(f"✓ Ledger Growth: +{blocks_added} blocks (integrity: {'VALID' if chain_valid else 'INVALID'})")
print(f"✓ Risk Mapper: {report['total_regions_monitored']} regions analyzed")
print(f"✓ Adaptive Learning: {len(thresholds)} thresholds calibrated")

print("\n" + "=" * 80)
if chain_valid and total_success >= 160:
    print("🟢 STRESS TEST: PASSED — SYSTEM IS PRODUCTION-READY")
else:
    print("🔴 STRESS TEST: ISSUES DETECTED — REVIEW ABOVE")
print("=" * 80)