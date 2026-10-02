"""
Scripts/run_autonomous_farmer.py
================================
Master Orchestrator Daemon for Autonomous Wallet Farming.
Continuously runs lead mining, dynamic risk brief generation, OSINT feed syndication,
and monitors on-chain Solana/Polygon settlement nodes.
"""

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from parla.farming.lead_scraper import LeadScraperEngine
from parla.farming.risk_brief_generator import RiskBriefGenerator
from parla.farming.syndication_hub import SyndicationHub
from parla.monetization.payment_listener import OnChainPaymentListener

def execute_farming_cycle():
    print("=" * 80)
    print("        PARLA AUTONOMOUS WALLET FARMING ENGINE : ACTIVE CYCLE")
    print("=" * 80)
    
    # Step 1: Mine Leads
    scraper = LeadScraperEngine()
    leads_manifest = scraper.run_mining_cycle()
    print(f" [+] Phase 1: Mined {leads_manifest['total_mined']} high-exposure B2B leads.")

    # Step 2: Generate Tailored Risk Alerts
    brief_gen = RiskBriefGenerator()
    brief_count = brief_gen.process_all_mined_leads()
    print(f" [+] Phase 2: Generated {brief_count} personalized markdown risk briefs.")

    # Step 3: Package OSINT Syndication Feed
    hub = SyndicationHub()
    feed = hub.generate_feed()
    print(f" [+] Phase 3: Packaged OSINT feed with paywall headers.")

    # Step 4: Check On-Chain Receptors for Incoming Funds
    listener = OnChainPaymentListener()
    sol_txs = listener.check_solana_transfers()
    poly_txs = listener.check_polygon_transfers()
    print(f" [+] Phase 4: Checked On-Chain Nodes | Solana Txs: {len(sol_txs)} | Polygon Nonce: {poly_txs[0].get('nonce', 0) if poly_txs else 0}")
    print("=" * 80)
    print(" [PASS] Autonomous Farming Cycle Execution Complete.")

def main():
    daemon_mode = "--daemon" in sys.argv
    print(f"[*] Launching Master Wallet Farmer Daemon (Loop Mode: {daemon_mode})...")
    while True:
        try:
            execute_farming_cycle()
        except Exception as e:
            print(f"[!] Error in farming cycle: {e}")
            
        if not daemon_mode:
            break
        print(" [*] Sleeping for 60 seconds until next farming cycle...\n")
        time.sleep(60)

if __name__ == "__main__":
    main()
