"""
test_autonomous_farmer.py
==========================
Test suite for the Autonomous Wallet Farming Engine.
"""

import unittest
from pathlib import Path
import json

from parla.farming.lead_scraper import LeadScraperEngine
from parla.farming.risk_brief_generator import RiskBriefGenerator
from parla.farming.syndication_hub import SyndicationHub
from parla.monetization.payment_listener import OnChainPaymentListener

class TestAutonomousFarmer(unittest.TestCase):
    def test_lead_scraper(self):
        scraper = LeadScraperEngine()
        res = scraper.run_mining_cycle()
        self.assertGreater(res["total_mined"], 0)
        self.assertTrue(Path(scraper.DATA_DIR / "mined_leads_cache.json" if hasattr(scraper, 'DATA_DIR') else "Data/mined_leads_cache.json").exists())

    def test_risk_brief_generator(self):
        gen = RiskBriefGenerator()
        lead = {
            "id": "TEST-LEAD-001",
            "company": "Test Maritime Company",
            "contact_title": "Risk Officer",
            "sector": "Maritime Bunkering",
            "region": "Singapore",
            "risk_trigger": "Sanctions Verification"
        }
        path = gen.generate_personalized_alert(lead)
        self.assertTrue(Path(path).exists())

    def test_syndication_hub(self):
        hub = SyndicationHub()
        feed = hub.generate_feed()
        self.assertIn("payment_receptors", feed)
        self.assertEqual(feed["payment_receptors"]["solana_usdt"], "89HXnLfaetwtJooVrxJxMuVyKmpKGfZ5Vm7CpiVW4Jos")

    def test_payment_listener(self):
        listener = OnChainPaymentListener()
        sol = listener.check_solana_transfers()
        poly = listener.check_polygon_transfers()
        self.assertIsInstance(sol, list)
        self.assertIsInstance(poly, list)

if __name__ == "__main__":
    unittest.main()
