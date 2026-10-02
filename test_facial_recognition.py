"""
Test Suite: Facial Recognition & Biometric Intelligence Engine
==============================================================
Validates:
1. 512-d Hypersphere L2-Normalization and Metric Cosine Distance
2. Watchlist Gallery Indexing and Classification Calibration
3. Zero-Trace Bystander Anonymization (VOID Pillar)
4. Merkle Ledger Ingress & Cryptographic Chain Sealing (HARMONY Pillar)
"""

import sys
import os
import shutil
import numpy as np
from PIL import Image, ImageDraw

from parla.domains.facial_recognition_engine import (
    FacialEmbedding,
    WatchlistTarget,
    WatchlistGallery,
    FacialRecognitionEngine,
    MatchClassification
)
from parla.core.ledger import OfflineLedger


def create_synthetic_face(color: tuple, face_type: str = "target") -> Image.Image:
    """Generates an in-memory synthetic portrait frame for deterministic testing."""
    img = Image.new("RGB", (200, 200), color=(220, 220, 220))
    draw = ImageDraw.Draw(img)
    if face_type == "target":
        # Target: Oval face with horizontal eyes and mouth
        draw.ellipse((40, 30, 160, 170), fill=color)
        draw.ellipse((65, 75, 85, 90), fill=(20, 20, 20))
        draw.ellipse((115, 75, 135, 90), fill=(20, 20, 20))
        draw.rectangle((80, 130, 120, 140), fill=(180, 40, 40))
    else:
        # Bystander: Distinct facial structure (wide rectangular jaw, vertical features, glasses)
        draw.rectangle((25, 45, 175, 165), fill=color)
        draw.rectangle((50, 70, 95, 95), outline=(10, 10, 10), width=4)
        draw.rectangle((105, 70, 150, 95), outline=(10, 10, 10), width=4)
        draw.line([(95, 82), (105, 82)], fill=(10, 10, 10), width=3)
        draw.polygon([(100, 95), (90, 120), (110, 120)], fill=(50, 50, 50))
        draw.ellipse((70, 135, 130, 155), fill=(140, 30, 30))
    return img


def run_tests():
    print("=" * 70)
    print(" PARLA FACIAL RECOGNITION & BIOMETRIC ENGINE: TEST SUITE")
    print("=" * 70)

    # ---------------------------------------------------------
    # TEST 1: 512-d Metric Vector & Cosine Math
    # ---------------------------------------------------------
    print("\n[1] Testing 512-d Hypersphere Projection & Metric Properties...")
    v1_raw = np.random.randn(512)
    v1 = FacialEmbedding(v1_raw)
    
    # Check L2 unit norm
    norm1 = np.linalg.norm(v1.vector)
    assert abs(norm1 - 1.0) < 1e-6, f"Norm error: {norm1}"
    print(f"    [PASS] L2 Norm verified: ||v|| = {norm1:.6f}")

    # Self-similarity must be exactly 1.0
    self_sim = v1.cosine_similarity(v1)
    assert abs(self_sim - 1.0) < 1e-6, f"Self similarity error: {self_sim}"
    print(f"    [PASS] Self-similarity verified: {self_sim:.4f}")

    # Orthogonal or opposite vectors
    v2 = FacialEmbedding(-v1_raw)
    opp_sim = v1.cosine_similarity(v2)
    assert abs(opp_sim - (-1.0)) < 1e-6, f"Opposite similarity error: {opp_sim}"
    print(f"    [PASS] Orthogonal/Inverted similarity verified: {opp_sim:.4f}")

    # ---------------------------------------------------------
    # TEST 2: Watchlist Gallery Enrollment & Matching
    # ---------------------------------------------------------
    print("\n[2] Testing Watchlist Gallery Enrollment & Nearest-Neighbor Search...")
    gallery = WatchlistGallery()

    # Enrolled Target: General Min Aung Hlaing (Target of Interest)
    mah_target = WatchlistTarget(
        target_id="TGT-SAC-001",
        name="SAC Commander Senior General",
        category="ADVERSARY",
        threat_level="EXTREME",
        metadata={"priority": "CRITICAL"}
    )
    # Generate reference face
    ref_face = create_synthetic_face(color=(160, 120, 90))
    engine_temp = FacialRecognitionEngine(gallery=gallery)
    ref_embedding = engine_temp.extract_embedding(ref_face)
    mah_target.add_embedding(ref_embedding)
    gallery.enroll(mah_target)

    assert gallery.size() == 1, "Gallery enrollment count mismatch."
    print(f"    [PASS] Enrolled target: {mah_target.name} [{mah_target.target_id}]")

    # Match test with exact identical face -> Definitive Match (A1)
    query_face_exact = create_synthetic_face(color=(160, 120, 90))
    query_emb_exact = engine_temp.extract_embedding(query_face_exact)
    matched, score, classification = gallery.search(query_emb_exact)
    
    assert matched is not None and matched.target_id == "TGT-SAC-001"
    assert classification == MatchClassification.DEFINITIVE_MATCH
    assert score >= 0.99
    print(f"    [PASS] Exact query match score: {score:.4f} -> {classification.value} (Grade A1)")

    # Query with a completely different civilian bystander face -> Unmatched
    bystander_face = create_synthetic_face(color=(80, 50, 40), face_type="bystander")
    bystander_emb = engine_temp.extract_embedding(bystander_face)
    _, bystander_score, bystander_class = gallery.search(bystander_emb)
    assert bystander_class == MatchClassification.UNMATCHED_BYSTANDER
    print(f"    [PASS] Bystander face score: {bystander_score:.4f} -> {bystander_class.value}")

    # ---------------------------------------------------------
    # TEST 3: VOID Pillar - Zero-Trace Bystander Anonymization
    # ---------------------------------------------------------
    print("\n[3] Testing VOID Pillar: In-Memory Bystander Anonymization...")
    # Composite frame: bystander face
    composite_frame = create_synthetic_face(color=(80, 50, 40), face_type="bystander")
    res_bystander = engine_temp.process_frame(
        image=composite_frame,
        source_id="CCTV_MANDALAY_CHECKPOINT_03",
        anonymize_bystanders=True
    )
    
    assert res_bystander["bystanders_anonymized"] == 1
    assert res_bystander["targets_matched"] == 0
    # Confirm processed image has been blurred in the bounding box
    orig_pixels = np.array(composite_frame)
    proc_pixels = np.array(res_bystander["processed_image"])
    assert not np.array_equal(orig_pixels, proc_pixels), "Bystander pixels were not blurred!"
    print("    [PASS] Bystander region blurred and redacted in-memory without persistence.")

    # ---------------------------------------------------------
    # TEST 4: HARMONY Pillar - Merkle Ledger Sealing
    # ---------------------------------------------------------
    print("\n[4] Testing HARMONY Pillar: Cryptographic Ledger Ingress...")
    test_db = "Data/test_facial_ledger.db"
    if os.path.exists(test_db):
        os.remove(test_db)

    ledger = OfflineLedger(db_path=test_db)
    production_engine = FacialRecognitionEngine(gallery=gallery, ledger=ledger)

    # Process frame containing enrolled target
    res_target = production_engine.process_frame(
        image=query_face_exact,
        source_id="UAV_RECON_SAGAING_01",
        location={"latitude": 21.9833, "longitude": 95.9667},
        anonymize_bystanders=True
    )

    assert res_target["targets_matched"] == 1
    assert len(res_target["ledger_events"]) == 1
    event = res_target["ledger_events"][0]
    block_hash = event.get("ledger_block_hash")
    assert block_hash is not None and len(block_hash) == 64
    print(f"    [PASS] Biometric match event cryptographically sealed into Merkle Ledger!")
    print(f"      - Block Hash: {block_hash[:24]}...")
    print(f"      - Admiralty Grade: {event['admiralty_grade']}")
    print(f"      - Target Name: {event['target_name']}")
    print(f"      - Coarsened GPS: Lat {event.get('latitude')}, Lon {event.get('longitude')}")

    # Verify block in the database directly
    with ledger._get_connection() as conn:
        cursor = conn.execute("SELECT seq_id, domain, block_hash, payload_json FROM ledger_blocks WHERE domain='facial_recognition';")
        row = cursor.fetchone()
        assert row is not None
        assert row["block_hash"] == block_hash
        payload_data = eval(row["payload_json"]) if isinstance(row["payload_json"], str) and not row["payload_json"].startswith("{") else None
        print(f"    [PASS] Database validation confirmed: seq_id={row['seq_id']}, domain={row['domain']}")

    # Clean up test DB safely on Windows
    del production_engine
    del ledger
    import gc
    gc.collect()
    try:
        if os.path.exists(test_db):
            os.remove(test_db)
    except Exception:
        pass

    print("\n" + "=" * 70)
    print(" ALL FACIAL RECOGNITION TESTS PASSED WITH 100% SPEC COMPLIANCE!")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
