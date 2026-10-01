"""
IoT Predictive Maintenance — Baseline Model Pipeline
Dataset  : https://www.kaggle.com/datasets/ziya07/iot-integrated-predictive-maintenance-dataset
Model    : Random Forest (baseline) + XGBoost (production)
Chaos    : C-1 class imbalance → class_weight + SMOTE
           C-4 missing values  → ffill + median imputation + gap flag
           C-5 temporal leakage → TimeSeriesSplit + chronological holdout
Metrics  : F1 (macro + faulty), PR-AUC, Confusion Matrix
"""

from __future__ import annotations

import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    classification_report,
    confusion_matrix,
    average_precision_score,
    f1_score,
    precision_recall_curve,
)
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

# ── Config ────────────────────────────────────────────────────────────────────
DATA_PATH   = Path("iot_predictive_maintenance.csv")
OUTPUT_DIR  = Path("model_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

TIME_COL    = "Timestamp"
ID_COL      = "Machine_ID"
TARGET_COL  = "Label"
SENSOR_COLS = ["Vibration", "Acoustic_Signal", "Temperature", "Current"]
IMF_COLS    = ["IMF_1", "IMF_2", "IMF_3"]
FEATURE_COLS = SENSOR_COLS + IMF_COLS

N_SPLITS      = 5      # TimeSeriesSplit folds
TEST_SIZE_PCT = 0.20   # chronological holdout fraction
MAX_GAP_FILL  = 5      # max consecutive NaN timesteps to forward-fill
RANDOM_STATE  = 42

# ── Load & Sort ───────────────────────────────────────────────────────────────
def load_and_sort(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=[TIME_COL], infer_datetime_format=True)
    df = df.sort_values(TIME_COL).reset_index(drop=True)
    print(f"[LOAD] Shape: {df.shape} | Sorted by {TIME_COL}")
    return df

# ── C-4: Missing Value Treatment ──────────────────────────────────────────────
def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    for col in FEATURE_COLS:
        gap_flag_col = f"{col}_gap_flag"
        df[gap_flag_col] = df[col].isnull().astype(int)

    # Forward-fill within Machine_ID groups, capped at MAX_GAP_FILL
    df = df.sort_values([ID_COL, TIME_COL])
    for col in FEATURE_COLS:
        df[col] = (
            df.groupby(ID_COL)[col]
            .transform(lambda s: s.fillna(method="ffill", limit=MAX_GAP_FILL))
        )

    # Remaining NaN → median per Machine_ID
    for col in FEATURE_COLS:
        df[col] = df.groupby(ID_COL)[col].transform(
            lambda s: s.fillna(s.median())
        )

    # Global fallback for machines with all-NaN
    df[FEATURE_COLS] = df[FEATURE_COLS].fillna(df[FEATURE_COLS].median())

    missing_after = df[FEATURE_COLS].isnull().sum().sum()
    print(f"[C-4] Missing after treatment: {missing_after}")
    return df

# ── Feature Engineering ───────────────────────────────────────────────────────
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values([ID_COL, TIME_COL])

    # Rolling statistics (window=5) — temporal context per machine
    # Applied within Machine_ID groups to avoid cross-machine contamination
    for col in SENSOR_COLS:
        grp = df.groupby(ID_COL)[col]
        df[f"{col}_roll_mean5"] = grp.transform(
            lambda s: s.rolling(5, min_periods=1).mean()
        )
        df[f"{col}_roll_std5"] = grp.transform(
            lambda s: s.rolling(5, min_periods=1).std().fillna(0)
        )

    # Machine_ID ordinal encoding (simple label encode)
    df["machine_enc"] = df[ID_COL].astype("category").cat.codes

    return df

# ── C-5: Temporal Train/Test Split ────────────────────────────────────────────
def temporal_split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cutoff_idx = int(len(df) * (1 - TEST_SIZE_PCT))
    train_df   = df.iloc[:cutoff_idx].copy()
    test_df    = df.iloc[cutoff_idx:].copy()
    print(
        f"[C-5] Train: {len(train_df):,} rows "
        f"({train_df[TIME_COL].min()} → {train_df[TIME_COL].max()})"
    )
    print(
        f"[C-5] Test : {len(test_df):,} rows "
        f"({test_df[TIME_COL].min()} → {test_df[TIME_COL].max()})"
    )
    return train_df, test_df

# ── SMOTE (manual lightweight version — no imbalanced-learn dependency) ───────
def smote_upsample(X: np.ndarray, y: np.ndarray, rng: np.random.Generator) -> tuple:
    """
    Simple random oversampling of minority class to 1:1 ratio.
    Full SMOTE requires imbalanced-learn; swap in if available:
        from imblearn.over_sampling import SMOTE
        X, y = SMOTE(random_state=RANDOM_STATE).fit_resample(X, y)
    """
    minority_mask = y == 1
    n_to_add      = (y == 0).sum() - minority_mask.sum()
    if n_to_add <= 0:
        return X, y

    minority_X  = X[minority_mask]
    oversample_idx = rng.integers(0, minority_X.shape[0], size=n_to_add)
    X_balanced  = np.vstack([X, minority_X[oversample_idx]])
    y_balanced  = np.concatenate([y, np.ones(n_to_add, dtype=y.dtype)])
    print(f"[C-1] SMOTE upsample: added {n_to_add:,} minority samples → balanced 1:1")
    return X_balanced, y_balanced

# ── Build Feature Matrix ──────────────────────────────────────────────────────
def get_feature_cols(df: pd.DataFrame) -> list[str]:
    base = FEATURE_COLS + ["machine_enc"]
    rolling = [c for c in df.columns if "_roll_" in c]
    gap_flags = [c for c in df.columns if "_gap_flag" in c]
    return base + rolling + gap_flags

# ── Cross-Validation ──────────────────────────────────────────────────────────
def cross_validate_temporal(
    train_df: pd.DataFrame,
    feature_cols: list[str],
) -> dict:
    X_train = train_df[feature_cols].values
    y_train = train_df[TARGET_COL].values

    tscv       = TimeSeriesSplit(n_splits=N_SPLITS, gap=10)
    fold_scores = []
    rng         = np.random.default_rng(RANDOM_STATE)

    print(f"\n[CV] TimeSeriesSplit with n_splits={N_SPLITS}, gap=10")
    for fold, (tr_idx, val_idx) in enumerate(tscv.split(X_train), 1):
        X_tr, y_tr   = X_train[tr_idx], y_train[tr_idx]
        X_val, y_val = X_train[val_idx], y_train[val_idx]

        # Scale — fit only on train fold
        scaler = StandardScaler()
        X_tr   = scaler.fit_transform(X_tr)
        X_val  = scaler.transform(X_val)

        # C-1: SMOTE on training fold only
        X_tr_bal, y_tr_bal = smote_upsample(X_tr, y_tr, rng)

        # Baseline: Random Forest with class_weight='balanced' as secondary guard
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=12,
            min_samples_leaf=5,
            class_weight="balanced",
            n_jobs=-1,
            random_state=RANDOM_STATE,
        )
        model.fit(X_tr_bal, y_tr_bal)

        y_pred     = model.predict(X_val)
        y_prob     = model.predict_proba(X_val)[:, 1]
        f1_macro   = f1_score(y_val, y_pred, average="macro", zero_division=0)
        f1_faulty  = f1_score(y_val, y_pred, pos_label=1, zero_division=0)
        pr_auc     = average_precision_score(y_val, y_prob) if y_val.sum() > 0 else 0.0

        fold_scores.append({
            "fold": fold,
            "f1_macro": f1_macro,
            "f1_faulty": f1_faulty,
            "pr_auc": pr_auc,
            "val_size": len(y_val),
            "faulty_in_val": int(y_val.sum()),
        })
        print(
            f"  Fold {fold}: F1-macro={f1_macro:.4f} | "
            f"F1-faulty={f1_faulty:.4f} | PR-AUC={pr_auc:.4f} | "
            f"val={len(y_val)} (faulty={int(y_val.sum())})"
        )

    mean_f1_macro  = np.mean([s["f1_macro"]  for s in fold_scores])
    mean_f1_faulty = np.mean([s["f1_faulty"] for s in fold_scores])
    mean_pr_auc    = np.mean([s["pr_auc"]    for s in fold_scores])
    print(
        f"\n[CV] Mean → F1-macro={mean_f1_macro:.4f} | "
        f"F1-faulty={mean_f1_faulty:.4f} | PR-AUC={mean_pr_auc:.4f}"
    )
    return {
        "folds": fold_scores,
        "mean_f1_macro": mean_f1_macro,
        "mean_f1_faulty": mean_f1_faulty,
        "mean_pr_auc": mean_pr_auc,
    }

# ── Final Model Training ──────────────────────────────────────────────────────
def train_final_model(
    train_df: pd.DataFrame,
    feature_cols: list[str],
) -> tuple:
    X_tr = train_df[feature_cols].values
    y_tr = train_df[TARGET_COL].values

    scaler = StandardScaler()
    X_tr   = scaler.fit_transform(X_tr)

    rng = np.random.default_rng(RANDOM_STATE)
    X_tr_bal, y_tr_bal = smote_upsample(X_tr, y_tr, rng)

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=15,
        min_samples_leaf=3,
        class_weight="balanced",
        n_jobs=-1,
        random_state=RANDOM_STATE,
    )
    model.fit(X_tr_bal, y_tr_bal)
    print("[TRAIN] Final model trained on full training set.")
    return model, scaler

# ── Evaluation ────────────────────────────────────────────────────────────────
def evaluate(
    model,
    scaler,
    test_df: pd.DataFrame,
    feature_cols: list[str],
) -> None:
    X_test = scaler.transform(test_df[feature_cols].values)
    y_test = test_df[TARGET_COL].values

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    print("\n" + "="*60)
    print("FINAL HOLDOUT EVALUATION (Chronological Last 20%)")
    print("="*60)
    print(classification_report(y_test, y_pred,
                                  target_names=["Healthy", "Faulty"],
                                  zero_division=0))

    pr_auc = average_precision_score(y_test, y_prob) if y_test.sum() > 0 else 0.0
    print(f"PR-AUC (Faulty class): {pr_auc:.4f}")

    # ── Confusion Matrix Plot ──────────────────────────────────────────────────
    with plt.style.context("dark_background"):
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.suptitle("IoT Predictive Maintenance — Model Evaluation",
                     fontsize=13, color="white", fontweight="bold")

        cm = confusion_matrix(y_test, y_pred)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                                       display_labels=["Healthy", "Faulty"])
        disp.plot(ax=axes[0], cmap="Blues", colorbar=False)
        axes[0].set_title("Confusion Matrix", color="white")
        axes[0].tick_params(colors="white")
        axes[0].set_xlabel("Predicted", color="white")
        axes[0].set_ylabel("Actual", color="white")

        # PR Curve
        precision, recall, _ = precision_recall_curve(y_test, y_prob)
        axes[1].plot(recall, precision, color="#4dd0e1", linewidth=2,
                     label=f"PR-AUC = {pr_auc:.3f}")
        axes[1].fill_between(recall, precision, alpha=0.15, color="#4dd0e1")
        axes[1].set_xlabel("Recall", color="white")
        axes[1].set_ylabel("Precision", color="white")
        axes[1].set_title("Precision-Recall Curve (Faulty Class)", color="white")
        axes[1].legend(fontsize=10)
        axes[1].set_xlim([0, 1])
        axes[1].set_ylim([0, 1.05])
        axes[1].axhline(y=y_test.mean(), color="#ef5350", linestyle="--",
                        linewidth=1, label=f"Baseline (random) = {y_test.mean():.3f}")
        axes[1].legend(fontsize=9)

        plt.tight_layout()
        out = OUTPUT_DIR / "model_evaluation.png"
        plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="#1a1a2e")
        plt.close()
        print(f"[PLOT] Saved → {out}")

# ── Feature Importance ────────────────────────────────────────────────────────
def plot_feature_importance(model, feature_cols: list[str]) -> None:
    importances = model.feature_importances_
    indices     = np.argsort(importances)[::-1][:15]  # top 15
    top_names   = [feature_cols[i] for i in indices]
    top_vals    = importances[indices]

    with plt.style.context("dark_background"):
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ["#4dd0e1" if "IMF" not in n else "#ffa726" for n in top_names]
        ax.barh(range(len(top_names)), top_vals[::-1], color=colors[::-1],
                edgecolor="none")
        ax.set_yticks(range(len(top_names)))
        ax.set_yticklabels(top_names[::-1], color="white", fontsize=9)
        ax.set_xlabel("Feature Importance (Gini)", color="white")
        ax.set_title("Top-15 Feature Importances — Yin Sensor vs Chaos IMF Components",
                     color="white", fontweight="bold")
        ax.tick_params(colors="#aaa")
        for spine in ax.spines.values():
            spine.set_edgecolor("#333")

        plt.tight_layout()
        out = OUTPUT_DIR / "feature_importance.png"
        plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="#1a1a2e")
        plt.close()
        print(f"[PLOT] Saved → {out}")

# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    df = load_and_sort(DATA_PATH)
    df = handle_missing(df)
    df = engineer_features(df)

    feature_cols = get_feature_cols(df)
    print(f"[FEATURES] Total features: {len(feature_cols)}")

    train_df, test_df = temporal_split(df)

    print(f"\n[C-1] Train label distribution:")
    vc = train_df[TARGET_COL].value_counts()
    for k, v in vc.items():
        print(f"  Label {k}: {v:,} ({v/len(train_df)*100:.1f}%)")

    cv_results = cross_validate_temporal(train_df, feature_cols)

    model, scaler = train_final_model(train_df, feature_cols)
    evaluate(model, scaler, test_df, feature_cols)
    plot_feature_importance(model, feature_cols)

    print("\n[DONE] Model pipeline complete.")
    print(f"  CV Mean F1-faulty : {cv_results['mean_f1_faulty']:.4f}")
    print(f"  CV Mean PR-AUC    : {cv_results['mean_pr_auc']:.4f}")
    print("  → Upgrade to XGBoost with scale_pos_weight if F1-faulty < 0.70")

if __name__ == "__main__":
    main()
