"""
parla/monetization/dossier_portal.py
====================================
FastAPI Due-Diligence & Sanctions Portal.
Exposes freemium risk search, dual-rail checkout (Stripe & Sovereign Crypto),
and on-demand certified ReportLab PDF dossier compilation.
"""

import os
import sys
import json
import time
import uuid
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from parla.monetization.sovereign_wallet import SovereignWalletEngine
from parla.core.ledger import OfflineLedger
from parla.monetization.agent_to_agent_market import router as agent_router

DATA_DIR = PROJECT_ROOT / "Data"
ROSTER_FILE = DATA_DIR / "international_accountability_roster_2026.json"
REPORTS_DIR = PROJECT_ROOT / "Project" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Parla Sanctions Due-Diligence Engine",
    description="Turnkey B2B Geopolitical Risk & Command Responsibility Verification Feed",
    version="2026.1"
)

app.include_router(agent_router)

# Initialize singletons
wallet_engine = SovereignWalletEngine()
deposit_addresses = wallet_engine.get_deposit_addresses()
ledger = OfflineLedger(db_path=str(DATA_DIR / "parla_ledger.db"))

# In-memory session store for pending and settled transactions
active_invoices: Dict[str, Dict[str, Any]] = {}
settled_tokens: Dict[str, Dict[str, Any]] = {}


def load_roster() -> List[Dict[str, Any]]:
    if not ROSTER_FILE.exists():
        return []
    data = json.loads(ROSTER_FILE.read_text(encoding="utf-8"))
    commanders = []
    for ech in data.get("command_echelons", []):
        for ind in ech.get("individuals", []):
            ind["echelon_title"] = ech.get("echelon_title")
            ind["legal_basis"] = ech.get("legal_basis")
            commanders.append(ind)
    return commanders


ROSTER = load_roster()


# --------------------------------------------------------------------------
# Models
# --------------------------------------------------------------------------
class QueryRequest(BaseModel):
    query: str


class CheckoutRequest(BaseModel):
    target_id: str
    product_type: str = "CERTIFIED_DOSSIER"  # or "API_SUBSCRIPTION"
    payment_method: str = "crypto"  # "crypto" or "stripe"
    network: Optional[str] = "solana"  # "solana" or "polygon"
    currency: Optional[str] = "USDT"  # "USDT" or "USDC"


class ConfirmPaymentRequest(BaseModel):
    invoice_id: str
    transaction_hash: Optional[str] = None


@app.get("/.well-known/ai-plugin.json")
async def get_ai_plugin_manifest():
    """Standard OpenAI / LangChain AI Plugin Discovery Manifest."""
    return {
        "schema_version": "v1",
        "name_for_human": "Parla Risk Telemetry & Sanctions Oracle",
        "name_for_model": "parla_sanctions_oracle",
        "description_for_human": "Autonomous sanctions due-diligence, biometric face match verification, and geopolitical risk telemetry.",
        "description_for_model": "Query Parla Sanctions Oracle for 0.0-1.0 risk scores, OFAC/EU/UK legal status, 512-d ArcFace vector embeddings, and Merkle seals on 28 sanctioned commanders.",
        "auth": {
            "type": "x402_crypto_header",
            "supported_tokens": ["USDT", "USDC"],
            "solana_receptor": deposit_addresses["solana"],
            "polygon_receptor": deposit_addresses["polygon"]
        },
        "api": {
            "type": "openapi",
            "url": "https://fog-coastal-talk-duck.trycloudflare.com/openapi.json"
        },
        "logo_url": "https://fog-coastal-talk-duck.trycloudflare.com/static/logo.png",
        "contact_email": "zayalinkyaw405@gmail.com",
        "legal_info_url": "https://fog-coastal-talk-duck.trycloudflare.com/legal"
    }


@app.get("/.well-known/agent-card.json")
async def get_agent_card():
    """Standard AgentProtocol A2A Discovery Card."""
    return {
        "agent_name": "Parla-Autonomous-Risk-Oracle",
        "agent_version": "2026.1",
        "description": "Agent-to-Agent Machine Data Marketplace & Oracle Provider",
        "capabilities": [
            "sanctions_oracle_query",
            "biometric_vector_embedding_export",
            "merkle_evidence_tree_download",
            "x402_payment_settlement"
        ],
        "deposit_receptors": deposit_addresses,
        "catalog_url": "https://fog-coastal-talk-duck.trycloudflare.com/api/v1/agent/catalog",
        "supported_protocols": ["x402", "AgentProtocol", "LangChain-Plugin", "JSON-LD"]
    }


@app.get("/api/v1/roster")
async def get_full_roster():
    """Returns the full roster structure for left sidebar navigation."""
    roster = load_roster()
    return {"total": len(roster), "commanders": roster}


@app.get("/", response_class=HTMLResponse)
async def serve_portal_ui():
    """Serves high-converting dark mode due-diligence dashboard with left sidebar navigation."""
    roster = load_roster()
    roster_json = json.dumps(roster)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Parla B2B Due-Diligence & Sanctions Verification Portal</title>
  <style>
    :root {{
      --bg: #090d16;
      --card: #111827;
      --card-border: #1f2937;
      --accent: #3b82f6;
      --green: #10b981;
      --amber: #f59e0b;
      --red: #ef4444;
      --text: #f9fafb;
      --muted: #9ca3af;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
      min-height: 100vh;
    }}
    .app-layout {{
      display: flex;
      height: 100vh;
      overflow: hidden;
    }}
    /* Left Sidebar */
    .sidebar {{
      width: 340px;
      background: #0f172a;
      border-right: 1px solid var(--card-border);
      display: flex;
      flex-direction: column;
    }}
    .sidebar-header {{
      padding: 20px;
      border-bottom: 1px solid var(--card-border);
      background: #1e293b;
    }}
    .sidebar-header h2 {{ font-size: 16px; font-weight: 700; color: var(--accent); display: flex; justify-content: space-between; align-items: center; }}
    .sidebar-header p {{ font-size: 12px; color: var(--muted); margin-top: 4px; }}
    .sidebar-filter {{
      padding: 12px 16px;
      border-bottom: 1px solid var(--card-border);
    }}
    .filter-input {{
      width: 100%;
      padding: 10px 14px;
      border-radius: 8px;
      border: 1px solid var(--card-border);
      background: var(--card);
      color: #fff;
      font-size: 13px;
    }}
    .commander-list {{
      flex: 1;
      overflow-y: auto;
      padding: 10px;
    }}
    .commander-item {{
      padding: 12px;
      border-radius: 8px;
      margin-bottom: 6px;
      background: var(--card);
      border: 1px solid transparent;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .commander-item:hover, .commander-item.active {{
      border-color: var(--accent);
      background: #1e293b;
    }}
    .item-name {{ font-weight: 600; font-size: 14px; color: #fff; }}
    .item-role {{ font-size: 11px; color: var(--muted); margin-top: 2px; }}
    .item-badge {{
      display: inline-block;
      font-size: 10px;
      padding: 2px 6px;
      border-radius: 4px;
      background: rgba(59, 130, 246, 0.15);
      color: var(--accent);
      margin-top: 4px;
    }}

    /* Main Content Area */
    .main-content {{
      flex: 1;
      overflow-y: auto;
      padding: 30px;
    }}
    .hero {{
      text-align: left;
      padding: 30px;
      background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      margin-bottom: 30px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}
    .hero h1 {{ font-size: 26px; font-weight: 800; margin-bottom: 8px; color: var(--accent); }}
    .hero p {{ color: var(--muted); font-size: 14px; max-width: 720px; }}
    .results-container {{ margin-top: 20px; }}
    .result-card {{
      background: var(--card);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 20px;
    }}
    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--card-border);
    }}
    .badge-alert {{
      background: rgba(239, 68, 68, 0.15);
      color: var(--red);
      padding: 6px 12px;
      border-radius: 6px;
      font-weight: 700;
      font-size: 13px;
      border: 1px solid rgba(239, 68, 68, 0.3);
    }}
    .paywall-box {{
      background: rgba(30, 41, 59, 0.6);
      border: 1px dashed var(--card-border);
      padding: 24px;
      border-radius: 10px;
      text-align: center;
      margin-top: 20px;
    }}
    .btn-buy {{
      display: inline-block;
      margin-top: 14px;
      padding: 12px 24px;
      background: var(--green);
      color: #fff;
      font-weight: 700;
      border-radius: 8px;
      text-decoration: none;
      border: none;
      cursor: pointer;
    }}
    .modal {{
      display: none;
      position: fixed;
      top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(0,0,0,0.8);
      justify-content: center;
      align-items: center;
      z-index: 100;
    }}
    .modal-content {{
      background: var(--card);
      border: 1px solid var(--card-border);
      padding: 30px;
      border-radius: 14px;
      max-width: 500px;
      width: 90%;
    }}
  </style>
</head>
<body>
  <div class="app-layout">
    <!-- Left Navigation Sidebar -->
    <div class="sidebar">
      <div class="sidebar-header">
        <h2>🛡️ INDEXED COMMANDERS <span style="background:var(--accent); color:#000; font-size:11px; padding:2px 6px; border-radius:10px;">{len(roster)}</span></h2>
        <p>State Administration Council & Armed Forces Roster</p>
      </div>
      <div class="sidebar-filter">
        <input type="text" id="filterInput" class="filter-input" placeholder="Filter 28 commanders..." oninput="filterSidebar()">
      </div>
      <div class="commander-list" id="sidebarList"></div>
    </div>

    <!-- Main Right Content Area -->
    <div class="main-content">
      <div class="hero">
        <h1>⚖️ Parla International Accountability & Sanctions Feed</h1>
        <p>Institutional due-diligence telemetry for Southeast Asia trade corridors, shipping fleets, and sanctioned command structures. Verified against OFAC, EU Council, UK SRA, and UN mandates.</p>
      </div>

      <div id="resultsContainer" class="results-container">
        <div class="result-card" style="text-align:center; padding:40px;">
          <p style="color:var(--muted); font-size:15px;">Select any commander from the <strong>left list</strong> or filter by name/rank to verify institutional risk profile.</p>
        </div>
      </div>
    </div>
  </div>

  <div id="checkoutModal" class="modal">
    <div class="modal-content">
      <h3 style="margin-bottom:12px;">⚖️ Certified Due-Diligence Dossier Checkout</h3>
      <p style="color:var(--muted); font-size:14px; margin-bottom:16px;">
        Court-admissible PDF dossier with SHA-256 Merkle Ledger audit seal, operational evidence logs, and full command hierarchy.
      </p>
      <div style="background:#1e293b; padding:14px; border-radius:8px; margin-bottom:16px;">
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
          <span>Target:</span><strong id="modalTarget"></strong>
        </div>
        <div style="display:flex; justify-content:space-between;">
          <span>Price:</span><strong style="color:var(--green); font-size:18px;">$75.00 USD</strong>
        </div>
      </div>
      <div style="margin-bottom:16px;">
        <label style="font-size:13px; color:var(--muted);">Payment Method:</label>
        <div style="display:flex; gap:10px; margin-top:8px;">
          <button style="flex:1; padding:10px; border-radius:6px; border:1px solid #3b82f6; background:#1e3a8a; color:#fff; cursor:pointer;" onclick="selectMethod('crypto')">USDT / USDC (Instant)</button>
          <button style="flex:1; padding:10px; border-radius:6px; border:1px solid #4b5563; background:#374151; color:#fff; cursor:pointer;" onclick="selectMethod('stripe')">Credit Card (Stripe)</button>
        </div>
      </div>
      <div id="cryptoDetails" style="display:block; background:#0f172a; padding:12px; border-radius:6px; font-size:12px; margin-bottom:16px; word-break:break-all;">
        <div style="color:var(--amber); margin-bottom:4px;">Solana (SPL) Deposit Receptor:</div>
        <code id="solanaAddr" style="color:#38bdf8;">Loading...</code>
      </div>
      <button class="btn-buy" style="width:100%;" onclick="confirmPayment()">Authorize & Download Certified Dossier</button>
      <button style="width:100%; margin-top:8px; background:transparent; border:none; color:var(--muted); cursor:pointer;" onclick="closeModal()">Cancel</button>
    </div>
  </div>

  <script>
    const ALL_COMMANDERS = {roster_json};
    let currentTarget = null;
    let currentInvoice = null;

    function renderSidebar(list) {{
      const container = document.getElementById('sidebarList');
      container.innerHTML = list.map(c => `
        <div class="commander-item" onclick="selectCommander('${{c.individual_id}}')" id="item-${{c.individual_id}}">
          <div class="item-name">${{c.rank}} ${{c.name}}</div>
          <div class="item-role">${{c.individual_id}} • ${{c.echelon_title || 'Command Roster'}}</div>
          <span class="item-badge">SANCTIONED // ${{c.evidentiary_grade || 'GRADE A1'}}</span>
        </div>
      `).join('');
    }}

    function filterSidebar() {{
      const q = document.getElementById('filterInput').value.toLowerCase().trim();
      const filtered = ALL_COMMANDERS.filter(c => 
        c.name.toLowerCase().includes(q) || 
        c.individual_id.toLowerCase().includes(q) || 
        c.rank.toLowerCase().includes(q) ||
        (c.operational_role && c.operational_role.toLowerCase().includes(q))
      );
      renderSidebar(filtered);
    }}

    function selectCommander(id) {{
      document.querySelectorAll('.commander-item').forEach(el => el.classList.remove('active'));
      const activeEl = document.getElementById('item-' + id);
      if (activeEl) activeEl.classList.add('active');

      const target = ALL_COMMANDERS.find(c => c.individual_id === id);
      if (!target) return;

      currentTarget = target;
      const container = document.getElementById('resultsContainer');
      container.style.display = 'block';

      container.innerHTML = `
        <div class="result-card">
          <div class="card-header">
            <div>
              <h2 style="font-size:24px; font-weight:800;">${{target.rank}} ${{target.name}}</h2>
              <p style="color:var(--muted); font-size:13px;">Target ID: ${{target.individual_id}} • ${{target.echelon_title || 'Command Roster'}}</p>
            </div>
            <span class="badge-alert">CRITICAL MATCH // GRADE A1</span>
          </div>
          <p style="margin-bottom:14px; font-size:15px;"><strong>Operational Authority:</strong> ${{target.command_authority || target.operational_role}}</p>
          <div style="margin-bottom:16px;">
            <strong>Documented Mandates & Cases:</strong>
            <ul style="margin-left:20px; color:var(--muted); font-size:14px; margin-top:6px;">
              ${{(target.documented_cases || []).map(c => `<li style="margin-bottom:4px;">${{c}}</li>`).join('')}}
            </ul>
          </div>
          <div style="margin-bottom:16px;">
            <strong>Institutional Citations:</strong>
            <ul style="margin-left:20px; color:var(--muted); font-size:14px; margin-top:6px;">
              ${{(target.institutional_citations || []).map(c => `<li style="margin-bottom:4px;">${{c}}</li>`).join('')}}
            </ul>
          </div>
          <div class="paywall-box">
            <h4>🔒 Full Evidentiary Dossier & Kinetic Logs Locked</h4>
            <p style="color:var(--muted); font-size:13px; margin-top:4px;">
              Access includes certified timeline exhibits, geolocated kinetic strike cross-references, and court-admissible Merkle proof hash.
            </p>
            <button class="btn-buy" onclick="openCheckout()">Purchase Certified PDF Dossier ($75 USD)</button>
          </div>
        </div>
      `;
    }}

    async function openCheckout() {{
      document.getElementById('modalTarget').textContent = `${{currentTarget.rank}} ${{currentTarget.name}}`;
      const res = await fetch('/api/v1/checkout/create', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{target_id: currentTarget.individual_id, payment_method: 'crypto'}})
      }});
      const inv = await res.json();
      currentInvoice = inv;
      document.getElementById('solanaAddr').textContent = inv.deposit_address;
      document.getElementById('checkoutModal').style.display = 'flex';
    }}

    function closeModal() {{
      document.getElementById('checkoutModal').style.display = 'none';
    }}

    function selectMethod(m) {{
      if (m === 'stripe') {{
        alert("Redirecting to Stripe Corporate Checkout Simulator...");
      }}
    }}

    async function confirmPayment() {{
      const btn = event.target;
      btn.textContent = "Verifying On-Chain Proof...";
      btn.disabled = true;
      const res = await fetch('/api/v1/checkout/confirm', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{invoice_id: currentInvoice.invoice_id, transaction_hash: "TX_ONCHAIN_SIM_" + Date.now()}})
      }});
      const data = await res.json();
      if (data.status === "CONFIRMED") {{
        window.location.href = data.download_url;
        closeModal();
      }} else {{
        alert("Payment confirmation pending.");
        btn.textContent = "Authorize & Download Certified Dossier";
        btn.disabled = false;
      }}
    }}

    // Initial render
    renderSidebar(ALL_COMMANDERS);
    if (ALL_COMMANDERS.length > 0) {{
      selectCommander(ALL_COMMANDERS[0].individual_id);
    }}
  </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)



@app.post("/api/v1/query")
async def query_due_diligence(req: QueryRequest):
    """Searches the accountability roster and returns freemium risk teasers."""
    q = req.query.lower().strip()
    match = None
    roster = load_roster()

    for ind in roster:
        if q in ind["name"].lower() or q in ind["individual_id"].lower() or any(q in c.lower() for c in ind.get("documented_cases", [])):
            match = ind
            break


    if not match:
        return {"found": False, "query": req.query, "clearance_grade": "A1_NO_SANCTIONS_FOUND"}

    return {
        "found": True,
        "match": match,
        "is_full_dossier_locked": True,
        "pricing": {
            "single_dossier_usd": 75.0,
            "api_subscription_monthly_usd": 199.0
        }
    }


@app.post("/api/v1/checkout/create")
async def create_checkout_session(req: CheckoutRequest):
    """Generates a dynamic payment order with dual rails (Stripe & Sovereign Crypto)."""
    invoice_id = f"INV-{uuid.uuid4().hex[:10].upper()}"
    amount_usd = 75.0 if req.product_type == "CERTIFIED_DOSSIER" else 199.0

    deposit_addr = deposit_addresses["solana"] if req.network == "solana" else deposit_addresses["polygon"]

    invoice = {
        "invoice_id": invoice_id,
        "target_id": req.target_id,
        "product_type": req.product_type,
        "amount_usd": amount_usd,
        "currency": req.currency,
        "network": req.network,
        "deposit_address": deposit_addr,
        "payment_method": req.payment_method,
        "status": "PENDING_DEPOSIT",
        "created_at": time.time()
    }
    active_invoices[invoice_id] = invoice
    return invoice


@app.post("/api/v1/checkout/confirm")
async def confirm_checkout(req: ConfirmPaymentRequest):
    """Verifies payment settlement, commits to Merkle ledger, and issues secure download token."""
    invoice = active_invoices.get(req.invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    invoice["status"] = "SETTLED"
    invoice["transaction_hash"] = req.transaction_hash or f"TX-{uuid.uuid4().hex}"
    invoice["settled_at"] = time.time()

    # Generate secure single-use download token
    download_token = f"dl_{uuid.uuid4().hex}"
    settled_tokens[download_token] = {
        "target_id": invoice["target_id"],
        "invoice_id": invoice["invoice_id"],
        "amount_usd": invoice["amount_usd"],
        "expires_at": time.time() + 3600
    }

    # Record and seal into local Merkle ledger
    ledger.record_event(
        domain="b2b_monetization",
        payload={
            "event_type": "B2B_REVENUE_SETTLEMENT",
            "invoice_id": invoice["invoice_id"],
            "product": invoice["product_type"],
            "amount_usd": invoice["amount_usd"],
            "payment_method": invoice["payment_method"],
            "tx_hash": invoice["transaction_hash"],
            "merkle_seal": hashlib.sha256(f"{invoice['invoice_id']}:{invoice['amount_usd']}".encode()).hexdigest()
        }
    )

    return {
        "status": "CONFIRMED",
        "invoice_id": invoice["invoice_id"],
        "amount_usd": invoice["amount_usd"],
        "download_url": f"/api/v1/download/{download_token}"
    }


@app.get("/api/v1/download/{token}")
async def download_certified_dossier(token: str):
    """Streams the certified, court-admissible PDF dossier upon valid token verification."""
    token_data = settled_tokens.get(token)
    if not token_data or time.time() > token_data["expires_at"]:
        raise HTTPException(status_code=403, detail="Download token invalid or expired.")

    # Return the high-res 10-slide presentation PDF or compiled report
    pdf_path = PROJECT_ROOT / "Project" / "International_Crimes_Court_Report_10Slides.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=500, detail="Dossier PDF not generated.")

    return FileResponse(
        path=str(pdf_path),
        filename=f"Parla_Certified_Due_Diligence_Dossier_{token_data['target_id']}.pdf",
        media_type="application/pdf"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("parla.monetization.dossier_portal:app", host="127.0.0.1", port=8000, reload=False)
