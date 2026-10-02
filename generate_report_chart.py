"""
generate_report_chart.py
Generates a publication-grade, multi-panel strategic visualization of:
1. 2026 Territorial / Regional Dominance by Major Faction
2. Force Distribution & SAC Alignment Tiers
Outputs to Project/reports/eao_arms_territory_sac_chart_2026.png and eao_control_chart.png.
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

# Ensure output directory exists
output_dir = Path("Project/reports")
output_dir.mkdir(parents=True, exist_ok=True)

# Data Definition
factions = [
    "Arakan Army (AA - Rakhine/Paletwa)",
    "United Wa State Army (UWSA - Wa Region)",
    "KNDF / KNPP (Kayah / Karenni)",
    "Chinland Council / CB (Chin State)",
    "Kachin Independence Army (KIA - Kachin)",
    "Three Brotherhood (MNDAA/TNLA - N. Shan)",
    "KNU / KNLA (Kayin / Tanintharyi)",
    "PDF / NUG (Central Dry Zone Rural)",
    "Shan State Progress Party (SSPP - C. Shan)",
    "SAC Military Junta (National Admin Core)"
]

percentages = [92.6, 95.0, 85.0, 82.5, 75.0, 75.0, 65.0, 55.0, 42.0, 27.0]

tier_colors = [
    "#dc2626",  # Red - Total War (AA)
    "#7c3aed",  # Purple - Armed Neutrality (UWSA)
    "#db2777",  # Pink - Total War (KNDF)
    "#0284c7",  # Sky Blue - Total War (Chin)
    "#0d9488",  # Teal - Total War (KIA)
    "#2563eb",  # Blue - Total War (MNDAA/TNLA)
    "#059669",  # Green - Total War (KNU)
    "#d97706",  # Amber - Total War (PDF)
    "#ea580c",  # Orange - Neutrality/FPNCC (SSPP)
    "#1e293b"   # Slate Dark Navy - SAC Junta
]

plt.rcParams["font.family"] = "DejaVu Sans"
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.2), dpi=300, gridspec_kw={'width_ratios': [1.3, 0.7]})

# Panel 1: Horizontal Bar Chart of Territorial Dominance
y_pos = np.arange(len(factions))
bars = ax1.barh(y_pos, percentages, color=tier_colors, height=0.65, edgecolor="none")

ax1.set_yticks(y_pos)
ax1.set_yticklabels(factions, fontsize=8.5, fontweight="600", color="#1e293b")
ax1.invert_yaxis()
ax1.set_xlim(0, 108)
ax1.set_xlabel("Estimated Regional / Operational Dominance (%)", fontsize=9.0, fontweight="700", color="#334155")
ax1.set_title("Myanmar Territorial Dominance Matrix (Mid-to-Late 2026)", fontsize=11.0, fontweight="800", color="#0f172a", pad=12)

# Value annotations
for bar in bars:
    w = bar.get_width()
    ax1.text(w + 1.2, bar.get_y() + bar.get_height()/2, f"{w:.1f}%",
             va="center", ha="left", fontsize=8.0, fontweight="700", color="#1e293b")

ax1.grid(axis="x", linestyle="--", alpha=0.35, color="#94a3b8")
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)
ax1.spines["left"].set_color("#cbd5e1")
ax1.spines["bottom"].set_color("#cbd5e1")

# Panel 2: National Macro Landmass Distribution (Donut Chart)
macro_labels = [
    "Resistance / EAO Control\n(48.5%)",
    "Contested / Shifting Fronts\n(26.5%)",
    "SAC Junta Control\n(25.0%)"
]
macro_sizes = [48.5, 26.5, 25.0]
macro_colors = ["#2563eb", "#f59e0b", "#1e293b"]

wedges, texts, autotexts = ax2.pie(
    macro_sizes,
    labels=macro_labels,
    colors=macro_colors,
    autopct="%1.1f%%",
    startangle=140,
    pctdistance=0.75,
    wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2),
    textprops=dict(fontsize=8.0, fontweight="600", color="#1e293b")
)

for autotext in autotexts:
    autotext.set_color("white")
    autotext.set_fontsize(8.5)
    autotext.set_fontweight("bold")

ax2.set_title("National Sovereign Landmass Allocation\n(Macro Landscape 2026)", fontsize=10.5, fontweight="800", color="#0f172a", pad=12)

plt.tight_layout()

# Save paths
primary_path = Path("Project/reports/eao_arms_territory_sac_chart_2026.png")
root_path = Path("eao_control_chart.png")

fig.savefig(primary_path, bbox_inches="tight")
fig.savefig(root_path, bbox_inches="tight")
print(f"[+] Successfully generated charts at:\n    - {primary_path}\n    - {root_path}")
