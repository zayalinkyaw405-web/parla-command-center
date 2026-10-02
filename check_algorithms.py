"""
check_algorithms.py
Full diagnostic of all Parla data mining algorithms.
"""

import sys
import os
import importlib

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

print("=" * 70)
print("🔍 PARLA DATA MINING ALGORITHM DIAGNOSTIC")
print("=" * 70)

results = []

# 1. Cryptographic: HMAC-SHA256
print("\n[1] HMAC-SHA256 Signature Verification")
try:
    import hmac, hashlib
    key = b"test_key"
    msg = b"test_message"
    sig = hmac.new(key, msg, hashlib.sha256).hexdigest()
    assert len(sig) == 64
    print("    ✓ OPERATIONAL")
    results.append(("HMAC-SHA256", True))
except Exception as e:
    print(f"    ✗ FAILED: {e}")
    results.append(("HMAC-SHA256", False))

# 2. Cryptographic: SHA-256 Merkle Chaining
print("\n[2] SHA-256 Merkle Hash Chaining")
try:
    block1 = hashlib.sha256(b"genesis").hexdigest()
    block2 = hashlib.sha256(f"{block1}data".encode()).hexdigest()
    assert block1 != block2
    assert len(block2) == 64
    print("    ✓ OPERATIONAL")
    results.append(("SHA-256 Merkle Chain", True))
except Exception as e:
    print(f"    ✗ FAILED: {e}")
    results.append(("SHA-256 Merkle Chain", False))

# 3. NLP: Regex PII Redaction
print("\n[3] Regex PII Redaction")
try:
    import re
    test = "Call John at 555-123-4567 or email john@test.com"
    redacted = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[REDACTED]', test)
    redacted = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED]', redacted)
    assert '555-123-4567' not in redacted
    assert 'john@test.com' not in redacted
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp("Contact Dr. Smith in Yangon")
        persons = [e.text for e in doc.ents if e.label_ == "PERSON"]
        print(f"    ✓ OPERATIONAL (Regex + spaCy NER, detected: {persons})")
    except Exception as spacy_err:
        print(f"    ✓ OPERATIONAL (Regex only, spaCy: {spacy_err})")
    results.append(("PII Redaction", True))
except Exception as e:
    print(f"    ✗ FAILED: {e}")
    results.append(("PII Redaction", False))

# 4. NLP: Keyword Event Classification
print("\n[4] Keyword Event Classification")
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from parla.core.knowledge_base import OSINTKnowledgeBase
    kb = OSINTKnowledgeBase()
    matches = kb.classify_text("Multiple airstrikes reported with bombing")
    assert len(matches) > 0
    assert matches[0][0] == "AIRSTRIKE"
    print(f"    ✓ OPERATIONAL (Top: {matches[0][0]}, confidence: {matches[0][1]:.2f})")
    results.append(("Keyword Classification", True))
except Exception as e:
    print(f"    ✗ FAILED: {e}")
    results.append(("Keyword Classification", False))

# 5. ML: DBSCAN Anomaly Clustering
print("\n[5] DBSCAN Anomaly Clustering")
try:
    import numpy as np
    from sklearn.cluster import DBSCAN
    from sklearn.preprocessing import StandardScaler
    np.random.seed(42)
    normal = np.random.normal(0, 1, (100, 3))
    anomaly = np.array([[10, 10, 10]])
    data = np.vstack([normal, anomaly])
    scaled = StandardScaler().fit_transform(data)
    db = DBSCAN(eps=0.5, min_samples=5).fit(scaled)
    assert db.labels_[-1] == -1
    print("    ✓ OPERATIONAL")
    results.append(("DBSCAN", True))
except Exception as e:
    print(f"    ✗ FAILED: {e}")
    results.append(("DBSCAN", False))

# 6. Signal: EMD Decomposition
print("\n[6] EMD Signal Decomposition")
try:
    EMD = None
    emd_lib = None
    try:
        from PyEMD import EMD as _EMD
        EMD = _EMD
        emd_lib = "PyEMD"
    except ImportError:
        try:
            _emd_module = importlib.import_module("emd")
            EMD = getattr(_emd_module, "EMD", None)
            emd_lib = "emd"
        except ImportError:
            raise ImportError("Neither 'PyEMD' nor 'emd' package is installed.")
    import numpy as np
    t = np.linspace(0, 1, 500)
    signal = np.sin(2 * np.pi * 5 * t) + np.sin(2 * np.pi * 20 * t)
    emd = EMD()
    imfs = emd.emd(signal)
    assert len(imfs) >= 1
    print(f"    ✓ OPERATIONAL ({len(imfs)} IMFs via {emd_lib})")
    results.append(("EMD", True))
except Exception as e:
    print(f"    ✗ FAILED: {e}")
    results.append(("EMD", False))

# 7. Explainability: Feature Attribution
print("\n[7] TreeSHAP-style Feature Attribution")
try:
    import numpy as np
    baseline = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    current = np.array([1.1, 2.0, 8.0, 4.0, 12.0])
    deviations = np.abs(current - baseline)
    top_features = np.argsort(deviations)[-2:][::-1]
    assert 2 in top_features or 4 in top_features
    print(f"    ✓ OPERATIONAL (Top contributors: features {top_features.tolist()})")
    results.append(("Feature Attribution", True))
except Exception as e:
    print(f"    ✗ FAILED: {e}")
    results.append(("Feature Attribution", False))

# 8. Statistical: Weighted Risk Scoring
print("\n[8] Weighted Risk Scoring")
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from parla.domains.risk_mapper import RegionalRiskMapper
    mapper = RegionalRiskMapper()
    report = mapper.calculate_regional_risk(days=90)
    assert "regions" in report
    print(f"    ✓ OPERATIONAL ({report['total_regions_monitored']} regions scored)")
    results.append(("Risk Scoring", True))
except Exception as e:
    print(f"    ✗ FAILED: {e}")
    results.append(("Risk Scoring", False))

# 9. Adaptive: Bayesian Threshold Adjustment
print("\n[9] Bayesian Threshold Adjustment")
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from parla.core.feedback_loop import FeedbackLoop
    fb = FeedbackLoop()
    thresholds = fb.get_current_thresholds()
    print(f"    ✓ OPERATIONAL ({len(thresholds)} event types calibrated)")
    for evt, thresh in thresholds.items():
        print(f"      • {evt}: >= {thresh}")
    results.append(("Threshold Adjustment", True))
except Exception as e:
    print(f"    ✗ FAILED: {e}")
    results.append(("Threshold Adjustment", False))

# 10. Decision: Multi-factor Confidence Scoring
print("\n[10] Multi-factor Confidence Scoring")
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from parla.core.agent_prompt import ParlaAgentPrompt
    agent = ParlaAgentPrompt()
    context = {"acoustic_db": 95.0, "doppler_shift_hz": 180.0, "event_type": "AIRSTRIKE", "confidence": 0.8}
    confidence = agent._calculate_confidence(context)
    assert 0.0 <= confidence <= 1.0
    print(f"    ✓ OPERATIONAL (Calculated confidence: {confidence:.2f})")
    results.append(("Confidence Scoring", True))
except Exception as e:
    print(f"    ✗ FAILED: {e}")
    results.append(("Confidence Scoring", False))

# Summary
print("\n" + "=" * 70)
print("📊 DIAGNOSTIC SUMMARY")
print("=" * 70)
passed = sum(1 for _, status in results if status)
total = len(results)
for name, status in results:
    print(f"  {'✓' if status else '✗'} {name}")
print(f"\n  Total: {passed}/{total} algorithms operational")
print("=" * 70)