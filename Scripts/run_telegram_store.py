"""
Scripts/run_telegram_store.py
==============================
Automated Telegram Crypto Storefront & Instant File Delivery Engine.
Allows B2B buyers, OSINT researchers, and legal teams to purchase certified 
dossiers and risk feeds directly via Telegram without cold emails.
"""

import os
import sys
import json
from pathlib import Path

# Ensure UTF-8 output formatting for Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from parla.monetization.sovereign_wallet import SovereignWalletEngine

ROSTER_FILE = PROJECT_ROOT / "Data" / "international_accountability_roster_2026.json"
REPORTS_DIR = PROJECT_ROOT / "Project" / "reports"

wallet_engine = SovereignWalletEngine()
deposit_addresses = wallet_engine.get_deposit_addresses()

def print_telegram_storefront_menu():
    print("=" * 70)
    print("🤖 PARLA AUTOMATED TELEGRAM CRYPTO STOREFRONT")
    print("======================================================================")
    print("Zero Cold-Email Selling | 24/7 Self-Service Crypto Paywall")
    print("----------------------------------------------------------------------")
    print(f"Solana (SPL) Deposit Receptor  : {deposit_addresses['solana']}")
    print(f"Polygon (ERC20) Deposit Receptor: {deposit_addresses['polygon']}")
    print("----------------------------------------------------------------------")
    print("Available Products for 1-Click Purchase:")
    print("  1. Certified Commander Dossier (PDF + Merkle Seal) -> $75 USDT/USDC")
    print("  2. Full 28-Commander Biometric Embeddings (JSON)  -> $250 USDT/USDC")
    print("  3. 21-Entity Corporate Exposure Feed (JSON)        -> $150 USDT/USDC")
    print("======================================================================")

def generate_telegram_bot_payload():
    """Generates the Telegram Bot Command Schema for Telegram BotFather setup."""
    commands = [
        {"command": "start", "description": "Launch Parla Risk Intelligence Storefront"},
        {"command": "roster", "description": "Browse 28 Indexed Sanctioned Commanders"},
        {"command": "corporate", "description": "Browse 21 Corporate Bunkering & Logistics Targets"},
        {"command": "buy", "description": "Instant USDT/USDC Paywall Checkout"},
        {"command": "verify", "description": "Verify Payment & Download Certified Dossier PDF"}
    ]
    
    bot_config_path = PROJECT_ROOT / "Data" / "telegram_bot_config.json"
    bot_config_path.write_text(json.dumps({
        "bot_title": "Parla Risk Telemetry Store",
        "commands": commands,
        "deposit_addresses": deposit_addresses,
        "status": "READY_FOR_BOTFATHER_TOKEN"
    }, indent=2), encoding="utf-8")
    
    print(f"✅ Telegram Bot Configuration exported to: {bot_config_path}")

if __name__ == "__main__":
    print_telegram_storefront_menu()
    generate_telegram_bot_payload()
