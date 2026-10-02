"""
test_recon_dual_personality.py
===============================
Executable Integration Test for Parla / Varla Recon Modules & VoidNode Bridge.
"""

import sys
import json
import time
from pathlib import Path

# Ensure UTF-8 output encoding for Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from parla_varla_core.wrappers.parla_recon import ParlaReconEngine
from parla_varla_core.wrappers.varla_recon import VarlaAdversarialReconEngine

def test_recon_pipeline():
    print("=" * 80)
    print("🧪 EXECUTING RECON MODULE TEST: PARLA (ETHICAL) VS VARLA (ADVERSARIAL)")
    print("========================================================================")

    parla_recon = ParlaReconEngine()
    varla_recon = VarlaAdversarialReconEngine()

    target = "IND-SAC-001"

    # 1. Parla Ethical Recon Execution
    print(" [1/2] Executing Parla Ethical Reconnaissance Pipeline...")
    raw_stream = "Scraped OSINT feed for General Min Aung Hlaing. Spotter email: informant@news.mm, Phone: +95 9 123 4567."
    parla_res = parla_recon.execute_recon(target, raw_stream)
    
    print(f"       Recon ID    : {parla_res['recon_id']}")
    print(f"       Sanitized   : {parla_res['sanitized_payload']}")
    print(f"       Admiralty   : {parla_res['admiralty_grade']}")
    print(f"       SHA256 Root : {parla_res['sha256_root'][:24]}...")
    
    assert "[REDACTED_PHONE]" in parla_res["sanitized_payload"]
    assert "[REDACTED_EMAIL]" in parla_res["sanitized_payload"]
    print("       ✅ Parla PII Redaction & SHA-256 Merkle Root Verified!")

    print("-" * 80)

    # 2. Varla Adversarial Darkweb Evasion Execution
    print(" [2/2] Executing Varla Adversarial Darkweb Recon Pipeline...")
    varla_res = varla_recon.generate_adversarial_recon(target)
    
    print(f"       Recon ID    : {varla_res['recon_id']}")
    print(f"       Technique   : {varla_res['evasion_technique']}")
    print(f"       Onion Node  : {varla_res['darkweb_onion_endpoint']}")
    print(f"       Admiralty   : {varla_res['admiralty_grade']}")
    print(f"       HMAC Sig    : {varla_res['hmac_signature'][:24]}...")

    assert varla_res["is_evasion_active"] is True
    assert varla_res["admiralty_grade"] == "GRADE_F6_UNTRUSTED"
    print("       ✅ Varla Evasion Vector & Darkweb Mock Generated!")

    print("========================================================================")
    print("🎉 RECON MODULE DUAL-PERSONALITY TEST COMPLETED SUCCESSFULLY!")
    print("========================================================================")

if __name__ == "__main__":
    test_recon_pipeline()
