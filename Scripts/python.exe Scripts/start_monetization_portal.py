"""
Scripts/start_monetization_portal.py
====================================
Launches the Parla B2B Due-Diligence & Monetization Server.
Displays active sovereign non-custodial wallet deposit receptors
and serves the search portal on http://127.0.0.1:8000.
"""

import sys
import os
import uvicorn
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from parla.monetization.sovereign_wallet import SovereignWalletEngine


def main():
    wallet = SovereignWalletEngine()
    addrs = wallet.get_deposit_addresses()

    print("=" * 80)
    print("      PARLA AUTONOMOUS DUE-DILIGENCE & MONETIZATION PORTAL")
    print("=" * 80)
    print(" [*] Status:                   ONLINE & ACCEPTING INQUIRIES")
    print(" [*] Local Portal Interface:   http://127.0.0.1:8000")
    print(" [*] Interactive Swagger Docs: http://127.0.0.1:8000/docs")
    print(" [*] Pricing Model:            $75 USD / Certified PDF Dossier")
    print("                               $199 USD / Monthly API Subscription")
    print(" [*] Settlement Rails:         Stripe (Cards) + Instant Borderless Crypto")
    print("-" * 80)
    print(f" [+] Solana (SPL) Receptor:    {addrs['solana']}")
    print(f" [+] Polygon (EVM) Receptor:   {addrs['polygon']}")
    print("=" * 80)
    print(" Press Ctrl+C to terminate.")
    print("-" * 80)

    uvicorn.run("parla.monetization.dossier_portal:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
