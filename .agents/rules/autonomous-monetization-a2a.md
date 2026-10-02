# Rule: Autonomous Monetization, A2A Protocols & Windows Resilience

## 1. Inbound Self-Service Monetization Architecture
- Default to inbound self-service digital marketplaces (Telegram Bot, Self-Hosted Portal, RapidAPI, Whop) over manual outbound email dispatch.
- Enable direct sovereign crypto settlement (Solana SPL / Polygon ERC20 USDT/USDC) with automated on-chain payment listeners.

## 2. Agent-to-Agent (A2A) Machine Protocol Invariants
- Expose standardized discovery endpoints:
  - `/.well-known/ai-plugin.json` (OpenAI / LangChain specification)
  - `/.well-known/agent-card.json` (AgentProtocol A2A specification)
  - `/api/v1/agent/catalog` (Machine-readable product directory)
- Implement `HTTP 402 Payment Required` with `x402` response headers for unauthenticated machine queries.
- Format machine data products in native AI formats (512-d vector arrays for Qdrant/Pinecone, SHA-256 Merkle trees, GeoJSON).

## 3. Zero-Cost & Minimum API Consumption Rule
- Perform all core calculations, biometric matching, PDF rendering, and ledger indexing locally on-system.
- Use public free RPCs and standard library HTTP tools (`urllib.request`) with throttled polling (30–60s). Avoid introducing paid cloud dependencies.

## 4. Windows Python Console & SQLite Resilience
- Always configure UTF-8 output streams on Windows CLI scripts (`sys.stdout.reconfigure(encoding="utf-8")`).
- Use explicit garbage collection (`import gc; gc.collect()`) prior to removing temporary SQLite database files on Windows.
