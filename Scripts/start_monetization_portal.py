"""
Scripts/start_monetization_portal.py
====================================
Launches the Parla B2B Due-Diligence & Monetization Server.
Displays active sovereign non-custodial wallet deposit receptors
and serves the search portal on http://127.0.0.1:8000.
Automatically ensures virtualenv Python is utilized.
"""

import sys
import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENV_PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"

# If invoked with system Python, transparently switch to .venv python
if VENV_PYTHON.exists() and Path(sys.executable).resolve() != VENV_PYTHON.resolve():
    print(f"[*] Re-routing through virtual environment: {VENV_PYTHON.name}")
    ret = subprocess.call([str(VENV_PYTHON), __file__] + sys.argv[1:])
    sys.exit(ret)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import uvicorn
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
