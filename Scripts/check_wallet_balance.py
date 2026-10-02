"""
Scripts/check_wallet_balance.py
================================
Queries live public RPC nodes to fetch current mainnet balances for Solana and Polygon 
sovereign deposit receptors, including SPL/ERC20 USDT & USDC token contracts and 
local Merkle ledger audit records.
"""

import sys
import json
import urllib.request
from pathlib import Path

# Ensure UTF-8 output encoding for Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

SOLANA_ADDR = "89HXnLfaetwtJooVrxJxMuVyKmpKGfZ5Vm7CpiVW4Jos"
POLYGON_ADDR = "0x87CEFE4B75EB20F8E0A493A5D2EA3946AF5F985B"

# ERC20 Token Contract Addresses on Polygon Mainnet
POLYGON_USDT_CONTRACT = "0xc2132D05D31c914a87C6611C10748AEb04B58e8F"
POLYGON_USDC_CONTRACT = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"

# Common SPL Token Mints on Solana Mainnet
SOLANA_USDT_MINT = "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB"
SOLANA_USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

def query_solana():
    """Fetches native SOL and SPL token balances from Solana RPC."""
    # 1. Native SOL Balance
    payload_sol = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBalance",
        "params": [SOLANA_ADDR]
    }
    req = urllib.request.Request(
        "https://api.mainnet-beta.solana.com",
        data=json.dumps(payload_sol).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "ParlaNode/1.0"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        lamports = res.get("result", {}).get("value", 0)
        sol_bal = lamports / 1e9

    # 2. SPL Token Accounts (USDT/USDC)
    payload_spl = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [
            SOLANA_ADDR,
            {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
            {"encoding": "jsonParsed"}
        ]
    }
    req_spl = urllib.request.Request(
        "https://api.mainnet-beta.solana.com",
        data=json.dumps(payload_spl).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "ParlaNode/1.0"}
    )
    spl_tokens = []
    try:
        with urllib.request.urlopen(req_spl, timeout=10) as resp:
            res_spl = json.loads(resp.read().decode("utf-8"))
            accounts = res_spl.get("result", {}).get("value", [])
            for acc in accounts:
                info = acc["account"]["data"]["parsed"]["info"]
                mint = info.get("mint")
                amount = info.get("tokenAmount", {}).get("uiAmountString", "0")
                token_symbol = "USDT" if mint == SOLANA_USDT_MINT else ("USDC" if mint == SOLANA_USDC_MINT else mint[:8])
                spl_tokens.append({"symbol": token_symbol, "mint": mint, "amount": amount})
    except Exception:
        spl_tokens = []

    return sol_bal, spl_tokens


def query_polygon_erc20_balance(contract_addr: str) -> float:
    """Queries balanceOf(address) for ERC20 contracts on Polygon."""
    # balanceOf(address) signature hash is 0x70a08231
    padded_addr = POLYGON_ADDR[2:].zfill(64)
    data_hex = f"0x70a08231{padded_addr}"
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_call",
        "params": [
            {"to": contract_addr, "data": data_hex},
            "latest"
        ]
    }
    
    rpc_urls = ["https://polygon-rpc.com", "https://rpc.ankr.com/polygon", "https://polygon.llamarpc.com"]
    for rpc in rpc_urls:
        try:
            req = urllib.request.Request(
                rpc,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "ParlaNode/1.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                raw_hex = res.get("result", "0x0")
                tokens = int(raw_hex, 16) / 1e6  # USDT and USDC on Polygon use 6 decimals
                return tokens
        except Exception:
            continue
    return 0.0


def query_polygon():
    """Fetches native POL balance and ERC20 USDT/USDC balances."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_getBalance",
        "params": [POLYGON_ADDR, "latest"]
    }
    rpc_urls = ["https://polygon-rpc.com", "https://rpc.ankr.com/polygon", "https://polygon.llamarpc.com"]
    poly_bal = 0.0
    for rpc in rpc_urls:
        try:
            req = urllib.request.Request(
                rpc,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "ParlaNode/1.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                wei = int(res.get("result", "0x0"), 16)
                poly_bal = wei / 1e18
                break
        except Exception:
            continue

    usdt_bal = query_polygon_erc20_balance(POLYGON_USDT_CONTRACT)
    usdc_bal = query_polygon_erc20_balance(POLYGON_USDC_CONTRACT)

    return poly_bal, usdt_bal, usdc_bal


def check_local_ledger():
    """Queries local SQLite Merkle ledger for settled transactions."""
    ledger_path = PROJECT_ROOT / "Data" / "parla_ledger.db"
    if not ledger_path.exists():
        return []
    try:
        from parla.core.ledger import OfflineLedger
        ledger = OfflineLedger(db_path=str(ledger_path))
        # Get count or records
        records = ledger.query_audit_trail(limit=5)
        return records
    except Exception:
        return []


def main():
    print("=" * 80)
    print("        💰 PARLA SOVEREIGN WALLET LIVE ON-CHAIN BALANCE REPORT")
    print("========================================================================")
    
    # 1. Solana Receptor
    try:
        sol_bal, spl_tokens = query_solana()
        print(f" [+] Solana Receptor ({SOLANA_ADDR}):")
        print(f"     - Native SOL Balance: {sol_bal:.6f} SOL")
        if spl_tokens:
            for t in spl_tokens:
                print(f"     - SPL {t['symbol']} Token: {t['amount']}")
        else:
            print("     - SPL Tokens (USDT/USDC): 0.00 USDT / 0.00 USDC")
    except Exception as e:
        print(f" [!] Solana RPC Query Exception: {e}")

    print("-" * 80)

    # 2. Polygon Receptor
    try:
        poly_bal, usdt_bal, usdc_bal = query_polygon()
        print(f" [+] Polygon Receptor ({POLYGON_ADDR}):")
        print(f"     - Native POL Balance: {poly_bal:.6f} POL")
        print(f"     - Polygon USDT Token: {usdt_bal:.2f} USDT")
        print(f"     - Polygon USDC Token: {usdc_bal:.2f} USDC")
    except Exception as e:
        print(f" [!] Polygon RPC Query Exception: {e}")

    print("-" * 80)

    # 3. Local Merkle Ledger Audit
    records = check_local_ledger()
    print(f" [+] Local Merkle Audit Ledger (parla_ledger.db):")
    print(f"     - Total Settlement Entries: {len(records)}")
    for r in records:
        print(f"     - Tx: {r.get('tx_id', 'N/A')} | Amount: {r.get('amount', 0)} USD | Verified: {r.get('status', 'OK')}")

    print("========================================================================")

if __name__ == "__main__":
    main()
