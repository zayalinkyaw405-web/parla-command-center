"""
Scripts/generate_prospect_leads.py
===================================
Generates structured target lead directories and customized outbound messaging packages
for Maritime Bunkering (Singapore), Border Supply Chain (Thailand), and Legal/ESG Compliance (London/Geneva).
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTBOUND_DIR = PROJECT_ROOT / "Project" / "outbound_prospects"
OUTBOUND_DIR.mkdir(parents=True, exist_ok=True)

TARGET_CAMPAIGNS = [
    {
        "segment_id": "SEG-MARITIME-SG",
        "industry": "Maritime Bunkering & Vessel Logistics",
        "geography": "Singapore / Malacca Strait Corridor",
        "value_proposition": "Dark Fleet & Jet Fuel Transshipment Screening against OFAC / EU Secondary Sanctions",
        "target_companies": [
            {"company": "Singamas Petroleum Trading", "role": "Compliance Director", "channel": "LinkedIn / Email"},
            {"company": "Chemoil International Pte Ltd", "role": "Head of Maritime Risk", "channel": "Corporate Email"},
            {"company": "Fratelli Cosulich Unipessodal", "role": "Bunker Trading Risk Officer", "channel": "LinkedIn"},
            {"company": "Equatorial Marine Fuel Management", "role": "Legal & Regulatory Counsel", "channel": "Email"},
            {"company": "BMT Asia Pacific Singapore", "role": "Senior Maritime Risk Analyst", "channel": "LinkedIn"}
        ],
        "email_subject": "Urgent Sanctions & Supply-Chain Alert: Maritime Trade & Bunkering Compliance (Singapore)",
        "price_anchor": "$75 USD Single PDF / $199 USD Monthly API"
    },
    {
        "segment_id": "SEG-SUPPLY-CHAIN-TH",
        "industry": "Cross-Border Logistics & Infrastructure",
        "geography": "Thailand-Myanmar Trade Corridors (Mae Sot / Ranong / Kanchanaburi)",
        "value_proposition": "Dual-Use Equipment & Mineral/Timber Sanctions Evasion Detection",
        "target_companies": [
            {"company": "Kerry Logistics (Thailand)", "role": "Cross-Border Compliance Lead", "channel": "Email"},
            {"company": "SCG Logistics Management", "role": "Supply Chain ESG Auditor", "channel": "LinkedIn"},
            {"company": "WHA Corporation PCL", "role": "Industrial Estate Risk Lead", "channel": "Corporate Email"},
            {"company": "NIPPON EXPRESS (Thailand)", "role": "Trade Compliance Manager", "channel": "LinkedIn"}
        ],
        "email_subject": "Cross-Border Logistics Alert: Dual-Use Sanctions Risk Screening (Thailand-Myanmar)",
        "price_anchor": "$75 USD Single PDF / $199 USD Monthly API"
    },
    {
        "segment_id": "SEG-LEGAL-ESG-UK",
        "industry": "International Human Rights Litigation & ESG Due Diligence",
        "geography": "London / Geneva / The Hague",
        "value_proposition": "Forensic ICC/IIMM Admissible Evidence & Chain-of-Custody Command Verification",
        "target_companies": [
            {"company": "Leigh Day Solicitors", "role": "Partner - International Human Rights & ESG", "channel": "Email"},
            {"company": "Matrix Chambers", "role": "Public International Law Counsel", "channel": "LinkedIn"},
            {"company": "Global Witness", "role": "Senior Conflict Resources Investigator", "channel": "Email / Signal"},
            {"company": "Doughty Street Chambers", "role": "International Sanctions & Accountability Specialist", "channel": "LinkedIn"}
        ],
        "email_subject": "Forensic Sanctions & Command Accountability Dossiers (ICC/IIMM Admissible)",
        "price_anchor": "$75 USD Single PDF / $199 USD Monthly API"
    }
]

def main():
    print("=" * 80)
    print("      PARLA OUTBOUND PROSPECT & TARGET LEAD DIRECTORY GENERATOR")
    print("=" * 80)
    
    summary_file = OUTBOUND_DIR / "TARGET_LEADS_CAMPAIGN_MANIFEST.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(TARGET_CAMPAIGNS, f, indent=2)
        
    print(f" [*] Generated Campaign Manifest: {summary_file}")
    for camp in TARGET_CAMPAIGNS:
        print(f"\n [+] Campaign: {camp['segment_id']} ({camp['industry']})")
        print(f"     Targeting: {len(camp['target_companies'])} High-Value Entities")
        for company in camp['target_companies']:
            print(f"     - {company['company']} | {company['role']} ({company['channel']})")

    print("\n" + "=" * 80)
    print(" [PASS] Outbound Lead Directory Generation Complete.")

if __name__ == "__main__":
    main()
