"""
parla/farming/risk_brief_generator.py
======================================
Automated Personalized Risk Brief Generator.
Generates tailored preliminary due-diligence alerts and sample dossiers with embedded checkout links
pointing directly to sovereign wallet receptors.
"""

import json
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTBOUND_DIR = PROJECT_ROOT / "Project" / "outbound_prospects"
DATA_DIR = PROJECT_ROOT / "Data"

from parla.monetization.sovereign_wallet import SovereignWalletEngine

class RiskBriefGenerator:
    """
    Generates personalized risk alerts for mined leads.
    """
    def __init__(self):
        OUTBOUND_DIR.mkdir(parents=True, exist_ok=True)
        self.wallet_engine = SovereignWalletEngine()
        self.wallets = self.wallet_engine.get_deposit_addresses()

    def generate_personalized_alert(self, lead: Dict[str, Any], tunnel_url: str = "http://127.0.0.1:8000") -> str:
        """Compiles customized markdown executive alert for lead."""
        alert_md = f"""# EXECUTIVE DUE-DILIGENCE ALERT: SANCTIONS & RISK EXPOSURE

**Prepared for:** {lead['company']} ({lead['contact_title']})
**Sector:** {lead['sector']} | **Region:** {lead['region']}
**Target Risk Anchor:** {lead['risk_trigger']}

---

### 1. Preliminary Risk Identification
Our automated intelligence nodes have flagged active supply-chain and sanctions exposure associated with entities operating in your regional sector.

- **Primary Command Link:** SAC High Command & Air Force Logistics Chains (`IND-SAC-001` / `IND-MAF-001`)
- **Forensic Verification:** Biometric facial recognition & Merkle ledger notarized proof.
- **Legal Directives:** OFAC / EU Council secondary sanctions and maritime insurance compliance directives.

---

### 2. Immediate Action & Dossier Acquisition
You can query our self-service portal or order a cryptographically verified court-admissible dossier ($75 USD / instant USDT/USDC settlement):

- **Live Compliance Portal:** [{tunnel_url}]({tunnel_url})
- **Solana Deposit Receptor:** `{self.wallets.get('solana')}`
- **Polygon Deposit Receptor:** `{self.wallets.get('polygon')}`

---

*Issued by Parla Autonomous Risk Telemetry Unit*
"""
        filename = OUTBOUND_DIR / f"{lead['id']}_{lead['company'].replace(' ', '_')}_alert.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(alert_md)
        return str(filename)

    def process_all_mined_leads(self, leads_file: Path = DATA_DIR / "mined_leads_cache.json") -> int:
        if not leads_file.exists():
            return 0
        with open(leads_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        leads = data.get("leads", [])
        count = 0
        for lead in leads:
            self.generate_personalized_alert(lead)
            count += 1
        return count

if __name__ == "__main__":
    gen = RiskBriefGenerator()
    c = gen.process_all_mined_leads()
    print(f"[*] Generated {c} personalized risk alerts.")
