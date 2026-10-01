"""
IoT-Integrated Predictive Maintenance Dataset — EDA Script
Dataset : https://www.kaggle.com/datasets/ziya07/iot-integrated-predictive-maintenance-dataset
Author  : Parla / IoT_Architect
Schema  : Timestamp, Machine_ID, Vibration, Acoustic_Signal, Temperature,
          Current, IMF_1, IMF_2, IMF_3, Label (0=healthy, 1=faulty)
Chaos Vectors: class imbalance, sensor drift, missing values, IMF collinearity
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # non-interactive backend; switch to "TkAgg" for live display
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd

# ── Config ────────────────────────────────────────────────────────────────────
DATA_PATH = Path("iot_predictive_maintenance.csv")  # update to actual filename
OUTPUT_DIR = Path("eda_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

SENSOR_COLS = ["Vibration", "Acoustic_Signal", "Temperature", "Current"]
IMF_COLS    = ["IMF_1", "IMF_2", "IMF_3"]
FEATURE_COLS = SENSOR_COLS + IMF_COLS
TARGET_COL  = "Label"
TIME_COL    = "Timestamp"
ID_COL      = "Machine_ID"

PALETTE = {0: "#4dd0e1", 1: "#ef5350"}  # Yin=teal (healthy), Chaos=red (faulty)
STYLE = "dark_background"

# ── Load ──────────────────────────────────────────────────────────────────────
def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        print(f"[ERROR] File not found: {path}")
        print("Download from Kaggle and place in the working directory.")
        sys.exit(1)

    df = pd.read_csv(path, parse_dates=[TIME_COL], infer_datetime_format=True)
    print(f"[LOAD] Shape: {df.shape}  |  Columns: {list(df.columns)}")
    return df


# ── 1. Data Quality Report ────────────────────────────────────────────────────
def data_quality_report(df: pd.DataFrame) -> None:
    print("\n" + "="*60)
    print("CHAOS VECTOR AUDIT — Data Quality Report")
    print("="*60)

    # Missing values
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    quality = pd.DataFrame({"missing_count": missing, "missing_%": missing_pct})
    print("\n[CHAOS-1] Missing Values:")
    print(quality[quality["missing_count"] > 0].to_string() or "  None detected.")

    # Duplicates
    dupes = df.duplicated().sum()
    print(f"\n[CHAOS-2] Duplicate Rows: {dupes} ({dupes/len(df)*100:.2f}%)")

    # Class balance
    label_counts = df[TARGET_COL].value_counts()
    label_pct = df[TARGET_COL].value_counts(normalize=True) * 100
    print(f"\n[CHAOS-3] Class Imbalance:")
    for cls in label_counts.index:
        print(f"  Label {cls}: {label_counts[cls]:,} ({label_pct[cls]:.1f}%)")
    imbalance_ratio = label_counts.max() / label_counts.min()
    print(f"  Imbalance Ratio: {imbalance_ratio:.2f}:1")

    # Sensor statistics
    print(f"\n[CHAOS-4] Sensor Descriptive Statistics:")
    print(df[FEATURE_COLS].describe().round(4).to_string())

    # Outlier detection via IQR
    print(f"\n[CHAOS-5] Outlier Count (IQR method, 1.5x fence):")
    for col in FEATURE_COLS:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        outliers = ((df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)).sum()
        print(f"  {col:<20}: {outliers:>6} ({outliers/len(df)*100:.2f}%)")


# ── 2. Class Distribution Plot ────────────────────────────────────────────────
def plot_class_distribution(df: pd.DataFrame) -> None:
    with plt.style.context(STYLE):
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle("CHAOS-3 · Class Distribution (Label: 0=Healthy, 1=Faulty)",
                     fontsize=13, color="white", fontweight="bold")

        counts = df[TARGET_COL].value_counts()
        colors = [PALETTE[i] for i in counts.index]

        # Bar chart
        axes[0].bar(counts.index.astype(str), counts.values, color=colors, width=0.4, edgecolor="white")
        axes[0].set_xlabel("Label", color="white")
        axes[0].set_ylabel("Count", color="white")
        axes[0].set_title("Sample Count", color="white")
        for spine in axes[0].spines.values():
            spine.set_edgecolor("#444")
        for i, v in enumerate(counts.values):
            axes[0].text(i, v + len(df) * 0.005, f"{v:,}", ha="center", color="white", fontsize=10)

        # Pie chart
        axes[1].pie(
            counts.values,
            labels=[f"{'Healthy' if i==0 else 'Faulty'} ({v/len(df)*100:.1f}%)"
                    for i, v in zip(counts.index, counts.values)],
            colors=colors,
            startangle=90,
            wedgeprops={"edgecolor": "white", "linewidth": 1.5},
            textprops={"color": "white"},
        )
        axes[1].set_title("Class Proportion", color="white")

        plt.tight_layout()
        out = OUTPUT_DIR / "01_class_distribution.png"
        plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="#1a1a2e")
        plt.close()
        print(f"[PLOT] Saved → {out}")


# ── 3. Sensor Distribution by Label ───────────────────────────────────────────
def plot_sensor_distributions(df: pd.DataFrame) -> None:
    with plt.style.context(STYLE):
        n_cols = 2
        n_rows = len(SENSOR_COLS + IMF_COLS) // n_cols + len(SENSOR_COLS + IMF_COLS) % n_cols
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(14, n_rows * 3))
        fig.suptitle("Sensor & IMF Distributions — Yin (Healthy) vs Chaos (Faulty)",
                     fontsize=13, color="white", fontweight="bold")
        axes = axes.flatten()

        all_cols = SENSOR_COLS + IMF_COLS
        for idx, col in enumerate(all_cols):
            ax = axes[idx]
            for label, color, name in [(0, PALETTE[0], "Healthy"), (1, PALETTE[1], "Faulty")]:
                subset = df[df[TARGET_COL] == label][col].dropna()
                ax.hist(subset, bins=50, alpha=0.65, color=color,
                        label=name, density=True, edgecolor="none")
            ax.set_title(col, color="white", fontsize=10)
            ax.set_xlabel("Value", color="#aaa", fontsize=8)
            ax.set_ylabel("Density", color="#aaa", fontsize=8)
            ax.legend(fontsize=8)
            ax.tick_params(colors="#aaa")
            for spine in ax.spines.values():
                spine.set_edgecolor("#333")

        # Hide unused axes
        for idx in range(len(all_cols), len(axes)):
            axes[idx].set_visible(False)

        plt.tight_layout()
        out = OUTPUT_DIR / "02_sensor_distributions.png"
        plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="#1a1a2e")
        plt.close()
        print(f"[PLOT] Saved → {out}")


# ── 4. Correlation Heatmap ────────────────────────────────────────────────────
def plot_correlation_heatmap(df: pd.DataFrame) -> None:
    with plt.style.context(STYLE):
        corr = df[FEATURE_COLS + [TARGET_COL]].corr()
        fig, ax = plt.subplots(figsize=(10, 8))
        fig.suptitle("CHAOS-5 · Feature Correlation — IMF Collinearity Check",
                     fontsize=13, color="white", fontweight="bold")

        im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
        plt.colorbar(im, ax=ax, label="Pearson r")

        ax.set_xticks(range(len(corr.columns)))
        ax.set_yticks(range(len(corr.columns)))
        ax.set_xticklabels(corr.columns, rotation=45, ha="right", color="white", fontsize=9)
        ax.set_yticklabels(corr.columns, color="white", fontsize=9)

        for i in range(len(corr)):
            for j in range(len(corr.columns)):
                val = corr.values[i, j]
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        fontsize=7, color="white" if abs(val) > 0.5 else "#888")

        plt.tight_layout()
        out = OUTPUT_DIR / "03_correlation_heatmap.png"
        plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="#1a1a2e")
        plt.close()
        print(f"[PLOT] Saved → {out}")


# ── 5. Time-Series Sensor Drift Plot ──────────────────────────────────────────
def plot_time_series(df: pd.DataFrame, n_machines: int = 3) -> None:
    machines = df[ID_COL].unique()[:n_machines]
    with plt.style.context(STYLE):
        fig, axes = plt.subplots(len(SENSOR_COLS), 1, figsize=(16, 12), sharex=False)
        fig.suptitle(f"CHAOS-1 · Sensor Drift Over Time — First {n_machines} Machines",
                     fontsize=13, color="white", fontweight="bold")

        colors_m = ["#4dd0e1", "#ffa726", "#66bb6a"]
        for col_idx, col in enumerate(SENSOR_COLS):
            ax = axes[col_idx]
            for m_idx, machine in enumerate(machines):
                subset = df[df[ID_COL] == machine].sort_values(TIME_COL)
                ax.plot(subset[TIME_COL], subset[col],
                        color=colors_m[m_idx % len(colors_m)],
                        linewidth=0.8, alpha=0.85, label=str(machine))
                # Overlay fault markers
                faulty = subset[subset[TARGET_COL] == 1]
                if not faulty.empty:
                    ax.scatter(faulty[TIME_COL], faulty[col],
                               color=PALETTE[1], s=8, alpha=0.5, zorder=3)
            ax.set_ylabel(col, color="white", fontsize=9)
            ax.tick_params(colors="#aaa", labelsize=7)
            ax.legend(fontsize=7, title="Machine", title_fontsize=7)
            for spine in ax.spines.values():
                spine.set_edgecolor("#333")

        axes[-1].set_xlabel("Timestamp", color="white")
        plt.tight_layout()
        out = OUTPUT_DIR / "04_time_series_drift.png"
        plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="#1a1a2e")
        plt.close()
        print(f"[PLOT] Saved → {out}")


# ── 6. Boxplots by Machine & Label ────────────────────────────────────────────
def plot_boxplots(df: pd.DataFrame) -> None:
    with plt.style.context(STYLE):
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("Sensor Spread by Machine & Fault State — Outlier Detection",
                     fontsize=13, color="white", fontweight="bold")
        axes = axes.flatten()

        for idx, col in enumerate(SENSOR_COLS):
            ax = axes[idx]
            data_by_label = [
                df[df[TARGET_COL] == label][col].dropna().values
                for label in [0, 1]
            ]
            bp = ax.boxplot(
                data_by_label,
                patch_artist=True,
                labels=["Healthy", "Faulty"],
                medianprops={"color": "white", "linewidth": 2},
            )
            for patch, color in zip(bp["boxes"], [PALETTE[0], PALETTE[1]]):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
            for whisker in bp["whiskers"]:
                whisker.set_color("#aaa")
            for cap in bp["caps"]:
                cap.set_color("#aaa")
            for flier in bp["fliers"]:
                flier.set(marker="o", markerfacecolor=PALETTE[1], markersize=2, alpha=0.4)

            ax.set_title(col, color="white", fontsize=10)
            ax.set_ylabel("Value", color="#aaa", fontsize=8)
            ax.tick_params(colors="white")
            for spine in ax.spines.values():
                spine.set_edgecolor("#333")

        plt.tight_layout()
        out = OUTPUT_DIR / "05_boxplots_by_label.png"
        plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="#1a1a2e")
        plt.close()
        print(f"[PLOT] Saved → {out}")


# ── 7. IMF Collinearity Scatter Matrix ────────────────────────────────────────
def plot_imf_scatter(df: pd.DataFrame) -> None:
    with plt.style.context(STYLE):
        n = len(IMF_COLS)
        fig, axes = plt.subplots(n, n, figsize=(12, 10))
        fig.suptitle("IMF Collinearity Scatter Matrix — Chaos Signal Decomposition",
                     fontsize=13, color="white", fontweight="bold")

        sample = df.sample(min(2000, len(df)), random_state=42)
        colors_arr = [PALETTE[int(l)] for l in sample[TARGET_COL]]

        for i, col_y in enumerate(IMF_COLS):
            for j, col_x in enumerate(IMF_COLS):
                ax = axes[i][j]
                if i == j:
                    for label, color in PALETTE.items():
                        d = sample[sample[TARGET_COL] == label][col_x]
                        ax.hist(d, bins=30, color=color, alpha=0.65, density=True)
                    ax.set_title(col_x, color="white", fontsize=8)
                else:
                    ax.scatter(sample[col_x], sample[col_y],
                               c=colors_arr, s=4, alpha=0.4)
                if i < n - 1:
                    ax.set_xticks([])
                if j > 0:
                    ax.set_yticks([])
                ax.tick_params(colors="#aaa", labelsize=6)
                for spine in ax.spines.values():
                    spine.set_edgecolor("#333")

        plt.tight_layout()
        out = OUTPUT_DIR / "06_imf_scatter_matrix.png"
        plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="#1a1a2e")
        plt.close()
        print(f"[PLOT] Saved → {out}")


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    df = load_data(DATA_PATH)

    data_quality_report(df)
    plot_class_distribution(df)
    plot_sensor_distributions(df)
    plot_correlation_heatmap(df)
    plot_time_series(df)
    plot_boxplots(df)
    plot_imf_scatter(df)

    print(f"\n[DONE] All EDA outputs saved to: {OUTPUT_DIR.resolve()}")
    print("Chaos vectors identified. Feed cleaned data to predictive model pipeline.")


if __name__ == "__main__":
    main()
