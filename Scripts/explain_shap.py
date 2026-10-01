"""
Explainable AI (SHAP) Pipeline for IoT Predictive Maintenance
Model      : Random Forest Classifier
Explainer  : TreeExplainer with tree_path_dependent perturbation
Artifacts  : Global Beeswarm Summary, Local Waterfall Plot, IMF Collinearity Attribution
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Safe import checking for third-party libraries
try:
    import shap
except ImportError:
    print("[ERROR] The 'shap' library is required. Install via: pip install shap")
    shap = None

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

# ── Paths & Parameters ────────────────────────────────────────────────────────
DATA_PATH   = Path("iot_predictive_maintenance.csv")
OUTPUT_DIR  = Path("shap_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

TIME_COL    = "Timestamp"
ID_COL      = "Machine_ID"
TARGET_COL  = "Label"
SENSOR_COLS = ["Vibration", "Acoustic_Signal", "Temperature", "Current"]
IMF_COLS    = ["IMF_1", "IMF_2", "IMF_3"]
FEATURE_COLS = SENSOR_COLS + IMF_COLS
RANDOM_STATE = 42


def load_and_preprocess(path: Path) -> tuple[pd.DataFrame, list[str]]:
    """Loads dataset, enforces chronological ordering, handles missingness, and constructs features."""
    if not path.exists():
        # Generate synthetic benchmark data mirroring Kaggle dataset if CSV not yet downloaded
        print(f"[WARN] {path} not found. Generating representative calibration set...")
        np.random.seed(RANDOM_STATE)
        n_samples = 2000
        timestamps = pd.date_range("2025-01-01", periods=n_samples, freq="10s")
        machines = [f"M_{i:02d}" for i in range(1, 6)]
        data = {
            TIME_COL: timestamps,
            ID_COL: np.random.choice(machines, size=n_samples),
            "Vibration": np.random.normal(2.5, 0.4, size=n_samples),
            "Acoustic_Signal": np.random.normal(45.0, 5.0, size=n_samples),
            "Temperature": np.random.normal(68.0, 4.0, size=n_samples),
            "Current": np.random.normal(12.0, 1.5, size=n_samples),
            "IMF_1": np.random.normal(0.8, 0.2, size=n_samples),
            "IMF_2": np.random.normal(0.4, 0.15, size=n_samples),
            "IMF_3": np.random.normal(0.2, 0.1, size=n_samples),
            TARGET_COL: np.random.choice([0, 1], size=n_samples, p=[0.96, 0.04]),
        }
        # Simulate physical fault signature coupling
        fault_mask = data[TARGET_COL] == 1
        data["Vibration"][fault_mask] += np.random.uniform(1.5, 3.5, size=fault_mask.sum())
        data["IMF_1"][fault_mask] += np.random.uniform(1.0, 2.0, size=fault_mask.sum())
        data["Temperature"][fault_mask] += np.random.uniform(10.0, 25.0, size=fault_mask.sum())
        df = pd.DataFrame(data)
    else:
        df = pd.read_csv(path, parse_dates=[TIME_COL])

    df = df.sort_values(TIME_COL).reset_index(drop=True)

    # Missing value mitigation with gap flags
    for col in FEATURE_COLS:
        if col in df.columns:
            df[f"{col}_gap_flag"] = df[col].isnull().astype(int)
            df[col] = df.groupby(ID_COL)[col].transform(lambda s: s.ffill(limit=5))
            df[col] = df.groupby(ID_COL)[col].transform(lambda s: s.fillna(s.median()))
            df[col] = df[col].fillna(df[col].median())

    # Rolling statistics
    for col in SENSOR_COLS:
        grp = df.groupby(ID_COL)[col]
        df[f"{col}_roll_mean5"] = grp.transform(lambda s: s.rolling(5, min_periods=1).mean())
        df[f"{col}_roll_std5"] = grp.transform(lambda s: s.rolling(5, min_periods=1).std().fillna(0))

    feature_cols = (
        FEATURE_COLS
        + [c for c in df.columns if "_roll_" in c]
        + [c for c in df.columns if "_gap_flag" in c]
    )
    return df, feature_cols


def train_baseline_model(df: pd.DataFrame, feature_cols: list[str]) -> tuple:
    """Trains a Random Forest baseline on chronological split for SHAP explanation."""
    cutoff = int(len(df) * 0.8)
    train_df = df.iloc[:cutoff]
    test_df = df.iloc[cutoff:]

    X_train = train_df[feature_cols].values
    y_train = train_df[TARGET_COL].values
    X_test = test_df[feature_cols].values
    y_test = test_df[TARGET_COL].values

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Balanced Random Forest
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    rf.fit(X_train_scaled, y_train)

    return rf, scaler, X_test_scaled, y_test, test_df


def analyze_imf_collinearity(df: pd.DataFrame, feature_cols: list[str]) -> pd.DataFrame:
    """
    Evaluates collinearity between raw kinematic telemetry and decomposed IMF features.
    Collinear features can split Shapley values; identifying correlation allows 
    grouped attribution interpretation for maintenance engineers.
    """
    imf_related = [c for c in feature_cols if any(k in c for k in ["IMF", "Vibration", "Acoustic"])]
    corr_matrix = df[imf_related].corr()
    corr_matrix.to_csv(OUTPUT_DIR / "imf_collinearity_matrix.csv")
    print(f"[COLLINEARITY] Evaluated {len(imf_related)} IMF/vibration features. Matrix saved.")
    return corr_matrix


def run_shap_analysis(
    model: RandomForestClassifier,
    X_test: np.ndarray,
    y_test: np.ndarray,
    test_df: pd.DataFrame,
    feature_names: list[str],
) -> None:
    if shap is None:
        raise RuntimeError("SHAP library is not available. Please install shap.")

    print("\n[SHAP] Initializing TreeExplainer (tree_path_dependent perturbation)...")
    # tree_path_dependent avoids evaluating impossible off-manifold combinations of collinear features
    explainer = shap.TreeExplainer(
        model,
        feature_perturbation="tree_path_dependent",
        model_output="probability",
    )

    # Compute SHAP explanation on a representative sample to balance fidelity and runtime
    sample_size = min(300, len(X_test))
    np.random.seed(RANDOM_STATE)
    sample_indices = np.random.choice(len(X_test), size=sample_size, replace=False)
    X_sample = X_test[sample_indices]
    y_sample = y_test[sample_indices]

    print(f"[SHAP] Calculating Shapley values across {sample_size} test observations...")
    explanation = explainer(X_sample)

    # Extract Faulty class (Class index 1)
    if len(explanation.shape) == 3 and explanation.shape[-1] == 2:
        exp_faulty = explanation[:, :, 1]
    else:
        exp_faulty = explanation

    # 1. Global Beeswarm Summary Plot
    plt.figure(figsize=(12, 7))
    shap.plots.beeswarm(exp_faulty, max_display=15, show=False)
    plt.title("SHAP Global Feature Attribution — Impact on Machine Fault Risk", fontsize=12, pad=15)
    plt.tight_layout()
    summary_path = OUTPUT_DIR / "shap_summary_beeswarm.png"
    plt.savefig(summary_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"[SHAP ARTIFACT] Saved Beeswarm Summary: {summary_path}")

    # 2. Local Explanation: Waterfall Plot for a True Positive or High-Risk Fault
    predicted_probs = model.predict_proba(X_sample)[:, 1]
    faulty_candidates = np.where((y_sample == 1) | (predicted_probs > 0.5))[0]

    target_idx = faulty_candidates[0] if len(faulty_candidates) > 0 else int(np.argmax(predicted_probs))
    actual_label = int(y_sample[target_idx])
    pred_risk = float(predicted_probs[target_idx])

    print(f"[SHAP] Generating Local Waterfall Plot for Sample #{target_idx} (Actual={actual_label}, PredRisk={pred_risk:.2%})...")
    plt.figure(figsize=(10, 6))
    shap.plots.waterfall(exp_faulty[target_idx], max_display=12, show=False)
    plt.title(
        f"Local Incident Root-Cause (Machine #{target_idx} | Risk: {pred_risk:.1%} | True State: {actual_label})",
        fontsize=11,
        pad=15,
    )
    plt.tight_layout()
    waterfall_path = OUTPUT_DIR / "shap_local_waterfall.png"
    plt.savefig(waterfall_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"[SHAP ARTIFACT] Saved Local Waterfall Plot: {waterfall_path}")

    # 3. Handle IMF Collinearity via Grouped Importance Audit
    # Group IMF features to show combined acoustic-vibration degradation impact
    abs_shap = np.abs(exp_faulty.values).mean(axis=0)
    imf_indices = [i for i, name in enumerate(feature_names) if "IMF" in name]
    raw_vibe_indices = [i for i, name in enumerate(feature_names) if "Vibration" in name]
    
    total_shap = abs_shap.sum()
    imf_importance_pct = (abs_shap[imf_indices].sum() / total_shap) * 100
    vibe_importance_pct = (abs_shap[raw_vibe_indices].sum() / total_shap) * 100

    print("\n" + "=" * 65)
    print("COLLINEAR FEATURE GROUP AUDIT (IMF vs Kinematic Telemetry)")
    print("=" * 65)
    print(f"  Total IMF Decomposition Attribution : {imf_importance_pct:.2f}% of total decision mass")
    print(f"  Raw Vibration & Rolling Stats Mass   : {vibe_importance_pct:.2f}% of total decision mass")
    print("  Note: TreeExplainer tree-path conditioning prevents off-manifold evaluation")
    print("        when IMFs and vibration components exhibit strong collinearity.")
    print("=" * 65)


def main() -> None:
    df, feature_cols = load_and_preprocess(DATA_PATH)
    analyze_imf_collinearity(df, feature_cols)
    model, scaler, X_test, y_test, test_df = train_baseline_model(df, feature_cols)
    run_shap_analysis(model, X_test, y_test, test_df, feature_cols)


if __name__ == "__main__":
    main()
