"""
debug_failures.py
Reveals the exact errors in Risk Scoring and Threshold Adjustment.
"""

import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("🔍 TARGETED DEBUG: Risk Scoring + Threshold Adjustment")
print("=" * 70)

# DEBUG 1: Risk Scoring
print("\n[DEBUG 1] RegionalRiskMapper")
print("-" * 70)
try:
    from parla.domains.risk_mapper import RegionalRiskMapper
    mapper = RegionalRiskMapper()
    print(f"  DB Path: {mapper.db_path}")
    
    # Check if DB file exists
    if not os.path.exists(mapper.db_path):
        print(f"  ✗ Database file NOT FOUND at: {mapper.db_path}")
    else:
        print(f"  ✓ Database file exists ({os.path.getsize(mapper.db_path)} bytes)")
    
    # Try to fetch events
    events = mapper._get_recent_events(days=90)
    print(f"  Events fetched: {len(events)}")
    
    # Try full calculation
    report = mapper.calculate_regional_risk(days=90)
    print(f"  ✓ Report generated: {report['total_regions_monitored']} regions")
    
except Exception as e:
    print(f"  ✗ ERROR: {e}")
    traceback.print_exc()

# DEBUG 2: Threshold Adjustment
print("\n[DEBUG 2] FeedbackLoop")
print("-" * 70)
try:
    from parla.core.feedback_loop import FeedbackLoop
    fb = FeedbackLoop()
    print(f"  DB Path: {fb.db_path}")
    
    if not os.path.exists(fb.db_path):
        print(f"  ✗ Database file NOT FOUND at: {fb.db_path}")
    else:
        print(f"  ✓ Database file exists")
    
    # Try to get thresholds
    thresholds = fb.get_current_thresholds()
    print(f"  ✓ Thresholds: {thresholds}")
    
except Exception as e:
    print(f"  ✗ ERROR: {e}")
    traceback.print_exc()

# DEBUG 3: Check actual ledger contents
print("\n[DEBUG 3] Ledger Contents Check")
print("-" * 70)
try:
    import sqlite3
    conn = sqlite3.connect("c:/Users/james/VuZiNat/iot_agent/Data/parla_ledger.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT domain, COUNT(*) FROM ledger_blocks GROUP BY domain")
    domains = cursor.fetchall()
    print("  Domain distribution:")
    for domain, count in domains:
        print(f"    • {domain}: {count} blocks")
    
    # Check OSINT payload structure
    cursor.execute("SELECT payload_json FROM ledger_blocks WHERE domain = 'osint_nlp' LIMIT 1")
    osint_row = cursor.fetchone()
    if osint_row:
        import json
        payload = json.loads(osint_row[0])
        print(f"\n  OSINT payload keys: {list(payload.keys())}")
        if 'event' in payload:
            print(f"  ✓ 'event' key present: {payload['event']}")
        else:
            print(f"  ✗ 'event' key MISSING - this is the bug!")
    
    # Check feedback payload structure
    cursor.execute("SELECT payload_json FROM ledger_blocks WHERE domain = 'feedback' LIMIT 1")
    fb_row = cursor.fetchone()
    if fb_row:
        payload = json.loads(fb_row[0])
        print(f"\n  Feedback payload keys: {list(payload.keys())}")
    else:
        print(f"\n  ✗ No feedback blocks found in ledger")
    
    conn.close()
    
except Exception as e:
    print(f"  ✗ ERROR: {e}")
    traceback.print_exc()

print("\n" + "=" * 70)