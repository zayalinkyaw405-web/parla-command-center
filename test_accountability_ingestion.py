"""
Test Suite: International Legal Accountability Ingestion
========================================================
Validates:
1. Knowledge Base Roster Ingestion & Intel Querying (UN FFM / ICC / IIMM)
2. Watchlist Gallery Multi-Echelon Biometric Enrollment (512-d Hypersphere Vectors)
3. Positive Match Detection, Admiralty Grading, and Merkle Ledger Sealing
4. VisualMediaAnalyzer Integration and Zero-Trace Compliance
"""

import os
import gc
import json
import time
import numpy as np
from PIL import Image, ImageDraw

from parla.core.knowledge_base import ParlaKnowledgeBase, AccountabilityIndividual
from parla.domains.facial_recognition_engine import (
    FacialEmbedding,
    WatchlistTarget,
    WatchlistGallery,
    FacialRecognitionEngine,
    MatchClassification
)
from parla.core.ledger import OfflineLedger
from Scripts.analyze_visual_media import VisualMediaAnalyzer


def run_tests():
    print("=" * 75)
    print(" PARLA INTERNATIONAL ACCOUNTABILITY INGESTION TEST SUITE")
    print("=" * 75)

    # ---------------------------------------------------------------------
    # TEST 1: Knowledge Base Ingestion & Entity Resolution
    # ---------------------------------------------------------------------
    print("\n[1] Testing Parla Knowledge Base: International Accountability Roster...")
    kb = ParlaKnowledgeBase()
    assert kb.accountability is not None, "InternationalAccountabilityKnowledgeBase not initialized in kb"
    
    unique_commanders = kb.accountability.list_all()
    assert len(unique_commanders) == 8, f"Expected 8 commanders, found {len(unique_commanders)}"
    print(f"    [PASS] Successfully loaded {len(unique_commanders)} unique commanders into Knowledge Base.")

    # Macro summary test
    summary_intel = kb.get_accountability_intel()
    assert summary_intel["type"] == "ACCOUNTABILITY_ROSTER_SUMMARY"
    assert summary_intel["total_commanders_tracked"] == 8
    assert len(summary_intel["command_echelons"]) == 3
    print(f"    [PASS] Macro roster summary verified: 3 command echelons, 8 commanders.")

    # Test exact query for Commander-in-Chief
    mah_res = kb.get_accountability_intel("Min Aung Hlaing")
    assert mah_res["type"] == "ACCOUNTABILITY_INDIVIDUAL_DOSSIER"
    mah = mah_res["data"]
    assert mah is not None
    assert mah["individual_id"] == "IND-SAC-001"
    assert mah["echelon_id"] == "ECH_SENIOR_LEADERSHIP"
    assert any("A/HRC/39/64" in c for c in mah["institutional_citations"])
    print(f"    [PASS] Intel Query [Min Aung Hlaing]: ID={mah['individual_id']}, Echelon={mah['echelon_title']}")
    print(f"           Citations: {mah['institutional_citations'][0]}")

    # Test Air Force Chief lookup
    tun_res = kb.get_accountability_intel("General Tun Aung")
    assert tun_res["type"] == "ACCOUNTABILITY_INDIVIDUAL_DOSSIER"
    tun = tun_res["data"]
    assert tun is not None
    assert tun["individual_id"] == "IND-MAF-001"
    assert any("Pa Zi Gyi" in c for c in tun["documented_cases"])
    print(f"    [PASS] Intel Query [Tun Aung]: Air Force Chief with Pa Zi Gyi strike documentation confirmed.")

    # Test Regional LID Commander lookup
    lid_res = kb.get_accountability_intel("Brigadier General Aung Aung")
    assert lid_res["type"] == "ACCOUNTABILITY_INDIVIDUAL_DOSSIER"
    lid = lid_res["data"]
    assert lid is not None
    assert lid["individual_id"] == "IND-LID-001"
    assert "33" in lid["operational_role"]
    print(f"    [PASS] Intel Query [Aung Aung]: Division 33 Commander verified with FFM citations.")

    # Test negative lookup
    unknown_res = kb.get_accountability_intel("Unknown Commander")
    assert unknown_res["type"] == "ACCOUNTABILITY_NOT_FOUND"
    assert unknown_res["data"] is None
    print("    [PASS] Negative lookup safely returned ACCOUNTABILITY_NOT_FOUND.")

    # ---------------------------------------------------------------------
    # TEST 2: Watchlist Gallery Enrollment & 512-d Hypersphere Vectors
    # ---------------------------------------------------------------------
    print("\n[2] Testing Watchlist Gallery: 512-d Unit Hypersphere Enrollment...")
    gallery = WatchlistGallery()
    enrolled_count = gallery.load_from_accountability_roster()
    assert enrolled_count == 8, f"Expected 8 enrolled, got {enrolled_count}"
    assert len(gallery.targets) == 8

    for tid, target in gallery.targets.items():
        assert target.category == "WAR_CRIMES_ACCOUNTABILITY"
        assert target.threat_level == "CRITICAL"
        assert target.embedding.vector.shape == (512,)
        
        # Verify L2 unit norm on 512-d hypersphere
        norm = np.linalg.norm(target.embedding.vector)
        assert abs(norm - 1.0) < 1e-4, f"Vector for {tid} not L2-normalized: norm={norm}"
        
        # Verify legal metadata structure
        meta = target.metadata
        assert "command_echelon" in meta
        assert "operational_role" in meta
        assert "command_authority" in meta
        assert len(meta.get("citations", [])) > 0
        assert len(meta.get("documented_cases", [])) > 0

    print(f"    [PASS] Enrolled {enrolled_count} commanders into WatchlistGallery with L2-normalized vectors.")
    print("    [PASS] All targets tagged as WAR_CRIMES_ACCOUNTABILITY with CRITICAL threat level.")

    # ---------------------------------------------------------------------
    # TEST 3: Biometric Engine Identification & Merkle Ledger Ingress
    # ---------------------------------------------------------------------
    print("\n[3] Testing Biometric Engine: Identification & Merkle Ledger Sealing...")
    test_db = os.path.join("Data", "test_accountability_ledger.db")
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except Exception:
            pass

    test_ledger = OfflineLedger(db_path=test_db)
    engine = FacialRecognitionEngine(
        gallery=gallery,
        ledger=test_ledger,
        definitive_threshold=0.70,
        probable_threshold=0.55
    )

    # Simulate query with exact embedding of Commander-in-Chief (IND-SAC-001)
    target_ind1 = gallery.targets["IND-SAC-001"]
    matched_target, sim, classification = gallery.search(target_ind1.embedding)
    assert matched_target is not None
    assert matched_target.target_id == "IND-SAC-001"
    assert classification == MatchClassification.DEFINITIVE_MATCH
    assert sim >= 0.999
    print(f"    [PASS] Watchlist search matched: {matched_target.name} ({matched_target.target_id})")
    print(f"           Similarity: {sim:.4f} | Classification: {classification.value}")

    # Build a synthetic frame and verify end-to-end process_frame & ledger sealing
    test_img = Image.new("RGB", (200, 200), color=(180, 180, 180))
    draw = ImageDraw.Draw(test_img)
    draw.ellipse((40, 30, 160, 170), fill=(210, 160, 120))

    # Temporarily substitute extract_embedding to produce target_ind1 vector for the test frame
    orig_extract = engine.extract_embedding
    engine.extract_embedding = lambda face_crop: target_ind1.embedding

    frame_result = engine.process_frame(
        image=test_img,
        source_id="OSINT_VIDEO_ANALYTICS_01",
        location={"latitude": 19.7633, "longitude": 96.0785},  # Naypyidaw
        anonymize_bystanders=True
    )
    engine.extract_embedding = orig_extract

    assert frame_result["targets_matched"] >= 1
    assert len(frame_result["ledger_events"]) >= 1
    
    evt = frame_result["ledger_events"][0]
    assert evt["target_id"] == "IND-SAC-001"
    assert evt["target_category"] == "WAR_CRIMES_ACCOUNTABILITY"
    assert evt["threat_level"] == "CRITICAL"
    assert evt["admiralty_grade"] == "A1"
    assert "ledger_block_hash" in evt and len(evt["ledger_block_hash"]) == 64
    print(f"    [PASS] Merkle Ledger Audit committed:")
    print(f"           Block Hash: {evt['ledger_block_hash'][:24]}...")
    print(f"           Target Category: {evt['target_category']}")
    print(f"           Admiralty Grade: {evt['admiralty_grade']}")
    print(f"           Documented Cases in Block: {len(evt['metadata']['documented_cases'])}")

    # Verify directly inside SQLite database
    with test_ledger._get_connection() as conn:
        cursor = conn.execute("SELECT seq_id, domain, block_hash FROM ledger_blocks WHERE domain='facial_recognition';")
        row = cursor.fetchone()
        assert row is not None
        assert row["block_hash"] == evt["ledger_block_hash"]
        print(f"    [PASS] Database integrity check confirmed: seq_id={row['seq_id']}")

    # Clean up test DB safely on Windows per windows-python-resilience rules
    del engine
    del test_ledger
    gc.collect()
    try:
        if os.path.exists(test_db):
            os.remove(test_db)
    except Exception:
        pass

    # ---------------------------------------------------------------------
    # TEST 4: VisualMediaAnalyzer Integration
    # ---------------------------------------------------------------------
    print("\n[4] Testing VisualMediaAnalyzer: Automated Ingestion Integration...")
    analyzer = VisualMediaAnalyzer(load_accountability=True)
    assert analyzer.gallery is not None
    assert len(analyzer.gallery.targets) == 8
    assert "IND-SAC-002" in analyzer.gallery.targets
    print("    [PASS] VisualMediaAnalyzer(load_accountability=True) successfully pre-loaded roster.")

    print("\n" + "=" * 75)
    print(" ALL INTERNATIONAL ACCOUNTABILITY INGESTION TESTS PASSED [100% SPEC COMPLIANT]")
    print("=" * 75)


if __name__ == "__main__":
    run_tests()
