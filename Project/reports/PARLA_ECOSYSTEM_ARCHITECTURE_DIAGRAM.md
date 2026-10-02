# 📐 Parla Autonomous System Architecture & Flow Diagram

> **System Overview:** End-to-end architecture detailing Edge Sensing, Multi-INT Triangulation, NIST FIPS 204 Post-Quantum Notarization, Human/Agent Discovery UI, and `x402` Autonomous Crypto Settlement.

```mermaid
graph TD
    %% ----------------------------------------------------------------------
    %% SUBGRAPH 1: INGESTION & TRIANGULATION
    %% ----------------------------------------------------------------------
    subgraph INGESTION ["📡 1. Multi-INT Sensing & Ingestion Layer"]
        IoT["📟 Industrial Edge Nodes<br/>(Vibration / Modal EMD)"]
        FIRMS["🛰️ NASA FIRMS VIIRS<br/>(Satellite Thermal Hotspots)"]
        ADSB["✈️ ADS-B Transponders<br/>(Military Sorties / Altitude)"]
        OSINT["📰 Conflict NLP Feeds<br/>(PII Redaction / spaCy NER)"]
        BIO["👤 ArcFace Biometrics<br/>(512-d Face Vector Embeddings)"]
    end

    %% ----------------------------------------------------------------------
    %% SUBGRAPH 2: CORE PROCESSING & SECURITY
    %% ----------------------------------------------------------------------
    subgraph CORE ["🛡️ 2. Parla Core & Zero-Trust Security Gate"]
        GATE{"🔒 Security Gate<br/>(HMAC / Quarantine)"}
        ADMIRALTY["📊 NATO 6x6 Admiralty<br/>(C3 to A1 Elevation)"]
        LEDGER["DB SQLite Merkle WAL<br/>(Offline ACID Ledger)"]
        PQC["⚛️ Post-Quantum Engine<br/>(NIST FIPS 204 ML-DSA)"]
    end

    %% ----------------------------------------------------------------------
    %% SUBGRAPH 3: DUAL MONETIZATION & MARKETPLACES
    %% ----------------------------------------------------------------------
    subgraph MONETIZATION ["💰 3. Monetization & A2A Machine Marketplace"]
        PORTAL["🌐 Due-Diligence Portal<br/>(FastAPI / Port 8000)"]
        TUNNEL["☁️ Cloudflare Tunnel<br/>(trycloudflare.com)"]
        UI["📱 Left Sidebar Web UI<br/>(28 Commanders / 21 Targets)"]
        DISCOVERY["🔍 A2A Auto-Discovery<br/>(ai-plugin.json / agent-card.json)"]
        X402["💳 HTTP 402 x402 Paywall<br/>(Price Headers & Receptors)"]
    end

    %% ----------------------------------------------------------------------
    %% SUBGRAPH 4: ON-CHAIN SETTLEMENT & DELIVERY
    %% ----------------------------------------------------------------------
    subgraph SETTLEMENT ["⛓️ 4. Sovereign On-Chain Settlement Rails"]
        SOL["☀️ Solana Receptor<br/>(89HXnLfaetwt...)"]
        POLY["🟣 Polygon Receptor<br/>(0x87CEFE4B...)"]
        LISTENER["🎧 Payment Listener<br/>(urllib RPC Monitor)"]
        PDF["📄 Certified PDF Dossier<br/>(ReportLab + Merkle Seal)"]
    end

    %% CONNECTIONS
    IoT --> GATE
    FIRMS --> ADMIRALTY
    ADSB --> ADMIRALTY
    OSINT --> GATE
    BIO --> GATE

    GATE -- Valid --> ADMIRALTY
    GATE -- Malformed/Forged --> QUARANTINE["⚠️ Forensic Quarantine"]
    
    ADMIRALTY --> LEDGER
    LEDGER --> PQC
    PQC --> PORTAL

    PORTAL --> TUNNEL
    TUNNEL --> UI
    PORTAL --> DISCOVERY
    PORTAL --> X402

    UI -- Human Checkout --> SOL
    UI -- Human Checkout --> POLY
    X402 -- Machine Payment --> SOL
    X402 -- Machine Payment --> POLY

    SOL --> LISTENER
    POLY --> LISTENER
    LISTENER -- Confirmed --> PDF
```

---

## 🔁 Sequence Flow: Autonomous Agent-to-Agent (A2A) Purchase

```mermaid
sequenceDiagram
    autonumber
    actor BuyerAgent as 🤖 Autonomous Buyer Agent
    participant Discovery as 🔍 /.well-known/agent-card.json
    participant Server as ⚡ Parla A2A API Server
    participant Paywall as 💳 HTTP 402 x402 Engine
    participant Blockchain as ⛓️ Solana / Polygon Mainnet
    participant Listener as 🎧 Payment Listener Daemon

    BuyerAgent->>Discovery: GET /.well-known/agent-card.json
    Discovery-->>BuyerAgent: Return Capabilities & Catalog URL
    
    BuyerAgent->>Server: GET /api/v1/agent/download/A2A-BIO-512D (No Token)
    Server-->>Paywall: Intercept Unauthenticated Request
    Paywall-->>BuyerAgent: HTTP 402 Payment Required (Headers: x402-price-usd: 150, receptors)
    
    BuyerAgent->>Blockchain: Transfer $150 USDT/USDC to Sovereign Address
    Blockchain-->>BuyerAgent: Transaction Hash (0x123... / 5Kn3...)
    
    BuyerAgent->>Server: POST /api/v1/agent/settle {product_id, tx_hash}
    Server->>Listener: Verify Transaction Status
    Listener-->>Server: On-Chain Settlement Confirmed
    Server-->>BuyerAgent: Return Auth Token (x402_auth_token: a2a_tok_...)
    
    BuyerAgent->>Server: GET /api/v1/agent/download/A2A-BIO-512D (Header: x402-auth-token)
    Server-->>BuyerAgent: 200 OK: ArcFace 512-d Vector Array Payload
```

---

*Diagram compiled for Parla Command Center Architecture Report.*
