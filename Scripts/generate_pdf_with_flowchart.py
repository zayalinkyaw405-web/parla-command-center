"""
Scripts/generate_pdf_with_flowchart.py
======================================
Renders a high-resolution styled architecture flowchart image and compiles 
an official ReportLab PDF Report embedding the diagram, Rust VoidNode specs, 
and Parla/Varla dual-personality system documentation.
"""

import sys
import os
import time
import hashlib
from pathlib import Path

# Ensure UTF-8 output encoding for Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

REPORTS_DIR = PROJECT_ROOT / "Project" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

FLOWCHART_IMG = REPORTS_DIR / "parla_varla_architecture_flowchart.png"
PDF_PATH = REPORTS_DIR / "Parla_Varla_Dual_Personality_Architecture_Report.pdf"

import matplotlib
matplotlib.use('Agg') # Headless rendering
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_flowchart_image():
    """Renders a styled high-res PNG flowchart matching the Mermaid classDef diagram."""
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    ax.set_facecolor('#090d16')
    fig.patch.set_facecolor('#090d16')
    ax.axis('off')

    # Color Palette Definitions
    c_parla = '#0f172a'
    s_parla = '#38bdf8'
    c_varla = '#1f1315'
    s_varla = '#ef4444'
    c_void = '#1e1b4b'
    s_void = '#818cf8'
    c_quantum = '#14532d'
    s_quantum = '#22c55e'
    c_market = '#1e293b'
    s_market = '#f59e0b'

    # Title Banner
    ax.text(6, 7.6, "PARLA / VARLA DUAL-PERSONALITY ARCHITECTURE & ENTANGLEMENT MAP", 
            ha='center', va='center', color='#38bdf8', fontsize=14, fontweight='bold')

    def draw_box(x, y, w, h, bg, stroke, title, subtitle):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2,rounding_size=0.15",
                                      linewidth=2, edgecolor=stroke, facecolor=bg)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h*0.65, title, ha='center', va='center', color='#ffffff', fontsize=9, fontweight='bold')
        ax.text(x + w/2, y + h*0.3, subtitle, ha='center', va='center', color='#94a3b8', fontsize=7.5)

    # 1. PARLA ETHICAL OSINT NODES (Left Column)
    ax.text(2.2, 6.9, "🛡️ PARLA ETHICAL OSINT (BLUE TEAM)", ha='center', color='#38bdf8', fontsize=10, fontweight='bold')
    draw_box(0.5, 5.7, 3.4, 0.8, c_parla, s_parla, "P-1. Ethical Recon Ingestor", "PII Redaction & spaCy NER")
    draw_box(0.5, 4.4, 3.4, 0.8, c_parla, s_parla, "P-2. Entity Resolution", "Deduplication & Canonical Linking")
    draw_box(0.5, 3.1, 3.4, 0.8, c_parla, s_parla, "P-3. Geolocation & EXIF", "NASA FIRMS + ADS-B Match")
    draw_box(0.5, 1.8, 3.4, 0.8, c_parla, s_parla, "P-4. Certified Report Builder", "ReportLab & Admiralty A1")

    # 2. VARLA ADVERSARIAL SHADOW NODES (Right Column)
    ax.text(9.8, 6.9, "😈 VARLA ADVERSARIAL SHADOW (RED TEAM)", ha='center', color='#ef4444', fontsize=10, fontweight='bold')
    draw_box(8.1, 5.7, 3.4, 0.8, c_varla, s_varla, "V-1. Darkweb Evasion Injector", "TOR Exit Node & Homoglyphs")
    draw_box(8.1, 4.4, 3.4, 0.8, c_varla, s_varla, "V-2. Disinformation Synthetic", "Adversarial Noise Vectoring")
    draw_box(8.1, 3.1, 3.4, 0.8, c_varla, s_varla, "V-3. EXIF & Deepfake Spoof", "GPS Anomaly Inserter")
    draw_box(8.1, 1.8, 3.4, 0.8, c_varla, s_varla, "V-4. Counter-Brief Generator", "Regression Test Suite")

    # 3. VOIDNODE RUST ZERO-TRUST CORE (Center Column)
    ax.text(6.0, 6.9, "🦀 VOIDNODE RUST CORE", ha='center', color='#818cf8', fontsize=10, fontweight='bold')
    draw_box(4.5, 4.8, 3.0, 1.4, c_void, s_void, "🔒 Zero-Trust Bridge", "Fail-Closed Isolation & HMAC")
    draw_box(4.5, 2.8, 3.0, 1.2, c_void, s_void, "🌳 SHA-256 Merkle Engine", "Leaf & Root Audit Proofs")

    # 4. QUANTUM & MONETIZATION LAYER (Bottom Bar)
    draw_box(1.5, 0.4, 4.2, 0.9, c_quantum, s_quantum, "⚛️ Post-Quantum Cryptography Engine", "NIST FIPS 204 ML-DSA Signatures")
    draw_box(6.3, 0.4, 4.2, 0.9, c_market, s_market, "💳 HTTP 402 x402 Crypto Paywall", "Solana & Polygon USDT/USDC")

    # Connecting Arrows
    arrow_props = dict(arrowstyle="->", color="#818cf8", lw=1.5, mutation_scale=12)
    ax.annotate("", xy=(4.5, 5.5), xytext=(3.9, 6.1), arrowprops=arrow_props)
    ax.annotate("", xy=(4.5, 5.2), xytext=(3.9, 4.8), arrowprops=arrow_props)
    ax.annotate("", xy=(4.5, 4.9), xytext=(3.9, 3.5), arrowprops=arrow_props)

    red_arrow_props = dict(arrowstyle="->", color="#ef4444", lw=1.5, mutation_scale=12, linestyle="--")
    ax.annotate("", xy=(7.5, 5.5), xytext=(8.1, 6.1), arrowprops=red_arrow_props)
    ax.annotate("", xy=(7.5, 5.2), xytext=(8.1, 4.8), arrowprops=red_arrow_props)
    ax.annotate("", xy=(7.5, 4.9), xytext=(8.1, 3.5), arrowprops=red_arrow_props)

    green_arrow_props = dict(arrowstyle="<->", color="#22c55e", lw=1.5, mutation_scale=12)
    ax.annotate("", xy=(6.0, 2.8), xytext=(6.0, 4.8), arrowprops=green_arrow_props)
    ax.annotate("", xy=(3.6, 1.3), xytext=(5.5, 2.8), arrowprops=green_arrow_props)
    ax.annotate("", xy=(8.4, 1.3), xytext=(6.5, 2.8), arrowprops=green_arrow_props)

    plt.xlim(0, 12)
    plt.ylim(0, 8)
    plt.tight_layout()
    plt.savefig(FLOWCHART_IMG, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"✅ Flowchart Image Rendered: {FLOWCHART_IMG}")

def compile_pdf_report():
    """Compiles the ReportLab PDF embedding the rendered architecture flowchart."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    CYAN_HEADER = colors.HexColor("#38bdf8")
    RED_ALERT = colors.HexColor("#ef4444")
    BLUE_ACCENT = colors.HexColor("#2563eb")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=CYAN_HEADER,
        spaceAfter=4
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=CYAN_HEADER,
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=4
    )

    story = []

    # Title & Header
    story.append(Paragraph("🛡️ PARLA / VARLA DUAL-PERSONALITY OSINT SYSTEM", ParagraphStyle('Sub', fontName='Helvetica-Bold', fontSize=9, textColor=BLUE_ACCENT)))
    story.append(Paragraph("ARCHITECTURAL SPECIFICATION & FLOWCHART REPORT", title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BLUE_ACCENT, spaceBefore=2, spaceAfter=8))

    # Executive Summary
    story.append(Paragraph("1. EXECUTIVE SUMMARY & ZERO-TRUST ARCHITECTURE", section_heading))
    summary_text = """
    This specification details the <b>Dual-Personality OSINT Framework</b>. <b>Parla</b> operates as the ethical Blue-Team engine (performing PII redaction, entity resolution, and NATO A1 Admiralty scoring). <b>Varla</b> acts as the adversarial Red-Team shadow (synthesizing darkweb evasion vectors, disinfo noise, and EXIF spoofing to regression-test Parla). The <b>VoidNode Rust Core</b> enforces SHA-256 Merkle proof auditability and fail-closed zero-trust payload routing.
    """
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 6))

    # Embedded Flowchart Diagram Image
    story.append(Paragraph("2. SYSTEM ARCHITECTURE & ENTANGLEMENT FLOWCHART", section_heading))
    if FLOWCHART_IMG.exists():
        # High resolution diagram embedding
        img_w, img_h = 540, 360
        story.append(Image(str(FLOWCHART_IMG), width=img_w, height=img_h))
    story.append(Spacer(1, 10))

    # Rust VoidNode Specifications
    story.append(Paragraph("3. RUST VOIDNODE SPECIFICATION & PROTOCOL MAP", section_heading))
    spec_data = [
        [Paragraph("<b>Component</b>", body_style), Paragraph("<b>Implementation Standard</b>", body_style), Paragraph("<b>Security Assurance</b>", body_style)],
        [Paragraph("Rust VoidNode Bridge", body_style), Paragraph("Zero-Trust Fail-Closed Memory Pipe", body_style), Paragraph("<font color='#059669'><b>Memory Safe (Rust)</b></font>", body_style)],
        [Paragraph("SHA-256 Merkle Engine", body_style), Paragraph("Binary Leaf & Root Proof Verification", body_style), Paragraph("<font color='#059669'><b>Tamper-Proof Audit</b></font>", body_style)],
        [Paragraph("Post-Quantum Engine", body_style), Paragraph("NIST FIPS 204 ML-DSA Signatures", body_style), Paragraph("<font color='#059669'><b>Quantum Resistant</b></font>", body_style)],
        [Paragraph("A2A Monetization", body_style), Paragraph("HTTP 402 x402 Crypto Paywall", body_style), Paragraph("<font color='#059669'><b>USDT/USDC Settlement</b></font>", body_style)]
    ]
    t_spec = Table(spec_data, colWidths=[140, 260, 140])
    t_spec.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_spec)

    doc.build(story)
    print(f"✅ Certified PDF Report Compiled Successfully: {PDF_PATH}")
    print("========================================================================")

if __name__ == "__main__":
    generate_flowchart_image()
    compile_pdf_report()
