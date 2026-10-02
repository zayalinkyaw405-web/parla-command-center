"""
Scripts/explain_parla_for_citizens.py
========================================================================================
PARLA CITIZEN BRIEFING: A CLEAR & ACCESSIBLE GUIDE FOR EVERYDAY PEOPLE
========================================================================================
Explains what Parla is, how it protects villages and families, how the Five Pillars
(Yin, Yang, Chaos, Void, Harmony) work in plain language, how your privacy is guarded,
and how to respond to early warnings during conflict, blackouts, and natural disasters.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Ensure UTF-8 output encoding on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from parla.core.knowledge_base import ParlaKnowledgeBase


def print_banner():
    print("""
========================================================================================
   🛡️  PARLA COMMUNITY GUARDIAN: CITIZEN DEFENSE & SURVIVAL BRIEFING  🛡️
========================================================================================
    A simple, honest explanation for families, elders, youth, and village defense
    volunteers about how Parla watches over communities without risking their safety.
========================================================================================
""")


def section_1_what_is_parla():
    print("""
----------------------------------------------------------------------------------------
📌 1. WHAT IS PARLA IN SIMPLE WORDS?
----------------------------------------------------------------------------------------
Parla is a decentralized, offline community warning system created to protect civilian
lives across war-affected and disaster-prone regions.

Think of Parla as the **"Watchful Ears and Sharp Mind of the Village"**:
• It does NOT need an internet connection or cellular signal to protect you.
• It runs on tiny, low-power solar batteries hidden in trees, roofs, or communal buildings.
• It listens to the sky for incoming military jet fighters, transport helicopters,
  heavy artillery fire, and approaching floodwaters.
• When danger is coming, it sounds local sirens and sends silent mesh alerts to
  community phones, giving families 60 to 180 precious seconds to reach bomb shelters.
""")


def section_2_the_five_pillars():
    print("""
----------------------------------------------------------------------------------------
🏛️ 2. HOW PARLA WORKS: THE FIVE PILLARS EXPLAINED
----------------------------------------------------------------------------------------
Parla is built upon five complementary principles working together:

1. 👂 YIN (The Quiet Ears - Receptive Listening)
   • Parla's sensors sit silently in the background like a watchful guardian.
   • It never broadcasts loud radio signals that hostile forces can track with direction
     finders. It only listens—capturing the high-pitch compressor whine of jet engines,
     the deep rumble of diesel artillery trucks, or the sound of rising river water.

2. 🧠 YANG (The Sharp Mind - Active Intelligence)
   • A motorcycle engine sounds different from an attack drone.
   • Thunder sounds different from a 120mm artillery shell.
   • Parla's mathematical brain instantly separates everyday village sounds from
     military strike aircraft (like the Yak-130 jet or Mi-35 attack helicopter),
     so people only run to bomb shelters when danger is truly real.

3. 🌪️ CHAOS (The Harsh Reality - Real-World Resilience)
   • In conflict zones, communication lines get severed, power grids fail, roads turn
     to mud, and bombs fall without notice.
   • Parla was born in chaos. It never assumes the world is peaceful or that the internet
     works. It is engineered to keep running even if 80% of communication towers are down.

4. 🌌 VOID (The Shield of Silence - The Null Space & Stealth)
   • **The Anomaly of Silence**: Military commanders often order total radio silence
     10 to 20 minutes before launching an airstrike. Parla alerts you when sudden
     silence happens ("the dog that didn't bark").
   • **Anti-Forensic Self-Defense**: If hostile forces raid a village and grab a Parla box,
     the box senses that its lid was opened and **vaporizes its own memory in 12 milliseconds**.
     They find only a dead plastic brick with ZERO names, ZERO maps, and ZERO history.
   • **Blackout Memory**: When the internet is completely cut, Parla stores reports in a
     safe memory pocket until a trusted traveler or motorcycle rider can carry the data out.

5. ⚖️ HARMONY (Truth, Protection & Justice - The Ledger)
   • Parla records every airstrike, church bombing, monastery attack, and flood event
     into an unchangeable cryptographic ledger (like stone carvings that cannot be erased).
   • Aggressors cannot claim "we never bombed that school" because the digital signature
     of the attack is permanently sealed for future international human rights accountability.
""")


def section_3_privacy_and_safety():
    print("""
----------------------------------------------------------------------------------------
🔒 3. WILL PARLA PUT ME OR MY FAMILY IN DANGER?
----------------------------------------------------------------------------------------
**NO. Parla is built with "Zero-Trust Privacy" from the ground up.**

Here is our strict promise to every citizen:
1. 📍 **NO EXACT LOCATIONS**: Your home or trench is never pinpointed. All locations
   are blurred into a wide 1.1-kilometer grid box. Even if someone intercepts the data,
   they cannot aim artillery at your specific house.
2. 👤 **NO NAMES OR PHONE NUMBERS**: Parla's system automatically erases the names of
   pastors, monks, nuns, village heads, and doctors before anything is saved.
3. 📵 **NO TRACKING OF CIVILIANS**: Parla does not read private text messages, photos,
   or phone contacts. It only analyzes acoustic waves in the air and weather pressure.
""")


def section_4_responding_to_alerts():
    print("""
----------------------------------------------------------------------------------------
🚨 4. WHAT SHOULD CITIZENS DO WHEN AN ALERT SOUNDS?
----------------------------------------------------------------------------------------
When your village siren sounds or your offline mobile app shows an alert:

• 🔴 **RED ALERT: AIRSTRIKE / JET INBOUND**
  - **Time to impact**: 60 to 180 seconds.
  - **Action**: Immediately move family into earthen trenches or covered bunkers.
  - **Do NOT**: Run into open fields, stand on roads, or record video with your phone.
  - **Do NOT**: Gather near tall towers, telecom antennas, or military vehicles.

• 🟡 **YELLOW ALERT: ARTILLERY / DRONE PROXIMITY**
  - **Action**: Stay low to the ground. Get under sturdy timber shelters or trench mouths.
  - Extinguish open cookstoves and torches at night to avoid thermal heat targeting.

• 🔵 **BLUE ALERT: MONSOON FLASH FLOOD / LANDSLIDE**
  - **Action**: Evacuate low-lying riverbanks and steep mining slopes.
  - Move livestock and essential rice sacks to higher ground.

• ⚪ **VOID ALERT: ABNORMAL EMISSIONS SILENCE**
  - **Action**: Heightened vigilance. Send sentries to perimeter; prepare bunker paths.
""")


def section_5_interactive_simulation():
    print("""
----------------------------------------------------------------------------------------
🎬 5. LIVE CITIZEN PERSPECTIVE SIMULATION
----------------------------------------------------------------------------------------
Here is what happens during a real 90-second event in an offline village:
""")

    steps = [
        ("00:00", "👂 [YIN]", "Acoustic sensor hidden in tree detects 2,400 Hz compressor tone 14 km away."),
        ("00:05", "🧠 [YANG]", "Neural model identifies: Yak-130 light attack jet flying at 680 km/h toward sector."),
        ("00:10", "🚨 [ALERT]", "Local siren triggers. Signal hops across village LoRa mesh radios to citizen phones."),
        ("00:15", "🏃 [ACTION]", "Villagers take shelter in pre-dug reinforced trenches. School children dispersed."),
        ("00:45", "🌪️ [CHAOS]", "Jet releases unguided bombs 800m north. Cellular tower knocked out by blast concussion."),
        ("00:50", "🌌 [VOID]", "No cellular signal. Node enters VOID mode; buffers strike telemetry into offline memory."),
        ("01:30", "🕊️ [HARMONY]", "Jet departs. Local medics deploy. Data sealed into tamper-proof ledger for humanitarian aid.")
    ]

    for timestamp, pillar, desc in steps:
        time.sleep(0.2)
        print(f"  [{timestamp}] {pillar:<12} : {desc}")

    print("\n✓ Simulation Complete: Parla protected lives without internet, and recorded the truth.")


def section_6_faith_and_unity():
    print("""
----------------------------------------------------------------------------------------
🤝 6. PROTECTING ALL COMMUNITIES, PLACES OF WORSHIP & SANCTUARIES
----------------------------------------------------------------------------------------
Parla stands with all ordinary citizens regardless of background or religious faith:
• **Monasteries, Churches, Mosques & Temples** are recognized as sacred humanitarian
  sanctuaries under International Humanitarian Law (Geneva Conventions Art. 53).
• When sacred shelters are attacked or desecrated, Parla documents the incident with
  immutable cryptographic timestamps so perpetrators will be held accountable.
• In the face of division and hate propaganda, Parla honors the universal spirit of
  compassion, human dignity, and mutual protection that unites our communities.
""")


def main():
    print_banner()
    section_1_what_is_parla()
    section_2_the_five_pillars()
    section_3_privacy_and_safety()
    section_4_responding_to_alerts()
    section_5_interactive_simulation()
    section_6_faith_and_unity()

    kb = ParlaKnowledgeBase()
    macro = kb.get_void_intel()

    print("=" * 88)
    print(f"📊 SYSTEM STATUS: Parla is active across {macro['active_telecom_blackout_zones']} blackout regions.")
    print("   Remember: You are not alone. When voices are silenced, Parla keeps the vigil.")
    print("========================================================================================")


if __name__ == "__main__":
    main()
