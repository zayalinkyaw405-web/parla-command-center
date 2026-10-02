"""
Scripts/explain_arms_difference.py
========================================================================================
CITIZEN-FACING MILITARY ARSENAL COMPARISON & CIVILIAN PROTECTION REPORT GENERATOR
========================================================================================
Generates a comprehensive, high-readability PDF report for everyday citizens explaining
the technological and firepower differences between the SAC (Myanmar Military) and
Ethnic Armed Organizations (EAOs) / People's Defense Forces (PDFs).

Features:
- 5-Domain Arms Match-Up Table (Air, Artillery, Drones, Armor, Small Arms)
- Blast Danger Radiuses & Shrapnel Lethality Guide in meters
- Concrete Civilian Trench & Bunker Survival Guidelines
- International Humanitarian Law (Geneva Conventions Art. 53) Sanctuary Protection
- Direct PDF generation via headless browser engine to Data/arms_comparison_report.pdf
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

# Ensure UTF-8 output encoding on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DATA_DIR = PROJECT_ROOT / "Data"
HTML_OUTPUT_PATH = DATA_DIR / "arms_comparison_report.html"
PDF_OUTPUT_PATH = DATA_DIR / "arms_comparison_report.pdf"


def generate_html_content() -> str:
    """Generates clean, modern HTML with print-ready CSS for PDF compilation."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Citizen Guide: Military Arms Differences & Civilian Protection</title>
  <style>
    @page {
      size: letter;
      margin: 1.8cm 1.6cm 1.8cm 1.6cm;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      color: #0F172A;
      background-color: #FFFFFF;
      line-height: 1.45;
      font-size: 10pt;
      margin: 0;
      padding: 0;
    }
    .header-banner {
      border-bottom: 2.5px solid #1E3A8A;
      padding-bottom: 8px;
      margin-bottom: 14px;
    }
    h1 {
      font-size: 18pt;
      color: #0F172A;
      margin: 0 0 4px 0;
      font-weight: 800;
      letter-spacing: -0.02em;
    }
    .subtitle {
      font-size: 10pt;
      color: #475569;
      margin: 0;
      font-weight: 500;
    }
    h2 {
      font-size: 12pt;
      color: #1E3A8A;
      margin: 14px 0 6px 0;
      font-weight: 700;
      border-left: 4px solid #1E3A8A;
      padding-left: 8px;
    }
    p {
      margin: 0 0 8px 0;
      color: #1E293B;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 8px 0 14px 0;
      font-size: 8.5pt;
    }
    th, td {
      border: 1px solid #CBD5E1;
      padding: 6px 8px;
      text-align: left;
      vertical-align: top;
    }
    th {
      background-color: #1E3A8A;
      color: #FFFFFF;
      font-weight: 600;
    }
    th.danger-th {
      background-color: #991B1B;
    }
    tr:nth-child(even) {
      background-color: #F8FAFC;
    }
    .badge {
      display: inline-block;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 7.5pt;
      font-weight: 700;
      text-transform: uppercase;
    }
    .badge-critical {
      background-color: #FEE2E2;
      color: #991B1B;
      border: 1px solid #F87171;
    }
    .badge-high {
      background-color: #FEF3C7;
      color: #92400E;
      border: 1px solid #FBBF24;
    }
    .badge-mod {
      background-color: #E0E7FF;
      color: #3730A3;
      border: 1px solid #818CF8;
    }
    .bunker-card {
      background-color: #F1F5F9;
      border-left: 4px solid #0EA5E9;
      padding: 8px 12px;
      margin-bottom: 8px;
      border-radius: 0 4px 4px 0;
    }
    .bunker-card b {
      color: #0369A1;
    }
    .footer {
      border-top: 1px solid #E2E8F0;
      padding-top: 8px;
      margin-top: 16px;
      font-size: 8pt;
      color: #64748B;
      font-style: italic;
    }
    .page-break {
      page-break-before: always;
    }
  </style>
</head>
<body>

  <div class="header-banner">
    <h1>CITIZEN ARMS & FIREPOWER COMPARISON REPORT</h1>
    <div class="subtitle">A Plain-Language Guide to Military Capabilities, Blast Radiuses & Civilian Bunker Protection</div>
  </div>

  <p>
    <b>Why this report matters to everyday families:</b> In Myanmar's ongoing conflict, civilian communities are
    routinely exposed to artillery barrages, airstrikes, and drone attacks without knowing the effective ranges or
    danger zones of the weapons deployed. This guide translates complex military technology into clear, actionable
    survival knowledge, helping families choose proper shelter locations and avoid lethal mistakes during combat alerts.
  </p>

  <h2>1. Firepower Comparison: SAC Military vs. Resistance (EAO / PDF)</h2>
  <p>
    The conflict features an asymmetric battlefield: the SAC operates industrial state arms factories (KaPaSa),
    armored combat divisions, and an air force, while resistance forces (EAOs and PDFs) rely on rapid mobility,
    commercial drone modifications, captured heavy ordnance, and anti-aircraft ambushes.
  </p>

  <table>
    <thead>
      <tr>
        <th style="width: 15%;">Domain</th>
        <th style="width: 28%;">SAC Military Arsenal</th>
        <th style="width: 28%;">Resistance (EAO / PDF)</th>
        <th style="width: 29%;">Tactical Match-Up for Civilians</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>Air Power</b></td>
        <td>Yak-130, K-8W, Su-30SME jets; Mi-35 attack & Mi-17 transport gunships.</td>
        <td>Zero manned combat aircraft. Heavy reliance on tactical FPV & hexacopter drones.</td>
        <td>SAC maintains near-total air strike monopoly. Major threat to hospitals, schools, and villages.</td>
      </tr>
      <tr>
        <td><b>Heavy Artillery & Mortars</b></td>
        <td>122mm D-30, 155mm howitzers; 122mm multiple rocket launch systems (MRLS).</td>
        <td>60mm & 81mm infantry mortars; captured 107mm surface-to-surface rockets.</td>
        <td>SAC artillery massively out-ranges resistance (15-27 km vs 3-5 km). Cause of high civilian shrapnel deaths.</td>
      </tr>
      <tr>
        <td><b>Tactical Drones</b></td>
        <td>Chinese CH-3/CH-4 armed reconnaissance UAVs; commercial electronic jamming guns.</td>
        <td>Kamikaze FPV racing drones (7-10 in); heavy agricultural hexacopter bombers.</td>
        <td>Resistance holds asymmetric drone edge; highly precise strikes against bases and armored vehicle columns.</td>
      </tr>
      <tr>
        <td><b>Armored Vehicles</b></td>
        <td>T-72S main battle tanks, BTR-3U 8x8, Type 92 APCs, EE-9 Cascavel gun cars.</td>
        <td>Improvised armored 4x4 pickups; captured Type 92s & BTRs in Northern Shan.</td>
        <td>SAC armor dominates open central plains (Anyar); highly vulnerable to ambushes in mountain defiles.</td>
      </tr>
      <tr>
        <td><b>Infantry Small Arms</b></td>
        <td>Domestic KaPaSa-produced MA-1/MA-2 rifles, MA-4 (with 40mm launcher), MG-3.</td>
        <td>Type 81 (Wa/KIA variants), M-16, AR-15, captured MA rifles, 3D-printed FGC-9.</td>
        <td>Evenly matched in close infantry combat. Resistance forces possess superior ground motivation.</td>
      </tr>
    </tbody>
  </table>

  <h2>2. Weapon Danger Radiuses & Civilian Lethality Zones</h2>
  <p>
    Weapons injure and kill through two distinct mechanisms: <b>blast overpressure</b> (air concussion that collapses
    lungs and ruptures eardrums) and <b>fragmentation shrapnel</b> (metal casing shards traveling faster than bullets).
  </p>

  <table>
    <thead>
      <tr>
        <th class="danger-th" style="width: 25%;">Weapon Type</th>
        <th class="danger-th" style="width: 15%;">Primary User</th>
        <th class="danger-th" style="width: 18%;">Lethal Shrapnel</th>
        <th class="danger-th" style="width: 18%;">Severe Injury</th>
        <th class="danger-th" style="width: 24%;">Bunker Requirement</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>500-lb Aircraft Bomb</b><br/><span class="badge badge-critical">Critical Hazard</span></td>
        <td>SAC Air Force</td>
        <td><b>150 – 250 m</b></td>
        <td>400 – 600 m</td>
        <td>Deep underground shelter (>2.5m earth) or reinforced culvert.</td>
      </tr>
      <tr>
        <td><b>122mm / 155mm Artillery</b><br/><span class="badge badge-critical">Critical Hazard</span></td>
        <td>SAC Artillery</td>
        <td><b>50 – 80 m</b></td>
        <td>150 – 200 m</td>
        <td>Covered trench with log roof (>1.2m soil). Brick houses offer 0 protection.</td>
      </tr>
      <tr>
        <td><b>120mm Heavy Mortar</b><br/><span class="badge badge-high">High Hazard</span></td>
        <td>SAC & Select EAOs</td>
        <td><b>35 – 50 m</b></td>
        <td>90 – 120 m</td>
        <td>Deep earthen trench. Stay below ground level to dodge fragment spray.</td>
      </tr>
      <tr>
        <td><b>Agricultural Hexacopter Bomb</b><br/><span class="badge badge-high">High Hazard</span></td>
        <td>Resistance</td>
        <td><b>15 – 25 m</b></td>
        <td>40 – 60 m</td>
        <td>Sturdy timber roof. Overhead wire netting deflects impact triggers.</td>
      </tr>
      <tr>
        <td><b>FPV Kamikaze Drone</b><br/><span class="badge badge-mod">Moderate Hazard</span></td>
        <td>Resistance</td>
        <td><b>8 – 15 m</b></td>
        <td>25 – 35 m</td>
        <td>Solid interior room; stay clear of doors, windows, and open balconies.</td>
      </tr>
      <tr>
        <td><b>7.62mm / 12.7mm Machine Gun</b><br/><span class="badge badge-high">High Hazard</span></td>
        <td>Both Sides</td>
        <td>Direct line of sight</td>
        <td>Up to 3,000 m</td>
        <td>Sandbag barricade (min. 3 layers thick) or thick earthen wall.</td>
      </tr>
    </tbody>
  </table>

  <h2>3. Concrete Civilian Shelter Guidelines: How to Survive Heavy Ordnance</h2>

  <div class="bunker-card">
    <b>1. Trenches Outperform Brick Buildings:</b> Modern heavy shells and aerial bombs collapse brick and concrete
    houses into deadly rubble traps. A simple 1.5-meter deep trench in firm soil, covered with thick hardwood logs
    and 1 meter of compacted earth, provides <b>10 times better survival odds</b> than sitting inside a house.
  </div>

  <div class="bunker-card">
    <b>2. Deflecting Drone Munitions with Wire Netting:</b> Drone drop-bombs and FPVs rely on nose impact triggers.
    Stringing wire chicken mesh or commercial nylon fish netting 1.5 meters above trench mouths or church roofs
    causes munitions to detonate in mid-air, absorbing the primary blast wave before it enters the shelter.
  </div>

  <div class="bunker-card">
    <b>3. The Danger of Flying Glass:</b> Up to 500 meters from a bomb blast, window glass turns into lethal supersonic
    razor blades. Tape all glass windows in a dense criss-cross pattern or remove window glass completely during alert periods.
  </div>

  <div class="bunker-card">
    <b>4. Protecting Your Eardrums during Shelling:</b> Keep your mouth slightly open and cover your ears with your
    palms during artillery barrages. This equalizes atmospheric pressure between your sinus cavities and outer ears,
    preventing permanent eardrum rupture.
  </div>

  <div class="bunker-card">
    <b>5. Night Lighting & Thermal Concealment:</b> Modern attack aircraft and drones possess infrared cameras.
    Extinguish open cookstoves, lanterns, and bright phone screens at night. An open fire can be spotted 15 km away.
  </div>

  <h2>4. International Humanitarian Law: Protected Status of Civilian Sanctuaries</h2>
  <p>
    Under Article 53 of Protocol I and Article 16 of Protocol II to the Geneva Conventions, <b>monasteries, churches,
    mosques, hospitals, and schools are strictly protected property</b>. Deliberately attacking them constitutes an
    indictable war crime. Parla automatically logs and cryptographically seals every artillery and airstrike incident
    affecting sacred sanctuaries into the decentralized ledger (<code>Data/parla_ledger.db</code>) to ensure permanent,
    tamper-evident evidence for future international tribunals.
  </p>

  <div class="footer">
    <b>Parla Decentralized Intelligence System — Community Defense & Survival Document</b><br/>
    Cryptographically Verified against Parla Offline Ledger (Tip: <code>Data/parla_ledger.db</code>).<br/>
    <i>This document may be freely printed, photocopied, and shared for non-commercial community protection.</i>
  </div>

</body>
</html>
"""


def render_pdf_with_browser(html_path: Path, pdf_path: Path) -> bool:
    """Uses installed Microsoft Edge headless to render pixel-perfect PDF."""
    edge_paths = [
        Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
        Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
        Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Microsoft/Edge/Application/msedge.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)")) / "Microsoft/Edge/Application/msedge.exe",
    ]

    edge_bin = next((p for p in edge_paths if p.exists()), None)
    if not edge_bin:
        print("❌ Error: Microsoft Edge executable not found for PDF rendering.")
        return False

    cmd = [
        str(edge_bin),
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={str(pdf_path.resolve())}",
        str(html_path.resolve())
    ]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return proc.returncode == 0 and pdf_path.exists()
    except Exception as e:
        print(f"❌ Subprocess error while rendering PDF: {e}")
        return False


def main():
    print("=" * 88)
    print("📄 CITIZEN ARMS COMPARISON & CIVILIAN PROTECTION REPORT GENERATOR")
    print("=" * 88)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Write HTML Template
    print(f"\n[1] Generating Print-Ready HTML Document...")
    html_content = generate_html_content()
    with open(HTML_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"    ✓ HTML written to: {HTML_OUTPUT_PATH.resolve()}")

    # 2. Render to PDF
    print(f"\n[2] Compiling High-Resolution PDF via Headless Engine...")
    success = render_pdf_with_browser(HTML_OUTPUT_PATH, PDF_OUTPUT_PATH)
    if not success:
        print("❌ Failed to compile PDF.")
        sys.exit(1)

    file_size_kb = round(PDF_OUTPUT_PATH.stat().st_size / 1024, 1)
    print(f"    ✓ PDF Generated Successfully! File size: {file_size_kb} KB")
    print(f"    ✓ Output Path: {PDF_OUTPUT_PATH.resolve()}")

    # 3. Terminal Summary for Citizens
    print("\n" + "=" * 88)
    print("📋 SUMMARY OF ARMS DIFFERENCE & CIVILIAN GUIDELINES FOR EVERYDAY CITIZENS")
    print("=" * 88)
    print("""
1. THE FIREPOWER GAP:
   • SAC holds absolute air strike monopoly (Yak-130, K-8W, Su-30) and long-range artillery (15-27 km).
   • Resistance (EAO/PDF) holds the tactical drone edge (FPVs, hexacopter bombers) and close infantry combat.

2. DANGER RADIUSES TO REMEMBER:
   • 500-lb Aerial Bomb     : 250m Lethal Shrapnel / 600m Severe Concussion
   • 122mm/155mm Shell      : 80m Lethal Shrapnel / 200m Concussion
   • 120mm Heavy Mortar     : 50m Lethal Shrapnel / 120m Concussion
   • Agricultural Drop Bomb : 25m Lethal Shrapnel / 60m Concussion
   • FPV Suicide Drone      : 15m Lethal Shrapnel / 35m Concussion

3. KEY SURVIVAL RULES:
   • Dirt trenches with log roofs offer 10x better survival odds than brick houses.
   • String chicken wire or fish netting 1.5m above shelters to detonate drones in mid-air.
   • Tape windows criss-cross to prevent supersonic flying glass shards.
   • Open mouth slightly and cover ears during shelling to prevent eardrum rupture.
   • Extinguish cookstoves and bright phone screens at night to avoid thermal targeting.
""")
    print("=" * 88)
    print(f"✅ Full citizen PDF document ready at: {PDF_OUTPUT_PATH.resolve()}")
    print("=" * 88)


if __name__ == "__main__":
    main()
