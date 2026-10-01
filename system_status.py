"""
system_status.py
Parla AI System Health & Operational Status Diagnostic
"""
import sys
import os
import sqlite3
from pathlib import Path

# Safe encoding on Windows CP1252 consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

print("=" * 70)
print("[PARLA AI] SYSTEM STATUS DIAGNOSTIC")
print("=" * 70)

status_report = {"PASS": 0, "FAIL": 0, "WARN": 0}

def check(name, condition, details=""):
    if condition:
        print(f"  ✓ {name}")
        if details: print(f"    ↳ {details}")
        status_report["PASS"] += 1
    else:
        print(f"  ✗ {name}")
        if details: print(f"    ↳ {details}")
        status_report["FAIL"] += 1

# 1. Environment
print("\n[1] ENVIRONMENT")
check("Python Version", sys.version_info >= (3, 8), f"v{sys.version.split()[0]}")
check("Project Root", PROJECT_ROOT.name == "iot_agent", str(PROJECT_ROOT))

# 2. Core Dependencies
print("\n[2] CORE DEPENDENCIES")
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    check("spaCy NLP Engine", True, "en_core_web_sm loaded")
except Exception as e:
    check("spaCy NLP Engine", False, str(e))

try:
    import numpy, sklearn
    check("Machine Learning (numpy, sklearn)", True)
except Exception as e:
    check("Machine Learning (numpy, sklearn)", False, str(e))

try:
    import shap
    check("Explainability (SHAP)", True)
except Exception as e:
    check("Explainability (SHAP)", False, str(e))

# 3. Database & Ledger
print("\n[3] ZERO-TRUST LEDGER")
db_path = PROJECT_ROOT / "Data" / "parla_ledger.db"
check("Database File Exists", db_path.exists(), str(db_path))

if db_path.exists():
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ledger_blocks'")
        table_exists = cursor.fetchone() is not None
        check("Ledger Table Exists", table_exists)
        
        if table_exists:
            cursor.execute("SELECT COUNT(*) FROM ledger_blocks")
            total_blocks = cursor.fetchone()[0]
            check("Total Ledger Blocks", total_blocks > 0, f"{total_blocks} blocks sealed")
            
            cursor.execute("SELECT domain, COUNT(*) FROM ledger_blocks GROUP BY domain")
            domains = cursor.fetchall()
            for domain, count in domains:
                print(f"    ↳ {domain}: {count} blocks")
        conn.close()
    except Exception as e:
        check("Database Read Access", False, str(e))

# 4. AI Modules
print("\n[4] AI MODULES & INTELLIGENCE")
modules_to_check = [
    ("Core: Agent Prompt", "parla.core.agent_prompt", "ParlaAgentPrompt"),
    ("Core: Knowledge Base", "parla.core.knowledge_base", "ParlaKnowledgeBase"),
    ("Core: Feedback Loop", "parla.core.feedback_loop", "FeedbackLoop"),
    ("Domain: OSINT NLP", "parla.domains.osint_nlp", "OSINTEventExtractor"),
    ("Domain: Risk Mapper", "parla.domains.risk_mapper", "RegionalRiskMapper"),
    ("Domain: Industrial", "parla.domains.industrial", "IndustrialProcessor"),
]

for name, module_path, class_name in modules_to_check:
    try:
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)
        check(name, True, f"{class_name} ready")
    except Exception as e:
        check(name, False, str(e))

# 5. Feedback Loop State
print("\n[5] ADAPTIVE LEARNING STATE")
try:
    from parla.core.feedback_loop import FeedbackLoop
    fb = FeedbackLoop()
    thresholds = fb.get_current_thresholds()
    if thresholds:
        check("Dynamic Thresholds Active", True, f"{len(thresholds)} event types calibrated")
        for evt, thresh in list(thresholds.items())[:3]: # Show top 3
            print(f"    ↳ {evt} >= {thresh}")
    else:
        check("Dynamic Thresholds", False, "No feedback data yet (defaults to 0.70)", )
        status_report["WARN"] += 1
        status_report["FAIL"] -= 1 # Adjust so it doesn't count as a hard fail
except Exception as e:
    check("Feedback Loop State", False, str(e))

# Summary
print("\n" + "=" * 70)
print("📊 STATUS SUMMARY")
print("=" * 70)
print(f"  Passed : {status_report['PASS']}")
print(f"  Warnings: {status_report['WARN']}")
print(f"  Failed : {status_report['FAIL']}")

if status_report['FAIL'] == 0:
    print("\n  🟢 PARLA AI SYSTEM IS FULLY OPERATIONAL AND READY.")
else:
    print("\n  🔴 SYSTEM REQUIRES ATTENTION. Review failed items above.")
print("=" * 70)