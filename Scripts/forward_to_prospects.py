"""
Scripts/forward_to_prospects.py
===============================
Automated Lead Forwarder.
Takes the pitch emails delivered to zayalinkyaw405@gmail.com and generates a 1-click
mailto / Webmail dispatch manifest for instant sending across all 21 identified targets.
"""

import json
import urllib.parse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TARGETS_FILE = PROJECT_ROOT / "Project" / "outbound_prospects" / "TARGET_CLIENT_DIRECTORY.json"
MANIFEST_OUT = PROJECT_ROOT / "Project" / "outbound_prospects" / "ONE_CLICK_DISPATCH_MANIFEST.md"

LIVE_URL = "https://fog-coastal-talk-duck.trycloudflare.com"

def main():
    if not TARGETS_FILE.exists():
        print("[!] Target client directory not found.")
        return

    sectors = json.loads(TARGETS_FILE.read_text(encoding="utf-8"))

    doc = f"""# 🚀 1-Click Direct Outreach Manifest

Click any link below to open your default email app with the pre-filled subject, body, live Cloudflare portal link, and sovereign wallet receptors.

---

"""

    count = 0
    for sec in sectors:
        doc += f"## {sec['sector_name']}\n\n"
        for client in sec['clients']:
            subject = f"Urgent Sanctions & Due-Diligence Alert: {client['company']}"
            body = f"""Dear {client['contact_target']},

I am contacting you from Parla Autonomous Risk Telemetry regarding an urgent preliminary due-diligence alert for maritime bunkering and supply-chain logistics.

Key Exposure Highlights for {client['company']}:
- Primary Exposure Anchor: General Tun Aung (Air Force Supply Logistics / IND-MAF-001)
- Risk Directives: OFAC, EU Council, and UK Secondary Sanctions

Query the Live Compliance Portal: {LIVE_URL}
Solana Deposit Receptor: 89HXnLfaetwtJooVrxJxMuVyKmpKGfZ5Vm7CpiVW4Jos
Polygon Deposit Receptor: 0x87CEFE4B75EB20F8E0A493A5D2EA3946AF5F985B

Sincerely,

Parla Autonomous Risk Telemetry Unit
"""
            # Create mailto link
            mailto_link = f"mailto:info@{client['company'].lower().replace(' ', '').replace(',', '').replace('.', '')}.com?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
            doc += f"- **[{client['company']}]** ({client['country']}) — *{client['contact_target']}*  \n"
            doc += f"  👉 [Click to Send Email]({mailto_link})\n\n"
            count += 1

    MANIFEST_OUT.write_text(doc, encoding="utf-8")
    print(f" [+] Created 1-Click Dispatch Manifest for {count} targets: {MANIFEST_OUT}")

if __name__ == "__main__":
    main()
