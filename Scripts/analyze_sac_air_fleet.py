"""
Scripts/analyze_sac_air_fleet.py
Performs comprehensive operational research and acoustic early-warning analysis
on the State Administration Council (SAC / Myanmar Air Force) aircraft fleet.
Evaluates fleet composition, airbase coverage, acoustic sensor warning windows,
and documented shoot-down attrition.
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

DATA_FILE = PROJECT_ROOT / "Data" / "sac_aircraft_fleet_2026.json"


def run_fleet_analysis():
    print("=" * 85)
    print("✈️ PARLA AIR DEFENSE INTELLIGENCE: SAC (MYANMAR AIR FORCE) FLEET AUDIT")
    print("=" * 85)

    kb = ParlaKnowledgeBase()

    # 1. Macro Fleet Summary
    macro = kb.get_aircraft_intel()
    print(f"\n[1] SAC ACTIVE FLEET OVERVIEW:")
    print(f"    • Total Estimated Active Aircraft : {macro['active_fleet_estimate']} airframes")
    print(f"    • Documented Combat Losses        : {macro['documented_losses']} airframes")
    print(f"    • Aircraft Models Profiled        : {macro['models_tracked']} models")
    print(f"    • Operational Airbases Tracked    : {macro['airbases_tracked']} bases")
    print(f"    • Fleet Composition by Category:")
    for cat, count in macro['fleet_by_category'].items():
        print(f"      - {cat:<28}: {count:>3} airframes")

    # 2. Detailed Model Breakdown
    print("\n" + "=" * 85)
    print("[2] SAC COMBAT & SUPPORT AIRCRAFT DETAILED INVENTORY:")
    print("=" * 85)
    print(f"  {'Model':<12} | {'Common Name':<34} | {'Origin':<14} | {'Active':<6} | {'Max Spd':<10} | {'Combat Radius'}")
    print("  " + "-" * 83)
    for model in kb.sac_air.list_aircraft():
        print(f"  {model.model_id:<12} | {model.common_name[:34]:<34} | {model.origin_country[:14]:<14} | {model.active_fleet_count:>6} | {int(model.max_speed_kmh):>6} km/h | {int(model.combat_radius_km):>5} km")

    # 3. Acoustic Early-Warning Window Simulation
    print("\n" + "=" * 85)
    print("[3] ACOUSTIC SENSOR DETECTION & CIVILIAN WARNING WINDOW SIMULATION:")
    print("=" * 85)
    
    test_distances = [12.0, 8.0, 5.0]  # km from civilian settlement
    sample_threats = ["SU-30SME", "YAK-130", "FTC-2000G", "K-8W", "MI-35P", "MI-17"]

    print(f"  Civilian Shelter Evacuation Time (Seconds) from Edge Sensor Ingress Detection:")
    print(f"  {'Threat Model':<14} | {'12 km Distance':<16} | {'8 km Distance':<16} | {'5 km Distance':<16}")
    print("  " + "-" * 75)
    for model_id in sample_threats:
        t12 = kb.sac_air.calculate_warning_time_seconds(model_id, 12.0)
        t8 = kb.sac_air.calculate_warning_time_seconds(model_id, 8.0)
        t5 = kb.sac_air.calculate_warning_time_seconds(model_id, 5.0)
        print(f"  {model_id:<14} | {t12:>5.1f} s ({t12/60:>3.1f}m)   | {t8:>5.1f} s ({t8/60:>3.1f}m)   | {t5:>5.1f} s ({t5/60:>3.1f}m)")

    # 4. Live Acoustic Spectrum Correlation Test
    print("\n" + "=" * 85)
    print("[4] REAL-TIME ACOUSTIC TELEMETRY CORRELATION TEST:")
    print("=" * 85)
    test_signals = [
        {"name": "Heavy Rotary Rotor Slap", "freq": 20.5, "db": 94.0, "doppler": 25.0},
        {"name": "Transonic Turbofan Dive", "freq": 3200.0, "db": 128.0, "doppler": 220.0},
        {"name": "Single Turbojet Screech", "freq": 650.0, "db": 115.0, "doppler": 180.0}
    ]

    for sig in test_signals:
        result = kb.get_aircraft_intel(f"ACOUSTIC:{sig['freq']}:{sig['db']}:{sig['doppler']}")
        matches = result.get("matches", [])
        print(f"\n  📡 Signal Input: [{sig['name']}] Freq={sig['freq']} Hz, dB={sig['db']}, Doppler={sig['doppler']} Hz")
        if matches:
            for m_id, conf in matches[:3]:
                ac = kb.sac_air.get_aircraft(m_id)
                print(f"     ✓ Candidate: {m_id:<12} ({ac.common_name[:32]}) -> Confidence: {conf*100:.1f}%")
        else:
            print("     ❌ No confident aircraft match.")

    # 5. Strategic Airbase Network & Assigned Squadrons
    print("\n" + "=" * 85)
    print("[5] MAJOR SAC AIRBASES & STRATEGIC COMBAT REACH:")
    print("=" * 85)
    for base in kb.sac_air.list_airbases():
        print(f"\n  📍 {base.name} ({base.base_id}) - {base.region_state}:")
        print(f"     • Coordinates: Lat {base.coordinates[0]:.3f}, Lon {base.coordinates[1]:.3f}")
        print(f"     • Primary Assigned Fleet: {', '.join(base.assigned_aircraft)}")
        print(f"     • Strategic Strike Coverage: {', '.join(base.strategic_strike_coverage)}")
        print(f"     • Fortification: {base.fortification_status[:80]}...")

    # 6. Verified Shoot-Down Attrition Registry
    print("\n" + "=" * 85)
    print("[6] DOCUMENTED COMBAT SHOOT-DOWNS & ATTRITION TELEMETRY (2023-2026):")
    print("=" * 85)
    for record in kb.sac_air.list_attrition():
        print(f"\n  💥 [{record.date}] {record.aircraft_type} ({record.tail_or_serial or 'Unknown Serial'}):")
        print(f"     • Crash Location : {record.location_sector} ({record.state_region})")
        print(f"     • Weapon Used    : {record.weapon_employed}")
        print(f"     • Downed By      : {record.downing_actor}")
        print(f"     • Significance   : {record.tactical_significance}")

    print("\n" + "=" * 85)
    print("✓ SAC AIRCRAFT FLEET & ACOUSTIC TELEMETRY AUDIT COMPLETE")
    print("=" * 85)


if __name__ == "__main__":
    run_fleet_analysis()
