"""
Scripts/find_suitable_clients.py
================================
Expands and categorizes target client directories across 4 high-value risk compliance sectors:
1. Maritime Fuel Traders & Vessel Operators (Singapore / Hong Kong / Dubai)
2. Cross-Border Logistics & Commodity Traders (Thailand / Myanmar Corridors)
3. International Legal Counsel & ESG Litigation Chambers (London / Geneva / DC)
4. Geopolitical Risk Consultancies & Sanctions Audit Firms (Global)
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLIENT_DIRECTORY_FILE = PROJECT_ROOT / "Project" / "outbound_prospects" / "TARGET_CLIENT_DIRECTORY.json"
MARKDOWN_DIRECTORY_FILE = PROJECT_ROOT / "Project" / "outbound_prospects" / "TARGET_CLIENT_DIRECTORY.md"

LIVE_URL = "https://fog-coastal-talk-duck.trycloudflare.com"

CLIENT_SECTORS = [
    {
        "sector_id": "SEC-01",
        "sector_name": "Maritime Bunkering & Vessel Fleet Operators",
        "geography": "Singapore / Malacca Strait / Hong Kong / Dubai",
        "target_roles": ["Head of Maritime Sanctions Compliance", "Bunker Risk Manager", "Legal & Claims Director"],
        "primary_trigger": "Dark fleet STS transfers, jet fuel supply chain exposure under EU/OFAC maritime advisories.",
        "clients": [
            {"company": "Singamas Petroleum Trading Pte Ltd", "country": "Singapore", "contact_target": "Compliance Director", "channel": "LinkedIn / Corporate Email"},
            {"company": "Chemoil International Pte Ltd", "country": "Singapore", "contact_target": "Head of Maritime Risk", "channel": "LinkedIn / Corporate Email"},
            {"company": "Fratelli Cosulich Unipessodal", "country": "Singapore", "contact_target": "Bunker Trading Risk Officer", "channel": "LinkedIn / Corporate Email"},
            {"company": "Equatorial Marine Fuel Management", "country": "Singapore", "contact_target": "Legal & Regulatory Counsel", "channel": "Corporate Email"},
            {"company": "BMT Asia Pacific", "country": "Singapore", "contact_target": "Senior Maritime Risk Analyst", "channel": "LinkedIn"},
            {"company": "Torm A/S Singapore Branch", "country": "Singapore / Denmark", "contact_target": "Vessel Sanctions Officer", "channel": "Corporate Email"},
            {"company": "Bunker Holding A/S", "country": "Denmark / Global", "contact_target": "Group Chief Compliance Officer", "channel": "LinkedIn / Email"}
        ]
    },
    {
        "sector_id": "SEC-02",
        "sector_name": "Cross-Border Logistics & Industrial Conglomerates",
        "geography": "Thailand / Myanmar Corridors (Mae Sot, Ranong, Bangkok)",
        "target_roles": ["Supply Chain ESG Auditor", "Trade Compliance Lead", "Customs & Logistics Director"],
        "primary_trigger": "Dual-use aviation equipment, timber/mineral revenue diversion, and SAC enterprise ownership checks.",
        "clients": [
            {"company": "Kerry Logistics (Thailand) PCL", "country": "Thailand", "contact_target": "Cross-Border Compliance Manager", "channel": "Corporate Email"},
            {"company": "SCG Logistics Management Co., Ltd.", "country": "Thailand", "contact_target": "Supply Chain Risk Officer", "channel": "LinkedIn"},
            {"company": "WHA Corporation PCL", "country": "Thailand", "contact_target": "Industrial Estate ESG Auditor", "channel": "Corporate Email"},
            {"company": "Nippon Express (Thailand) Co., Ltd.", "country": "Thailand / Japan", "contact_target": "Trade Compliance Lead", "channel": "LinkedIn"},
            {"company": "JWD InfoLogistics PCL", "country": "Thailand", "contact_target": "Regional Trade Risk Lead", "channel": "Corporate Email"}
        ]
    },
    {
        "sector_id": "SEC-03",
        "sector_name": "International Human Rights Law & ESG Chambers",
        "geography": "London / Geneva / The Hague / Washington DC",
        "target_roles": ["Partner - International Sanctions", "Public International Law Counsel", "Senior ESG Investigator"],
        "primary_trigger": "Requirement for SHA-256 Merkle notarized evidence, biometric verification, and ICC/IIMM chain of custody.",
        "clients": [
            {"company": "Leigh Day Solicitors", "country": "UK", "contact_target": "Partner - International Claims", "channel": "Email / Direct Mail"},
            {"company": "Matrix Chambers", "country": "UK", "contact_target": "Public International Law Counsel", "channel": "LinkedIn / Chambers Directory"},
            {"company": "Global Witness", "country": "UK / Switzerland", "contact_target": "Senior Conflict Resources Investigator", "channel": "Encrypted Email / Signal"},
            {"company": "Doughty Street Chambers", "country": "UK", "contact_target": "Sanctions & Accountability Specialist", "channel": "LinkedIn / Chambers Directory"},
            {"company": "Dechert LLP (ESG & Sanctions Unit)", "country": "UK / US", "contact_target": "International Trade Partner", "channel": "Corporate Email"}
        ]
    },
    {
        "sector_id": "SEC-04",
        "sector_name": "Geopolitical Risk & Sanctions Consultancies",
        "geography": "Global (London, Washington DC, Singapore)",
        "target_roles": ["Senior Director - APAC Intelligence", "Sanctions Advisory Lead", "Corporate Intelligence Partner"],
        "primary_trigger": "Sub-second API access ($199/mo) for automated PEP, military command structure, and entity screening.",
        "clients": [
            {"company": "Control Risks Group", "country": "Global / Singapore", "contact_target": "Head of APAC Due Diligence", "channel": "LinkedIn"},
            {"company": "The Risk Advisory Group", "country": "UK / Singapore", "contact_target": "Sanctions Practice Lead", "channel": "Corporate Email"},
            {"company": "Eurasia Group", "country": "US / Global", "contact_target": "Southeast Asia Director", "channel": "LinkedIn / Corporate Email"},
            {"company": "Kroll (Compliance Risk Unit)", "country": "Global / Singapore", "contact_target": "Managing Director - Business Intelligence", "channel": "LinkedIn / Corporate Email"}
        ]
    }
]

def generate_markdown():
    doc = f"""# 🎯 Suitable Client Directory & Sales Outreach Strategy

**Generated:** 2026  
**Live Access Portal:** [{LIVE_URL}]({LIVE_URL})  
**Target Revenue Range:** $75.00 USD (Single Certified Dossier) — $199.00 USD/month (API Subscription)

---

"""
    for sec in CLIENT_SECTORS:
        doc += f"## {sec['sector_id']}: {sec['sector_name']}\n"
        doc += f"- **Geography:** {sec['geography']}\n"
        doc += f"- **Primary Pitch Trigger:** {sec['primary_trigger']}\n\n"
        doc += "| Company | Country | Target Role | Outreach Channel |\n"
        doc += "| :--- | :--- | :--- | :--- |\n"
        for c in sec['clients']:
            doc += f"| **{c['company']}** | {c['country']} | {c['contact_target']} | {c['channel']} |\n"
        doc += "\n---\n\n"

    return doc

def main():
    print("=" * 80)
    print("      COMPILING TARGET CLIENT DIRECTORY FOR B2B MONETIZATION")
    print("=" * 80)

    # Save JSON manifest
    with open(CLIENT_DIRECTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(CLIENT_SECTORS, f, indent=2)
    print(f" [+] Created JSON Manifest: {CLIENT_DIRECTORY_FILE.relative_to(PROJECT_ROOT)}")

    # Save Markdown directory
    md_content = generate_markdown()
    with open(MARKDOWN_DIRECTORY_FILE, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f" [+] Created Markdown Guide: {MARKDOWN_DIRECTORY_FILE.relative_to(PROJECT_ROOT)}")

    total_clients = sum(len(s['clients']) for s in CLIENT_SECTORS)
    print("=" * 80)
    print(f" [PASS] 21 High-Probability Client Targets Compiled Across {len(CLIENT_SECTORS)} Sectors.")

if __name__ == "__main__":
    main()
