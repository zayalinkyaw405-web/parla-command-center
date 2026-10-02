# Parla Sovereign Crypto P2P Cash Off-Ramp Guide

> **Goal:** Convert USDT/USDC deposited into your sovereign non-custodial wallet into local spendable cash (KBZPay, WaveMoney, PromptPay THB, SGD Bank Transfer) in under 10 minutes.

---

## 1. Sovereign Wallet Addresses (Receptors)

Your automated payment system receives funds directly into these offline encrypted non-custodial wallets:

- **Solana (SPL):** `89HXnLfaetwtJooVrxJxMuVyKmpKGfZ5Vm7CpiVW4Jos` *(USDT / USDC / SOL)*
- **Polygon (EVM):** `0x87CEFE4B75EB20F8E0A493A5D2EA3946AF5F985B` *(USDT / USDC / POL)*

---

## 2. Instant P2P Cash-Out Workflow (< 10 Minutes)

### Option A: Binance / Bybit P2P (Recommended for MMK / THB / SGD)
1. **Transfer USDT:** Send USDT from your sovereign address to your Binance/Bybit Funding Wallet (Solana network fee < $0.005).
2. **Go to P2P Trading:** Select `Sell USDT`.
3. **Choose Currency & Payment Method:**
   - **Myanmar Kyat (MMK):** Select `KBZPay`, `WaveMoney`, or `CB Bank` / `KBZ Bank`.
   - **Thai Baht (THB):** Select `PromptPay` or `Kasikornbank / SCB`.
   - **Singapore Dollar (SGD):** Select `PayNow` or `FAST Bank Transfer`.
4. **Select High-Completion Merchant:** Pick a verified merchant with >98% completion rate and >100 trades.
5. **Receive Cash First:** Wait until funds land in your KBZPay / WaveMoney / Bank Account app.
6. **Release Crypto:** Click "Payment Received" to release USDT to the buyer.

---

## 3. Immediate Off-Grid Direct P2P (No Exchange / OTC)
If you prefer direct OTC / local broker trade:
1. Contact local verified P2P exchanger on Telegram/Viber/Signal.
2. Provide your Solana deposit hash or send USDT directly to their address.
3. Exchanger transfers KBZPay / WaveMoney / Cash immediately.

---

## 4. Emergency Backup & Private Key Access
Your private keys are encrypted locally using AES-256-GCM in:
`Data/vault/sovereign_wallet.enc`

To export your raw private keys at any time:
```powershell
.\.venv\Scripts\python.exe -c "from parla.monetization.sovereign_wallet import SovereignWalletEngine; w = SovereignWalletEngine(); print(w.export_unencrypted_keys())"
```
*(Keep your private keys strictly confidential).*
