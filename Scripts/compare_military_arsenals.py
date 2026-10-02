"""
Scripts/compare_military_arsenals.py
Evaluates and compares weapons systems, domestic production facilities,
ammunition calibers, and asymmetric technological balances between the
State Administration Council (SAC / Tatmadaw / KaPaSa) and Myanmar Ethnic Armed Organizations (EAOs).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure UTF-8 output encoding on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from parla.core.knowledge_base import ParlaKnowledgeBase

DATA_FILE = PROJECT_ROOT / "Data" / "myanmar_arms_and_arsenals_2026.json"


def run_comparative_arsenal_analysis():
    print("=" * 85)
    print("⚔️ PARLA OPERATIONS RESEARCH: MYANMAR MILITARY ARSENAL & ASYMMETRY COMPARISON")
    print("=" * 85)

    kb = ParlaKnowledgeBase()

    # 1. Macro Summary
    macro = kb.get_arms_intel()
    print(f"\n[1] ARSENAL TELEMETRY OVERVIEW:")
    print(f"    • Total Weapons Systems Cataloged: {macro['total_weapons_tracked']}")
    print(f"    • Primary Factions Profiled: {', '.join(macro['factions_tracked'])}")
    print(f"    • Weapon Categories Tracked:")
    for cat, count in macro['weapons_by_category'].items():
        print(f"      - {cat:<15}: {count} systems")

    # 2. Side-by-Side Comparison: SAC vs. Three Brotherhood Alliance (3BA)
    print("\n" + "=" * 85)
    print("[2] COMPARATIVE ANALYSIS: SAC (Tatmadaw) vs. Three Brotherhood Alliance (3BA)")
    print("=" * 85)
    comp_3ba = kb.get_arms_intel("COMPARE:SAC:3BA")["data"]
    fa = comp_3ba["faction_a"]
    fb = comp_3ba["faction_b"]

    print(f"  Metric                      | {fa['id']:<30} | {fb['id']:<30}")
    print("  " + "-" * 80)
    print(f"  Inventory Tier              | {fa['tier']:<30} | {fb['tier']:<30}")
    print(f"  Estimated Manpower          | {fa['manpower'][:30]:<30} | {fb['manpower'][:30]:<30}")
    print(f"  Combat Air Superiority      | {fa['air_superiority']:<30} | {fb['air_superiority']:<30}")
    print(f"  Air Defense Umbrella        | {fa['air_defense']:<30} | {fb['air_defense']:<30}")
    print(f"  Tactical Drone Capability   | {fa['drone_rating']:<30} | {fb['drone_rating']:<30}")
    print(f"  Domestic Production         | {fa['domestic_capacity'][:30]:<30} | {fb['domestic_capacity'][:30]:<30}")
    print(f"  Tracked Weapons in Catalog  | {fa['weapons_cataloged_count']:<30} | {fb['weapons_cataloged_count']:<30}")
    print(f"\n  Asymmetric Dynamics:")
    print(f"    • Air Monopoly: {comp_3ba['asymmetric_dynamics']['air_superiority_monopoly']}")
    print(f"    • Tactical Drone Edge: {comp_3ba['asymmetric_dynamics']['drone_tactical_edge']}")
    print(f"    • Caliber Interoperability: {comp_3ba['asymmetric_dynamics']['caliber_capture_compatibility']}")

    # 3. Side-by-Side Comparison: SAC vs. Arakan Army (AA)
    print("\n" + "=" * 85)
    print("[3] COMPARATIVE ANALYSIS: SAC (Tatmadaw) vs. Arakan Army (AA)")
    print("=" * 85)
    comp_aa = kb.get_arms_intel("COMPARE:SAC:AA")["data"]
    faa = comp_aa["faction_b"]
    print(f"  • AA Force Posture: {faa['tier']}")
    print(f"  • Signature Weapons: {', '.join(faa['signature_weapons'])}")
    print(f"  • Air Defense Capability: {faa['air_defense']}")
    print(f"  • Tactical Drone Rating: {faa['drone_rating']}")

    # 4. Caliber Matching & Battlefield Ammunition Reusability
    print("\n" + "=" * 85)
    print("[4] CALIBER CROSS-MATCHING & REUSABILITY AUDIT:")
    print("=" * 85)
    
    calibers_to_test = ["5.56x45mm", "7.62x39mm", "122mm Rocket", "DRONE"]
    for c in calibers_to_test:
        if c == "DRONE":
            drones = kb.arms.list_weapons("DRONE")
            print(f"\n  • Category: DRONE WARFARE SYSTEMS ({len(drones)} tracked):")
            for d in drones:
                print(f"    - [{d.weapon_id}] {d.name} ({d.origin}) -> Range: {d.effective_range_km} km | Operators: {', '.join(d.primary_operators)}")
        else:
            matches = kb.get_arms_intel(f"CALIBER:{c}")["data"]
            print(f"\n  • Caliber: {c} ({len(matches)} systems):")
            for m in matches:
                print(f"    - [{m.weapon_id}] {m.name} ({m.origin}) -> Operators: {', '.join(m.primary_operators)}")

    # 5. Domestic Arms Manufacturing Comparison
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        ind = data.get("domestic_defence_industries", {})
        print("\n" + "=" * 85)
        print("[5] DOMESTIC DEFENCE INDUSTRIAL CAPABILITY COMPARISON:")
        print("=" * 85)
        for key, spec in ind.items():
            print(f"\n  🏭 {spec['name']} ({key}):")
            print(f"     • Active Facilities: {spec['total_active_factories']}")
            print(f"     • Primary Locations: {', '.join(spec['primary_locations'])}")
            print(f"     • Production Lines:")
            for pl in spec['core_production_lines']:
                print(f"       - {pl['series']} ({pl['caliber']}): {pl['type']}")
            print(f"     • Supply Vulnerabilities: {spec['supply_vulnerabilities']}")

    print("\n" + "=" * 85)
    print("✓ MILITARY ARSENAL & ASYMMETRY COMPARISON COMPLETE")
    print("=" * 85)


if __name__ == "__main__":
    run_comparative_arsenal_analysis()
