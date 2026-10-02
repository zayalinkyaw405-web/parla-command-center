"""
test_knowledge_base_osint.py
Verification of upgraded OSINTKnowledgeBase & ParlaKnowledgeBase.analyze_osint
"""

import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from parla.core.knowledge_base import ParlaKnowledgeBase, OSINTKnowledgeBase

def test_osint_kb_direct():
    print("=" * 60)
    print("TEST 1: OSINTKnowledgeBase Direct Methods")
    print("=" * 60)
    
    kb = OSINTKnowledgeBase()
    
    # 1. Classification
    matches = kb.classify_text("Reports of drone strike and kamikaze drone drop bomb on military convoy")
    assert len(matches) > 0
    assert matches[0][0] == "DRONE_WARFARE"
    print(f"[+] Drone warfare correctly classified: {matches[0]}")
    
    # 2. Thermobaric classification
    matches_tb = kb.classify_text("Thermobaric vacuum bomb dropped causing lung collapse")
    assert matches_tb[0][0] == "CHEMICAL_THERMOBARIC_ATTACK"
    print(f"[+] Thermobaric correctly classified: {matches_tb[0]}")

    # 3. Admiralty evaluation
    adm = kb.evaluate_admiralty(
        reliability="C",
        credibility=3,
        corroborating_evidence=[
            {"modality": "GEOINT_THERMAL"},
            {"modality": "SIGINT_FLIGHT"}
        ]
    )
    print(f"[+] Admiralty Evaluation: {adm['initial_grade']} -> {adm['elevated_grade']} (Confidence: {adm['elevated_confidence']})")
    assert adm["elevated_grade"] == "A1"
    assert adm["actionable_for_civilian_protection"] is True

    # 4. Tactical Entity Extraction
    entities = kb.extract_tactical_entities("Two Su-30 jets dropped FAB-500 bombs while AA units engaged")
    print(f"[+] Tactical Entities: {entities}")
    assert "SU_30SME" in entities["aircraft"]
    assert "FAB_500" in entities["ordnance"]
    assert "AA" in entities["factions"]
    print("✓ Test 1 Passed.\n")

def test_parla_kb_unified_analysis():
    print("=" * 60)
    print("TEST 2: ParlaKnowledgeBase Unified Multi-INT Analysis")
    print("=" * 60)
    
    pkb = ParlaKnowledgeBase()
    
    # Analyze raw report with tactical aircraft, munitions, and satellite corroboration
    raw_text = "Urgent: Su-30 fighter jet conducted high-speed bombing run dropping thermobaric ODAB bombs near school."
    
    result = pkb.analyze_osint(
        text=raw_text,
        source_reliability="C",
        base_credibility=3,
        corroborations=[
            {"modality": "GEOINT_THERMAL", "detail": "NASA FIRMS thermal hotspot detected"}
        ]
    )
    
    print(f"[+] Primary Event: {result['primary_event']}")
    print(f"[+] Admiralty Grade: {result['admiralty_grade']} (Confidence: {result['confidence']})")
    print(f"[+] Action Directive: {result['action_directive']}")
    print(f"[+] Enriched SAC Threats: {result['enriched_sac_threats']}")
    print(f"[+] Enriched Ordnance: {result['enriched_ordnance']}")
    
    assert result["primary_event"] in ("AIRSTRIKE", "CHEMICAL_THERMOBARIC_ATTACK")
    assert result["action_directive"] == "URGENT_CIVILIAN_SHELTER_ALERT"
    assert len(result["enriched_sac_threats"]) > 0
    assert "Sukhoi Su-30SME" in result["enriched_sac_threats"][0]["model"]
    assert len(result["enriched_ordnance"]) > 0
    assert result["enriched_ordnance"][0]["system"] == "ODAB-500PM Thermobaric FAE"
    print("✓ Test 2 Passed.\n")

if __name__ == "__main__":
    test_osint_kb_direct()
    test_parla_kb_unified_analysis()
    print("=" * 60)
    print("🎉 ALL KNOWLEDGE BASE OSINT TESTS PASSED")
    print("=" * 60)
