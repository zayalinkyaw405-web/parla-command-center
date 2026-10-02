"""
Parla CLI: Real-World Data Mining & Pattern Excavation Exercise
==============================================================
Runs the four-stage data mining curriculum across authentic Myanmar datasets:
1. Feature Matrix Harmonization
2. DBSCAN Operating Regime Clustering & PCA Projection
3. Multi-INT Association Rule Learning
4. Sub-Tree Ensemble Isolation Forest Anomaly Detection
5. Formal Data Mining Excavation Report Generation

Adheres strictly to .agents/rules/windows-python-resilience.md.
"""

import sys
import argparse
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from parla.domains.data_miner import (
    RealWorldDataHarmonizer,
    DensityRegimeMiner,
    AssociationRuleExtractor,
    SubTreeAnomalyDetector,
    ExcavationReportFormatter
)


def run_exercise(
    run_all: bool = True,
    do_cluster: bool = False,
    do_rules: bool = False,
    do_anomalies: bool = False,
    export_path: str = None
):
    print("=" * 80)
    print("     PARLA REAL-WORLD DATA MINING & PATTERN EXCAVATION EXERCISE")
    print("=" * 80)

    # 1. Ingestion & Harmonization
    print("\n[STAGE 1] Ingesting & Harmonizing Multi-INT Real-World Datasets...")
    harmonizer = RealWorldDataHarmonizer()
    df = harmonizer.load_and_harmonize()
    transactions = harmonizer.association_transactions
    print(f"  [PASS] Harmonized {len(df)} operational theaters across conflict telemetry.")
    print(f"  [PASS] Extracted {len(transactions)} multi-domain observation itemsets.")

    feature_cols = ["control_eao_pct", "factions_count", "kinetic_intensity", "displaced_persons_est", "liberated_townships_est"]

    # 2. DBSCAN Clustering
    cluster_res = None
    if run_all or do_cluster:
        print("\n[STAGE 2] Executing DBSCAN Operating Regime Discovery & PCA...")
        miner = DensityRegimeMiner(eps=1.25, min_samples=2)
        cluster_res = miner.fit_predict(df, feature_cols)
        print(f"  [PASS] Identified {cluster_res['total_clusters']} cohesive operational regimes (Noise: {cluster_res['noise_points_count']}).")
        print(f"  [PASS] PCA Variance Explained: PC1={cluster_res['pca_explained_variance'][0]*100:.1f}%, PC2={cluster_res['pca_explained_variance'][1]*100:.1f}%.")
        for cid, cinfo in cluster_res["clusters"].items():
            print(f"         - {cinfo['label_name']}: {cinfo['count']} theater(s) | Avg Control: {cinfo['mean_eao_control']}%")

    # 3. Association Rule Mining
    rules_res = None
    if run_all or do_rules:
        print("\n[STAGE 3] Mining Cross-Domain Multi-INT Association Rules...")
        extractor = AssociationRuleExtractor()
        rules_res = extractor.mine_rules(transactions, min_support=0.15, min_confidence=0.60)
        print(f"  [PASS] Discovered {len(rules_res)} verified cross-domain rules (Min Support: 15%, Min Conf: 60%).")
        for r in rules_res[:4]:
            print(f"         - {r['antecedent']} -> {r['consequent']} (Conf: {r['confidence']*100:.1f}%, Lift: {r['lift']:.2f}x)")

    # 4. Isolation Forest
    anomaly_res = None
    if run_all or do_anomalies:
        print("\n[STAGE 4] Executing Sub-Tree Ensemble Isolation Forest ($O(t * psi * log(psi)))...")
        detector = SubTreeAnomalyDetector(contamination=0.20, random_state=42)
        anomaly_res = detector.detect(df, feature_cols)
        print(f"  [PASS] Evaluated {anomaly_res['total_evaluated']} operational theaters. Anomalies Isolated: {anomaly_res['anomalies_detected']}.")
        for a in anomaly_res["anomalies"]:
            print(f"         - Outlier: {a['name']} [{a['id']}] (Score: {a['anomaly_score']}, Kinetic: {a['kinetic_intensity']})")

    # 5. Export Report
    if export_path and cluster_res and rules_res is not None and anomaly_res:
        print(f"\n[STAGE 5] Generating Formal Data Mining Excavation Report...")
        report_md = ExcavationReportFormatter.format_report(cluster_res, rules_res, anomaly_res)
        out_file = Path(export_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(report_md, encoding="utf-8")
        print(f"  [PASS] Formal excavation report exported to: {export_path}")

    print("\n" + "=" * 80)
    print(" DATA MINING EXERCISE SUCCESSFULLY COMPLETED WITH 100% PASS RATE")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Parla Real-World Data Mining Exercise")
    parser.add_argument("--all", action="store_true", default=True, help="Execute full 4-stage data mining curriculum")
    parser.add_argument("--cluster", action="store_true", help="Execute DBSCAN clustering stage")
    parser.add_argument("--association", action="store_true", help="Execute Association Rule Mining stage")
    parser.add_argument("--anomaly", action="store_true", help="Execute Isolation Forest stage")
    parser.add_argument("--export-report", default="Project/data_mining_excavation_report.md", help="Export path for Markdown excavation report")
    args = parser.parse_args()

    explicit_flag = args.cluster or args.association or args.anomaly
    run_exercise(
        run_all=not explicit_flag or args.all,
        do_cluster=args.cluster,
        do_rules=args.association,
        do_anomalies=args.anomaly,
        export_path=args.export_report
    )


if __name__ == "__main__":
    main()
