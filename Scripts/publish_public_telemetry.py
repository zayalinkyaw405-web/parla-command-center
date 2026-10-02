"""
Scripts/publish_public_telemetry.py
===================================
Publishes the public OSINT telemetry report to a standalone Markdown release document ready for public distribution.
"""

import json
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FEED_FILE = PROJECT_ROOT / "Data" / "public_telemetry_feed.json"
RELEASE_FILE = PROJECT_ROOT / "Project" / "outbound_prospects" / "PUBLIC_TELEMETRY_RELEASE_2026.md"

LIVE_URL = "https://fog-coastal-talk-duck.trycloudflare.com"

def main():
    if not FEED_FILE.exists():
        print("[!] Telemetry feed not found.")
        return

    feed = json.loads(FEED_FILE.read_text(encoding="utf-8"))
    
    doc = f"""# 🛡️ Parla Autonomous Conflict Intelligence & Sanctions Telemetry (Public Release)

**Updated:** {feed.get('updated_at')}  
**Freemium Access Policy:** {feed.get('freemium_policy')}  

---

### Live Portal & API Endpoint
- **Web Verification Interface:** [{LIVE_URL}]({LIVE_URL})
- **Interactive Swagger Documentation:** [{LIVE_URL}/docs]({LIVE_URL}/docs)

---

### Settlement Receptors (Instant On-Chain USDT/USDC)
- **Solana Receptor (SPL):** `{feed['payment_receptors']['solana_usdt']}`
- **Polygon Receptor (EVM):** `{feed['payment_receptors']['polygon_usdt']}`

---

### Active High-Priority Intelligence Telemetry
"""
    for item in feed.get("recent_telemetry", []):
        doc += f"""
#### [{item['entity_id']}] {item['name']}
- **Role:** {item['role']}
- **Biometric Forensic Grade:** {item['forensic_status']}
- **Certified PDF Dossier Status:** AVAILABLE ($75.00 USD)
"""

    doc += """
---

*Published by Parla Autonomous Risk Telemetry Unit*
"""
    RELEASE_FILE.write_text(doc, encoding="utf-8")
    print(f" [+] Published Public Telemetry Release to: {RELEASE_FILE}")

if __name__ == "__main__":
    main()
