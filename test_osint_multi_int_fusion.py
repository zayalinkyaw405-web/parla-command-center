"""
test_osint_multi_int_fusion.py
End-to-end verification of Maximum Capability OSINT:
1. Multi-INT Triangulation (SOCMINT + NASA FIRMS GEOINT + ADS-B Flight Telemetry)
2. NATO 6x6 Admiralty System Grading & Dynamic Corroboration Escalation
3. Tactical Knowledge Matrix Linking (SAC Aircraft & Munitions)
4. Zero-Trace PII & Micro-Coordinate Neutralization
5. Cryptographic Offline Ledger Verification
"""

import sys
import os
import json

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parla.domains.admiralty_evaluator import (
    AdmiraltyEvaluator,
    SourceReliability,
    InformationCredibility
)
from parla.domains.geoint_firms_ingestor import GEOINTFirmsIngestor
from parla.domains.real_data_gateway import RealDataGateway
from parla.domains.osint_nlp import OSINTEventExtractor, generate_osint_signature
from parla.core.ledger import OfflineLedger

def test_admiralty_and_corroboration():
    print("=" * 70)
    print("TEST 1: NATO 6x6 Admiralty System & Multi-INT Corroboration")
    print("=" * 70)

    evaluator = AdmiraltyEvaluator(alert_threshold_confidence=0.70)

    # Base unverified eyewitness: C3 (Fairly reliable source, possibly true)
    assessment_base = evaluator.evaluate(
        reliability=SourceReliability.C,
        credibility=InformationCredibility.POSSIBLY_TRUE
    )
    print(f"[-] Base Eyewitness Grade: {assessment_base.initial_grade} (Confidence: {assessment_base.elevated_confidence})")
    assert assessment_base.initial_grade == "C3"
    assert assessment_base.elevated_confidence == 0.65
    assert not assessment_base.actionable_for_civilian_protection

    # Corroborated with NASA FIRMS thermal anomaly + ADS-B military flight detection
    corroborating_data = [
        {"modality": "GEOINT_THERMAL", "detail": "NASA FIRMS VIIRS 375m thermal spike 4.2 km from target"},
        {"modality": "SIGINT_FLIGHT", "detail": "ADS-B military sortie departing Tada-U Airbase"}
    ]
    assessment_elevated = evaluator.evaluate(
        reliability=SourceReliability.C,
        credibility=InformationCredibility.POSSIBLY_TRUE,
        corroborating_evidence=corroborating_data
    )
    print(f"[+] Elevated Multi-INT Grade: {assessment_elevated.elevated_grade} (Confidence: {assessment_elevated.elevated_confidence})")
    print(f"    Corroborating Modalities: {assessment_elevated.corroborating_modalities}")
    print(f"    Actionable For Protection: {assessment_elevated.actionable_for_civilian_protection}")
    assert assessment_elevated.elevated_grade == "A1"
    assert assessment_elevated.elevated_confidence >= 0.90
    assert assessment_elevated.actionable_for_civilian_protection

    # Contradiction test: Conflicting reports downgrade credibility
    assessment_contradicted = evaluator.evaluate(
        reliability=SourceReliability.C,
        credibility=InformationCredibility.POSSIBLY_TRUE,
        corroborating_evidence=corroborating_data,
        contradiction_evidence=["MUTUALLY_EXCLUSIVE_IMPACT_CLAIMS"]
    )
    print(f"[!] Contradiction Detected Grade: {assessment_contradicted.elevated_grade} (Confidence: {assessment_contradicted.elevated_confidence})")
    assert assessment_contradicted.elevated_grade in ("C4", "A4", "B4")
    assert not assessment_contradicted.actionable_for_civilian_protection
    print("✓ Test 1 Passed.\n")


def test_firms_geoint_proximity():
    print("=" * 70)
    print("TEST 2: NASA FIRMS Satellite Thermal Space-Time Proximity Match")
    print("=" * 70)

    firms = GEOINTFirmsIngestor()

    # Register satellite thermal anomaly in Magway region
    # Lat: 20.154, Lon: 94.945 at 2026-10-02T03:30:00Z
    firms.add_anomaly(
        lat=20.154,
        lon=94.945,
        brightness_k=365.4,
        acq_time="2026-10-02T03:30:00Z",
        satellite="VIIRS_NOAA20",
        confidence="high",
        frp_mw=45.2
    )

    # 1. Matching ground report 5 km away within 1 hour
    matched, details = firms.corroborate_event(
        target_lat=20.180,
        target_lon=94.960,
        target_time_iso="2026-10-02T04:15:00Z",
        radius_km=15.0,
        window_hours=6.0
    )
    print(f"[+] Ground Report (Magway) matched against NASA FIRMS: {matched}")
    if matched:
        print(f"    Satellite: {details['satellite']}, Distance: {details['distance_km']} km, Time Delta: {details['time_delta_hours']} h, FRP: {details['frp_mw']} MW")
        print(f"    Fuzzed Sector Hash (Void Pillar): {details['sector_hash']}")
    assert matched is True
    assert details["distance_km"] < 10.0

    # 2. Non-matching ground report 300 km away in Shan State
    matched_distant, _ = firms.corroborate_event(
        target_lat=22.934,
        target_lon=97.752,
        target_time_iso="2026-10-02T04:15:00Z",
        radius_km=15.0,
        window_hours=6.0
    )
    print(f"[-] Distant Ground Report (Shan) matched: {matched_distant}")
    assert matched_distant is False
    print("✓ Test 2 Passed.\n")


def test_end_to_end_multi_int_pipeline():
    print("=" * 70)
    print("TEST 3: End-to-End Multi-INT Triangulation & Zero-Trace Sealing")
    print("=" * 70)

    extractor = OSINTEventExtractor()

    # Raw messy field report with critical tactical intelligence & sensitive PII
    raw_osint = (
        "CONFIDENTIAL DISPATCH: Today around 09:30, two Yak-130 strike jets from Tada-U Airbase "
        "dropped heavy thermobaric fuel-air explosive vacuum bombs on Magway civilian settlements. "
        "Casualties reported. Informant: U Aung Myint (NRC-12/MAG-987654), phone: +95-9-798765432, "
        "email: operator_recon@proton.me. Exact strike coordinates: 20.15432, 94.94567."
    )

    # Sign with node key
    sig = generate_osint_signature(raw_osint)

    # Provide corroborating satellite and flight evidence
    corroborating_evidence = [
        {
            "modality": "GEOINT_THERMAL",
            "satellite": "VIIRS_NOAA20",
            "distance_km": 3.8,
            "frp_mw": 48.5
        },
        {
            "modality": "SIGINT_FLIGHT",
            "aircraft": "YAK-130",
            "origin_base": "Tada-U",
            "transponder_loss_near_target": True
        }
    ]

    result = extractor.process_osint_payload(
        raw_text=raw_osint,
        signature=sig,
        source_id="RECON_NODE_04",
        source_reliability="C",
        base_credibility=3,
        corroborating_evidence=corroborating_evidence
    )

    print(f"[+] Status: {result['status']}")
    print(f"[+] Ledger Block Hash: {result['ledger_hash'][:32]}...")
    print(f"[+] Event Type: {result['event']['event_type']}")
    print(f"[+] Elevated Admiralty Grade: {result['event']['admiralty_grade']} (Initial was {result['event']['admiralty_initial']})")
    print(f"[+] Confidence: {result['event']['confidence']}")
    print(f"[+] Action Directive: {result['event']['action']}")
    
    tactical = result['event'].get('tactical_intel', {})
    print(f"[+] Extracted Tactical Aircraft: {[a['aircraft_type'] for a in tactical.get('aircraft', [])]}")
    print(f"[+] Extracted Ordnance Matrix: {[o['ordnance_type'] for o in tactical.get('ordnance', [])]}")
    print(f"[+] Corroborating Modal Vectors: {result['event']['corroborations']}")

    # Verify PII was thoroughly sanitized from ledger payload
    db_path = extractor.ledger.db_path
    import sqlite3
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT payload_json FROM ledger_blocks ORDER BY seq_id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()

    assert row is not None
    saved_payload = row[0]

    # Verify zero PII leaked into ledger
    assert "+95-9-798765432" not in saved_payload, "Leak: Phone number found in ledger!"
    assert "operator_recon@proton.me" not in saved_payload, "Leak: Email found in ledger!"
    assert "987654" not in saved_payload, "Leak: National ID found in ledger!"
    assert "20.15432" not in saved_payload, "Leak: Exact latitude found in ledger!"
    assert "U Aung Myint" not in saved_payload, "Leak: Person name found in ledger!"
    print("🛡️ PII Zero-Trace Audit: Clean. Zero source identifiers leaked to ledger.")

    assert result['event']['admiralty_grade'] == "A1"
    assert result['event']['action'] == "URGENT_CIVILIAN_SHELTER_ALERT"
    print("✓ Test 3 Passed.\n")

if __name__ == "__main__":
    test_admiralty_and_corroboration()
    test_firms_geoint_proximity()
    test_end_to_end_multi_int_pipeline()
    print("=" * 70)
    print("🎉 ALL MAXIMUM OSINT CAPABILITY TESTS PASSED ACCURATELY")
    print("=" * 70)
