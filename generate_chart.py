"""
generate_chart.py
Generates high-resolution horizontal bar chart of estimated territorial/operational dominance
across ALL major Myanmar Ethnic Armed Organizations and SAC Junta (Q4 2026).
"""
import sys
import os
import subprocess

# Auto-relaunch under .venv python if matplotlib is missing in current environment
try:
    import matplotlib
except ImportError:
    venv_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "Scripts", "python.exe")
    if os.path.exists(venv_py) and sys.executable != venv_py:
        result = subprocess.run([venv_py] + sys.argv)
        sys.exit(result.returncode)
    raise

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Comprehensive data across all key ethnic factions and theater regions
categories = [
    "SAC Military Junta (National Admin)",
    "Arakan Army (AA - Rakhine)",
    "United Wa State Army (UWSA - Wa Region)",
    "KNDF / KNPP (Karenni State)",
    "Kachin Independence Army (KIA - Kachin)",
    "Northern Alliance (MNDAA/TNLA - N. Shan)",
    "KNU / KNLA (Kayin / Tanintharyi)",
    "SSPP / SSA-N (Central/N. Shan)",
    "RCSS / SSA-S (S. Shan Border)",
    "Mon RMA / NMSP-AD (Mon State)"
]

percentages = [42.0, 92.6, 95.0, 85.0, 78.0, 68.0, 62.0, 45.0, 40.0, 32.0]

colors = [
    "#1a237e",  # Deep Navy for Junta (SAC)
    "#d32f2f",  # Crimson for Arakan Army (AA)
    "#4a148c",  # Deep Purple for UWSA
    "#c2185b",  # Rose Pink for KNDF
    "#00695c",  # Teal for KIA
    "#1976d2",  # Vivid Blue for Northern Alliance (MNDAA/TNLA)
    "#0288d1",  # Sky Blue for KNU/KNLA
    "#f57c00",  # Amber/Orange for SSPP
    "#e65100",  # Dark Orange for RCSS
    "#689f38"   # Olive Green for Mon RMA/NMSP-AD
]

plt.rcParams["font.family"] = "DejaVu Sans"
fig, ax = plt.subplots(figsize=(7.5, 3.4), dpi=300)

y_pos = np.arange(len(categories))
bars = ax.barh(y_pos, percentages, color=colors, height=0.62, edgecolor="none")

# Style adjustments
ax.set_yticks(y_pos)
ax.set_yticklabels(categories, fontsize=7.8, fontweight="600", color="#1e293b")
ax.invert_yaxis()  # Top-down order

ax.set_xlim(0, 105)
ax.set_xlabel("Estimated Regional / Operational Dominance (%)", fontsize=8.0, fontweight="600", color="#334155")
ax.tick_params(axis="x", labelsize=7.5, colors="#475569")
ax.tick_params(axis="y", length=0)

# Value annotations on bars
for bar in bars:
    width = bar.get_width()
    ax.text(
        width + 1.2,
        bar.get_y() + bar.get_height() / 2,
        f"{width:.1f}%",
        va="center",
        ha="left",
        fontsize=7.8,
        fontweight="bold",
        color="#0f172a"
    )

# Spines & Grid
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color("#cbd5e1")
ax.spines["bottom"].set_color("#cbd5e1")
ax.xaxis.grid(True, linestyle="--", alpha=0.5, color="#e2e8f0")
ax.set_axisbelow(True)

plt.title("Q4 2026 Myanmar Conflict: Comprehensive EAO & Junta Territorial Matrix", 
          fontsize=9.0, fontweight="bold", pad=10, color="#0f172a", loc="left")

plt.tight_layout()

# Save in both locations
output_path1 = Path("eao_control_chart.png")
output_path2 = Path("Project/eao_control_chart.png")
output_path2.parent.mkdir(parents=True, exist_ok=True)

plt.savefig(output_path1, dpi=300, bbox_inches="tight")
plt.savefig(output_path2, dpi=300, bbox_inches="tight")
plt.close(fig)

print("Comprehensive chart generated successfully at eao_control_chart.png and Project/eao_control_chart.png")
