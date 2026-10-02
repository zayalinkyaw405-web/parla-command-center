"""
pipeline_test.py
End-to-End Pipeline Test for Parla Command Center.
Comprehensive integration test across:
  - Track A: Industrial IoT Telemetry & RL Adaptive Tuning
  - Track B: OSINT Feed Ingestion & Two-Tier PII Redaction
  - Track C: Multi-INT Triangulation (NASA FIRMS Satellite Thermal + ADS-B Flight Transponder + NATO Admiralty 6x6 Elevation)
  - Track D: Unified Knowledge Base Cross-Referencing (SAC Aircraft Fleet & Military Arsenal Databases)
  - Track E: Zero-Trace Ledger Sealing & Merkle Block Integrity Audit
  - Track F: Zero-Trust Security Gate & Tamper Quarantine Routing
  - Track G: Store-and-Forward Sync Checkpoints & Deep Chain Cryptographic Verification
"""

import os
import sys
import time
import json
import hmac
import hashlib
import sqlite3
import numpy as np

# Ensure root directory is in python path
WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WORKSPACE_ROOT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from parla.domains.industrial import IndustrialProcessor
from parla.domains.osint_ingestor import OSINTIngestor, IngestedEvent
from parla.domains.real_data_gateway import RealDataGateway, NormalizedTelemetry
from parla.domains.feedback_loop import FeedbackLoop, FeedbackSignal
from parla.domains.geoint_firms_ingestor import GEOINTFirmsIngestor
from parla.domains.admiralty_evaluator import AdmiraltyEvaluator, SourceReliability, InformationCredibility
from parla.domains.osint_nlp import OSINTEventExtractor, generate_osint_signature
from parla.core.knowledge_base import ParlaKnowledgeBase
from parla.core.ledger import OfflineLedger

# Configuration
SECRET_KEY = b"parla_industrial_offline_key_2026"
TEST_DB_PATH = os.path.join(WORKSPACE_ROOT, "test_parla_ledger.db")

def print_section(title: str):
    print("\n" + "=" * 75)
    print(f" {title}")
    print("=" * 75)

def main():
    print_section("PARLA COMMAND CENTER: EXPANDED FULL-STACK PIPELINE TEST (7 TRACKS)")
    
    # Reset test database for clean deterministic execution
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass

    # Initialize all modules
    print("\n[+] Initializing Parla Core & Domain Engines...")
    test_ledger = OfflineLedger(db_path=TEST_DB_PATH)
    ind_proc = IndustrialProcessor(db_path=TEST_DB_PATH, ledger=test_ledger)
    osint_proc = OSINTIngestor(kb_dir=os.path.join(WORKSPACE_ROOT, "Project"))
    gateway = RealDataGateway()
    rl_loop = FeedbackLoop(kb_dir=os.path.join(WORKSPACE_ROOT, "Project"))
    firms = GEOINTFirmsIngestor()
    admiralty = AdmiraltyEvaluator()
    extractor = OSINTEventExtractor(ledger=test_ledger)
    pkb = ParlaKnowledgeBase()
    
    print("    [1] Industrial Processor (Zero-Trust Ledger & Modal EMD)")
    print("    [2] OSINT Ingestor (Two-Tier Regex + spaCy NER PII Redaction)")
    print("    [3] Real Data Gateway (REST, MQTT, FIRMS & ADS-B)")
    print("    [4] Reinforcement Learning Feedback Loop (Adaptive DBSCAN)")
    print("    [5] NASA FIRMS GEOINT Ingestor (Space-Time Haversine Matcher)")
    print("    [6] NATO 6x6 Admiralty Evaluator (Multi-INT Elevation)")
    print("    [7] OSINT NLP Event Extractor (Tactical Entity Linker & Ledger)")
    print("    [8] Unified Parla Knowledge Base (Cross-Domain Fusion)")
    print("    [9] Offline-First ACID Ledger (WAL Mode, Quarantine & Store-and-Forward)")

    # =====================================================================
    # TRACK A: Industrial IoT Telemetry & RL Adaptation
    # =====================================================================
    print_section("TRACK A: Industrial IoT Telemetry & RL Adaptation")
    
    print("\n[1] Simulating Edge Node: Generating signed vibration telemetry...")
    machine_id = "PUMP-ALPHA-01"
    np.random.seed(42)
    t = np.linspace(0, 1, 1000)
    vibration_data = np.random.normal(0, 0.5, 1000) + 2.5 * np.sin(2 * np.pi * 50 * t)
    temperature = 72.0
    
    payload = {"machine_id": machine_id, "vibration_data": vibration_data.tolist(), "temperature": temperature}
    payload_json = json.dumps(payload, sort_keys=True)
    signature = hmac.new(SECRET_KEY, payload_json.encode(), hashlib.sha256).hexdigest()
    
    print("[2] Processing through Industrial Processor...")
    ind_result = ind_proc.process_telemetry(machine_id, vibration_data, temperature, signature)
    print(f"    Status: {ind_result['status']}")
    print(f"    Urgency: {ind_result['directive']['urgency']}")
    print(f"    Failure Mode: {ind_result['directive']['failure_mode']}")
    print(f"    Ledger Hash: {ind_result['ledger_hash'][:32]}...")
    assert ind_result['status'] == "PROCESSED"
    
    print("\n[3] Simulating Human Operator Correction (RL Feedback)...")
    feedback_signal = FeedbackSignal(
        event_id=ind_result['ledger_hash'][:16],
        original_prediction=ind_result['directive']['failure_mode'],
        true_label="TEMPORARY_LOAD_SPIKE",
        reward=-1.0,
        confidence=ind_result['directive']['confidence']
    )
    rl_result = rl_loop.process_feedback(feedback_signal)
    print(f"    RL Status: {rl_result['status']}")
    print(f"    System Adaptation: {rl_result['adjustment_made']}")
    print(f"    New DBSCAN eps: {rl_result['new_dbscan_eps']}")
    assert rl_result['status'] == "LEARNED"

    # =====================================================================
    # TRACK B: OSINT Feed Ingestion & PII Redaction
    # =====================================================================
    print_section("TRACK B: OSINT Feed Ingestion & PII Redaction")
    
    print("\n[1] Simulating REST API: Fetching raw conflict telemetry...")
    mock_api_response = {
        "data": [
            {
                "source": "Myanmar Peace Monitor",
                "description": "At 08:00, artillery shelling was reported near Hpakant. Local spotter U Aung (aung.ko@news.mm, +95 9 123 456 789) reported civilian displacements near 25.4567, 96.1234.",
                "urls": ["https://example.com/hpakant-report"]
            }
        ]
    }
    
    normalized_event = NormalizedTelemetry(
        source_type="REST_API",
        event_id=f"rest_{int(time.time())}_0",
        timestamp=time.time(),
        raw_payload=mock_api_response["data"][0],
        normalized_data={
            "text": mock_api_response["data"][0]["description"],
            "location": "Hpakant",
            "timestamp_raw": "08:00"
        }
    )
    print(f"    Normalized Event ID: {normalized_event.event_id}")
    
    sanitized_text = osint_proc._redact_pii(normalized_event.normalized_data["text"])
    category = osint_proc._classify_event(sanitized_text, normalized_event.raw_payload)
    print(f"    Sanitized Text: {sanitized_text[:75]}...")
    print(f"    Classified Category: {category}")
    assert "+95 9 123 456 789" not in sanitized_text
    assert "aung.ko@news.mm" not in sanitized_text
    
    final_event = IngestedEvent(
        timestamp="2026-10-02",
        source=normalized_event.raw_payload["source"],
        category=category,
        summary=sanitized_text,
        original_hash=ind_result['ledger_hash'][:16],
        source_links=normalized_event.raw_payload["urls"]
    )
    osint_proc._append_to_kb(final_event)
    print("    ✓ Successfully appended to Project/news-and-market-trends.md")

    # =====================================================================
    # TRACK C: Multi-INT Triangulation (FIRMS + ADS-B + Admiralty 6x6)
    # =====================================================================
    print_section("TRACK C: Multi-INT Triangulation (FIRMS + ADS-B + Admiralty 6x6)")
    
    # 1. Register Satellite Thermal Anomaly via Gateway
    print("\n[1] Registering Satellite Thermal Hotspot (NASA FIRMS VIIRS 375m)...")
    firms_records = [
        {
            "latitude": 21.982,
            "longitude": 95.895,
            "brightness": 368.5,
            "acquisition_time": "2026-10-02T04:10:00Z",
            "satellite": "VIIRS_NOAA20",
            "confidence": "high",
            "frp": 52.4
        }
    ]
    gateway.ingest_firms_records(firms_records, firms)
    
    # 2. Register Military Flight Sortie via Gateway
    print("[2] Ingesting ADS-B Flight Transponder Telemetry (Military Sortie)...")
    flight_records = [
        {
            "callsign": "MAF-STRIKE-02",
            "icao24": "7101A2",
            "altitude_m": 3200.0,
            "velocity_mps": 220.0,
            "latitude": 21.950,
            "longitude": 95.910
        }
    ]
    norm_flights = gateway.ingest_adsb_telemetry(flight_records)
    print(f"    Ingested Sortie: {norm_flights[0].normalized_data['callsign']} (Speed: {norm_flights[0].normalized_data['velocity_kmh']} km/h)")
    
    # 3. Space-Time Proximity Matching
    print("[3] Corroborating Ground Event against Satellite Thermal Hotspot...")
    matched, match_details = firms.corroborate_event(
        target_lat=21.980,
        target_lon=95.900,
        target_time_iso="2026-10-02T04:30:00Z",
        radius_km=15.0,
        window_hours=6.0
    )
    print(f"    FIRMS Corroboration Match: {matched}")
    print(f"    Distance: {match_details['distance_km']} km, Time Delta: {match_details['time_delta_hours']} h, FRP: {match_details['frp_mw']} MW")
    print(f"    Sector Hash: {match_details['sector_hash']}")
    assert matched is True

    # 4. Admiralty 6x6 Grade Elevation
    print("[4] Evaluating NATO 6x6 Admiralty Grading...")
    assessment = admiralty.evaluate(
        reliability=SourceReliability.C,
        credibility=InformationCredibility.POSSIBLY_TRUE,
        corroborating_evidence=[
            match_details,
            {"modality": "SIGINT_FLIGHT", "callsign": norm_flights[0].normalized_data['callsign']}
        ]
    )
    print(f"    Initial Grade: {assessment.initial_grade} (Confidence: {assessment.initial_confidence})")
    print(f"    Elevated Grade: {assessment.elevated_grade} (Confidence: {assessment.elevated_confidence})")
    print(f"    Actionable for Civilian Protection: {assessment.actionable_for_civilian_protection}")
    assert assessment.elevated_grade == "A1"
    assert assessment.elevated_confidence >= 0.90

    # =====================================================================
    # TRACK D: Unified Knowledge Base Threat Cross-Referencing
    # =====================================================================
    print_section("TRACK D: Unified Knowledge Base Threat Cross-Referencing")
    
    raw_dispatch = (
        "Tactical Dispatch: A Sukhoi Su-30SME fighter jet conducted dive-bombing pass dropping "
        "thermobaric ODAB-500 vacuum bomb near market center. Eyewitness: Ko Min (phone: +95-9-987654321). "
        "Casualties reported. Informant email: spotter@node.org, coords: 21.98012, 95.90012."
    )
    
    print("\n[1] Querying ParlaKnowledgeBase.analyze_osint() with Multi-INT Context...")
    kb_analysis = pkb.analyze_osint(
        text=raw_dispatch,
        source_reliability="C",
        base_credibility=3,
        corroborations=[match_details]
    )
    
    print(f"    Classified Event: {kb_analysis['primary_event']}")
    print(f"    Admiralty Grade: {kb_analysis['admiralty_grade']} (Confidence: {kb_analysis['confidence']})")
    print(f"    Action Directive: {kb_analysis['action_directive']}")
    
    sac_threats = kb_analysis['enriched_sac_threats']
    ordnance_threats = kb_analysis['enriched_ordnance']
    if sac_threats:
        print(f"    Resolved Airframe: {sac_threats[0]['model']} (Threat: {sac_threats[0]['threat_level']})")
        print(f"    Operating Bases: {sac_threats[0]['primary_bases']}")
    if ordnance_threats:
        print(f"    Resolved Munition: {ordnance_threats[0]['system']} (Lethal Radius: {ordnance_threats[0]['lethal_radius_m']} m)")
        print(f"    Humanitarian Flag: {ordnance_threats[0]['humanitarian_flag']}")

    assert kb_analysis['action_directive'] == "URGENT_CIVILIAN_SHELTER_ALERT"
    assert len(sac_threats) > 0
    assert len(ordnance_threats) > 0

    # =====================================================================
    # TRACK E: Zero-Trace Ledger Sealing & Cryptographic Audit
    # =====================================================================
    print_section("TRACK E: Zero-Trace Ledger Sealing & Cryptographic Audit")
    
    print("\n[1] Processing and Sealing Sanitized Payload into Merkle Ledger...")
    sig = generate_osint_signature(raw_dispatch)
    extract_result = extractor.process_osint_payload(
        raw_text=raw_dispatch,
        signature=sig,
        source_id="SPOTTER_NODE_DELTA",
        source_reliability="C",
        base_credibility=3,
        corroborating_evidence=[match_details]
    )
    
    print(f"    Ledger Seal Status: {extract_result['status']}")
    print(f"    Merkle Block Hash: {extract_result['ledger_hash'][:32]}...")
    print(f"    Seq ID: {extract_result['seq_id']}")
    assert extract_result['status'] == "SEALED"

    print("\n[2] Verifying Ledger Block Integrity & Zero PII Leakage...")
    conn = sqlite3.connect(TEST_DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT payload_json FROM ledger_blocks ORDER BY seq_id DESC LIMIT 1")
    sealed_row = cur.fetchone()
    conn.close()
    
    assert sealed_row is not None
    saved_payload = sealed_row[0]
    
    # Assert zero PII leaks
    assert "+95-9-987654321" not in saved_payload, "Leak: Phone number present in ledger!"
    assert "spotter@node.org" not in saved_payload, "Leak: Email address present in ledger!"
    assert "21.98012" not in saved_payload, "Leak: Raw coordinates present in ledger!"
    assert "Ko Min" not in saved_payload, "Leak: Person name present in ledger!"
    
    print("    ✓ Phone number: REDACTED")
    print("    ✓ Email address: REDACTED")
    print("    ✓ Exact GPS coordinates: REDACTED & FUZZED")
    print("    ✓ Informant identity: ZEROIZED")
    print("    ✓ Cryptographic Merkle Hash: INTACT")

    # =====================================================================
    # TRACK F: Zero-Trust Security Gate & Tamper Quarantine Routing
    # =====================================================================
    print_section("TRACK F: Zero-Trust Security Gate & Tamper Quarantine Routing")
    
    print("\n[1] Simulating Cryptographic Attack: Tampered HMAC Signature...")
    malicious_sig = "deadbeefcafebabe0000111122223333444455556666777788889999aaaabbbb"
    tampered_osint_result = extractor.process_osint_payload(
        raw_text="MALICIOUS_DISPATCH: Injected false alarm without valid signature.",
        signature=malicious_sig,
        source_id="ROGUE_AGENT_X"
    )
    print(f"    Status: {tampered_osint_result['status']}")
    print(f"    Reason: {tampered_osint_result['reason']}")
    assert tampered_osint_result['status'] == "DROPPED_AND_QUARANTINED"

    print("\n[2] Simulating Industrial Telemetry Attack: Forged Edge Telemetry...")
    bad_ind_result = ind_proc.process_telemetry("PUMP-FORGED", vibration_data, temperature, malicious_sig)
    print(f"    Status: {bad_ind_result['status']}")
    print(f"    Action: {bad_ind_result['action']}")
    assert bad_ind_result['status'] == "REJECTED"

    print("\n[3] Testing Direct Ingress Malformed Payload Quarantine...")
    # Injecting invalid non-dictionary payload directly to test quarantine isolation
    success, reason, block = test_ledger.record_event(
        domain="INTRUSION_DETECTION",
        payload="MALFORMED_NON_DICT_STRING",  # type: ignore
        source_id="ATTACK_SIMULATOR"
    )
    print(f"    Append Success: {success}")
    print(f"    Quarantine Flag: {reason}")
    assert success is False
    assert "Quarantined" in reason

    print("\n[4] Auditing Quarantine Table for Forensic Artifacts...")
    quarantine_records = test_ledger.get_quarantine_records()
    print(f"    Quarantine Records Captured: {len(quarantine_records)}")
    assert len(quarantine_records) >= 2
    for qr in quarantine_records[:2]:
        print(f"    • Domain: {qr['domain']}, Source: {qr['source_id']}, Reason: {qr['reason']}")

    # =====================================================================
    # TRACK G: Store-and-Forward Sync Checkpoints & Deep Chain Cryptographic Verification
    # =====================================================================
    print_section("TRACK G: Store-and-Forward Sync & Deep Chain Cryptographic Verification")
    
    print("\n[1] Inspecting Store-and-Forward Event Queue...")
    pending_events = test_ledger.get_pending_events()
    print(f"    Pending Forward Events in Queue: {len(pending_events)}")
    assert len(pending_events) >= 1
    
    pending_seq_ids = [evt["seq_id"] for evt in pending_events]
    print(f"    Pending Sequence IDs: {pending_seq_ids}")

    print("\n[2] Simulating Satellite Uplink Burst (Marking Blocks as SYNCED)...")
    test_ledger.mark_synced(pending_seq_ids)
    remaining_pending = test_ledger.get_pending_events()
    print(f"    Remaining Pending Events: {len(remaining_pending)}")
    assert len(remaining_pending) == 0

    print("\n[3] Querying Operational Statistics & Active Backlog...")
    stats = test_ledger.get_stats()
    print(f"    Total Blocks Committed: {stats['total_blocks']}")
    print(f"    Synced Blocks: {stats['synced_blocks']}")
    print(f"    Quarantined Records: {stats['quarantine_count']}")
    print(f"    Active Domains: {stats['active_domains']}")
    assert stats['total_blocks'] >= 2
    assert stats['quarantine_count'] >= 2

    print("\n[4] Executing Deep Mathematical Chain Integrity Audit...")
    audit = test_ledger.verify_chain_integrity()
    print(f"    Audit Valid: {audit['is_valid']}")
    print(f"    Total Blocks Audited: {audit['total_blocks']}")
    print(f"    Audit Message: {audit['message']}")
    assert audit['is_valid'] is True
    assert len(audit['errors']) == 0

    # =====================================================================
    # FINAL SUMMARY
    # =====================================================================
    print_section("EXPANDED PIPELINE TEST: 100% SUCCESS ACROSS ALL 7 TRACKS")
    print("All 7 operational tracks executed cleanly and certified:")
    print("  • Track A: Industrial IoT Telemetry & RL Adaptation          -> PASSED")
    print("  • Track B: OSINT Ingestion & PII Redaction                  -> PASSED")
    print("  • Track C: Multi-INT Triangulation & Admiralty 6x6          -> PASSED (Elevated to A1)")
    print("  • Track D: Unified Knowledge Base Threat Cross-Referencing -> PASSED (Shelter Alert Triggered)")
    print("  • Track E: Zero-Trace Ledger Sealing & Cryptographic Audit     -> PASSED (0% PII Leakage)")
    print("  • Track F: Zero-Trust Security Gate & Tamper Quarantine      -> PASSED (Intrusions Isolated)")
    print("  • Track G: Store-and-Forward Sync & Deep Chain Audit         -> PASSED (100% Cryptographic Integrity)")
    print("=" * 75 + "\n")

if __name__ == "__main__":
    main()