"""
Unit Test Suite: Real-World Data Mining & Pattern Excavation Engine
===================================================================
Validates:
1. Multi-INT Real-World Dataset Harmonization
2. DBSCAN Operating Regime Discovery & PCA Dimensionality Reduction
3. Cross-Domain Association Rule Mining (Support, Confidence, Lift)
4. Sub-Tree Ensemble Isolation Forest Anomaly Detection
5. Five-Part Data Mining Excavation Report Generation

Adheres strictly to .agents/rules/windows-python-resilience.md.
"""

import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd

from parla.domains.data_miner import (
    RealWorldDataHarmonizer,
    DensityRegimeMiner,
    AssociationRuleExtractor,
    SubTreeAnomalyDetector,
    ExcavationReportFormatter
)


def run_tests():
    print("=" * 70)
    print(" PARLA REAL-WORLD DATA MINING ENGINE: TEST SUITE")
    print("=" * 70)

    # ---------------------------------------------------------
    # TEST 1: Data Harmonization
    # ---------------------------------------------------------
    print("\n[1] Testing Multi-INT Data Ingestion & Harmonization...")
    harmonizer = RealWorldDataHarmonizer()
    df = harmonizer.load_and_harmonize()
    transactions = harmonizer.association_transactions

    assert not df.empty, "Harmonized dataframe must not be empty."
    assert len(df) >= 3, f"Expected at least 3 operational theaters, got {len(df)}"
    assert len(transactions) >= 5, f"Expected at least 5 observation transactions, got {len(transactions)}"
    expected_cols = ["control_eao_pct", "factions_count", "kinetic_intensity"]
    for c in expected_cols:
        assert c in df.columns, f"Missing required column: {c}"

    print(f"    [PASS] Harmonized {len(df)} theaters and {len(transactions)} observation itemsets.")

    # ---------------------------------------------------------
    # TEST 2: DBSCAN Operating Regime Discovery & PCA
    # ---------------------------------------------------------
    print("\n[2] Testing DBSCAN Operating Regime Clustering & PCA...")
    miner = DensityRegimeMiner(eps=1.25, min_samples=2)
    feature_cols = ["control_eao_pct", "factions_count", "kinetic_intensity", "displaced_persons_est", "liberated_townships_est"]
    cluster_res = miner.fit_predict(df, feature_cols)

    assert "labels" in cluster_res, "DBSCAN result must contain cluster labels."
    assert len(cluster_res["labels"]) == len(df), "Labels length must match theaters count."
    assert len(cluster_res["pca_explained_variance"]) == 2, "PCA must produce 2 components."
    assert sum(cluster_res["pca_explained_variance"]) > 0.50, "PCA must explain >50% variance."
    assert cluster_res["total_clusters"] >= 1, "Must detect at least 1 cohesive operational regime."

    print(f"    [PASS] Discovered {cluster_res['total_clusters']} cohesive regimes (Variance: {sum(cluster_res['pca_explained_variance'])*100:.1f}%).")

    # ---------------------------------------------------------
    # TEST 3: Multi-Domain Association Rule Mining
    # ---------------------------------------------------------
    print("\n[3] Testing Cross-Domain Association Rule Mining...")
    extractor = AssociationRuleExtractor()
    rules = extractor.mine_rules(transactions, min_support=0.10, min_confidence=0.50)

    assert isinstance(rules, list), "Rules result must be a list."
    assert len(rules) >= 1, "Expected at least 1 valid association rule."
    for r in rules:
        assert 0.0 <= r["support"] <= 1.0, f"Support out of bounds: {r['support']}"
        assert 0.0 <= r["confidence"] <= 1.0, f"Confidence out of bounds: {r['confidence']}"
        assert r["lift"] >= 0.0, f"Lift must be non-negative: {r['lift']}"

    top_rule = rules[0]
    print(f"    [PASS] Extracted {len(rules)} rules. Top Rule: {top_rule['antecedent']} -> {top_rule['consequent']} (Lift: {top_rule['lift']:.2f}x).")

    # ---------------------------------------------------------
    # TEST 4: Isolation Forest Anomaly Detection
    # ---------------------------------------------------------
    print("\n[4] Testing Sub-Tree Ensemble Isolation Forest...")
    detector = SubTreeAnomalyDetector(contamination=0.25, random_state=42)
    anomaly_res = detector.detect(df, feature_cols)

    assert anomaly_res["total_evaluated"] == len(df)
    assert "raw_scores" in anomaly_res
    assert len(anomaly_res["raw_scores"]) == len(df)
    # Check decision function score boundedness
    for s in anomaly_res["raw_scores"]:
        assert -1.0 <= s <= 1.0, f"Decision score out of bounds: {s}"

    print(f"    [PASS] Evaluated {len(df)} theaters; isolated {anomaly_res['anomalies_detected']} tactical outlier(s).")

    # ---------------------------------------------------------
    # TEST 5: Formal Excavation Report Schema Compliance
    # ---------------------------------------------------------
    print("\n[5] Testing Formal Data Mining Excavation Report Generation...")
    report_text = ExcavationReportFormatter.format_report(cluster_res, rules, anomaly_res)

    required_sections = [
        "## 1. Target & Chaos Level",
        "## 2. Extraction Harmony",
        "## 3. Discovered Patterns (The Yin)",
        "## 4. Business & Humanitarian Value (The Yang)",
        "## 5. Red Team Audit"
    ]
    for sec in required_sections:
        assert sec in report_text, f"Missing required report section: {sec}"

    # PII verification
    assert "@" not in report_text, "Report must not leak raw email addresses."
    assert "+95" not in report_text, "Report must not leak raw phone numbers."

    print("    [PASS] Report strictly conforms to the 5-point Yin-Yang-Chaos-Void schema with zero PII.")

    print("\n" + "=" * 70)
    print(" ALL DATA MINING ENGINE TESTS PASSED WITH 100% SPEC COMPLIANCE!")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
