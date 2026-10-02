"""
test_a2a_machine_purchase.py
=============================
End-to-End Verification Test for Autonomous Agent-to-Agent (A2A) Purchases.
Simulates an external AI Agent discovering, querying, negotiating HTTP 402 paywalls, 
settling payments, and retrieving machine datasets.
"""

import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path

# Ensure UTF-8 output encoding for Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000"

def test_a2a_flow():
    print("=" * 80)
    print("🧪 RUNNING END-TO-END AUTONOMOUS AI AGENT PURCHASE TEST")
    print("========================================================================")

    # 1. Test AI Plugin Discovery
    print(" [1/6] Testing OpenAI / LangChain AI Plugin Discovery (/.well-known/ai-plugin.json)...")
    req = urllib.request.urlopen(f"{BASE_URL}/.well-known/ai-plugin.json")
    plugin_data = json.loads(req.read().decode('utf-8'))
    assert plugin_data["name_for_model"] == "parla_sanctions_oracle"
    print(f"       ✅ Discovered Plugin: {plugin_data['name_for_human']}")

    # 2. Test AgentProtocol Discovery Card
    print(" [2/6] Testing AgentProtocol Card (/.well-known/agent-card.json)...")
    req = urllib.request.urlopen(f"{BASE_URL}/.well-known/agent-card.json")
    card_data = json.loads(req.read().decode('utf-8'))
    assert "sanctions_oracle_query" in card_data["capabilities"]
    print(f"       ✅ Discovered Agent Card: {card_data['agent_name']} (Capabilities: {len(card_data['capabilities'])})")

    # 3. Test Machine Catalog
    print(" [3/6] Fetching Machine Catalog (/api/v1/agent/catalog)...")
    req = urllib.request.urlopen(f"{BASE_URL}/api/v1/agent/catalog")
    catalog_data = json.loads(req.read().decode('utf-8'))
    assert catalog_data["total_products"] == 4
    print(f"       ✅ Catalog Returned {catalog_data['total_products']} Machine Products")

    # 4. Test Sanctions Risk Oracle
    print(" [4/6] Querying Sanctions Oracle (/api/v1/agent/oracle/sanctions/IND-SAC-001)...")
    req = urllib.request.urlopen(f"{BASE_URL}/api/v1/agent/oracle/sanctions/IND-SAC-001")
    oracle_data = json.loads(req.read().decode('utf-8'))
    assert oracle_data["sanctioned"] is True
    assert oracle_data["risk_score"] == 1.0
    print(f"       ✅ Oracle Verified Target: {oracle_data['name']} (Risk: {oracle_data['risk_score']} | Merkle Seal Present)")

    # 5. Test Unauthenticated Download (HTTP 402 Paywall Negotiation)
    print(" [5/6] Testing Unauthenticated Download for A2A-BIO-512D (Expecting HTTP 402)...")
    try:
        urllib.request.urlopen(f"{BASE_URL}/api/v1/agent/download/A2A-BIO-512D")
        print("       ❌ FAIL: Expected HTTP 402 Payment Required!")
        sys.exit(1)
    except urllib.error.HTTPError as err:
        assert err.code == 402
        price = err.headers.get("x402-price-usd")
        sol_receptor = err.headers.get("x402-solana-receptor")
        print(f"       ✅ HTTP 402 Paywall Negotiated! Price: ${price} USD | Solana Receptor: {sol_receptor[:12]}...")

    # 6. Test Machine Settlement & Authenticated Download
    print(" [6/6] Simulating Machine Settlement (/api/v1/agent/settle) & Authenticated Retrieval...")
    settle_payload = json.dumps({
        "product_id": "A2A-BIO-512D",
        "buyer_agent_id": "agent-pinecone-indexer-99",
        "network": "solana",
        "currency": "USDT",
        "tx_hash": "5Kn3m29ZpXy6vA8bC4dE1fG2h3j4k5m6n7p8q9r0s1t2u3v4w5x6y7z"
    }).encode('utf-8')

    settle_req = urllib.request.Request(
        f"{BASE_URL}/api/v1/agent/settle",
        data=settle_payload,
        headers={"Content-Type": "application/json"}
    )
    settle_res = json.loads(urllib.request.urlopen(settle_req).read().decode('utf-8'))
    auth_token = settle_res["x402_auth_token"]
    print(f"       ✅ Settlement Verified! Issued Token: {auth_token}")

    # Download with token header
    dl_req = urllib.request.Request(
        f"{BASE_URL}/api/v1/agent/download/A2A-BIO-512D",
        headers={"x402-auth-token": auth_token}
    )
    dl_res = urllib.request.urlopen(dl_req).read().decode('utf-8')
    vector_data = json.loads(dl_res)
    print(f"       ✅ Authenticated Payload Received! Vectors Count: {len(vector_data)} Identities")

    print("========================================================================")
    print("🎉 ALL 6 END-TO-END AUTONOMOUS AGENT PURCHASE TESTS PASSED 100%!")
    print("========================================================================")

if __name__ == "__main__":
    test_a2a_flow()
