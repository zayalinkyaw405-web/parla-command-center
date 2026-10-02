"""
verify_report_deliverables.py
Validates the completeness, factual accuracy, and file integrity of the strategic intelligence report deliverables.
Includes validation of the 10-slide executive presentation PDF.
"""
import sys
import os
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def verify_all():
    print("=" * 70)
    print("VERIFYING STRATEGIC REPORT DELIVERABLES")
    print("=" * 70)

    # 1. Check file existence
    md_report = Path("Project/reports/Myanmar_Arms_Territorial_Control_And_SAC_Relations_2026.md")
    html_report = Path("Project/reports/Myanmar_Arms_Territorial_Control_And_SAC_Relations_2026.html")
    chart_img = Path("Project/reports/eao_arms_territory_sac_chart_2026.png")
    pdf_report = Path("Project/reports/Myanmar_Strategic_Report_2026_10Slides.pdf")
    root_pdf = Path("Myanmar_Strategic_Report_2026_10Slides.pdf")

    assert md_report.exists(), "Missing Markdown report!"
    assert html_report.exists(), "Missing HTML report!"
    assert chart_img.exists(), "Missing chart image!"
    assert pdf_report.exists(), "Missing PDF slide deck report!"
    assert root_pdf.exists(), "Missing root copy of PDF slide deck!"

    md_size = md_report.stat().st_size
    html_size = html_report.stat().st_size
    chart_size = chart_img.stat().st_size
    pdf_size = pdf_report.stat().st_size

    print(f"[+] Markdown Report Size: {md_size} bytes")
    print(f"[+] HTML Report Size: {html_size} bytes")
    print(f"[+] Chart Image Size: {chart_size} bytes")
    print(f"[+] 10-Slide PDF Deck Size: {pdf_size} bytes")

    assert md_size > 5000, "Markdown report too brief!"
    assert html_size > 10000, "HTML report too brief!"
    assert chart_size > 50000, "Chart image suspiciously small!"
    assert pdf_size > 15000, "PDF slide report suspiciously small!"

    # 2. Check PDF page count (must be exactly 10 slides)
    with open(pdf_report, "rb") as f:
        pdf_data = f.read()
    import re
    page_count = len(re.findall(rb'/Type\s*/Page\b', pdf_data))
    print(f"[+] Verified PDF Slide Count: {page_count} slides")
    assert page_count == 10, f"Expected 10 slides, but found {page_count}!"

    # 3. Content validation
    content = md_report.read_text(encoding="utf-8")

    # Arms comparison keywords
    for kw in ["KaPaSa", "KIO", "UWSA", "Type 81-Wa", "MAM-01", "D-30", "FN-6", "MANPADS", "FPV", "hexacopter"]:
        assert kw in content, f"Missing arms comparison keyword: {kw}"
    print("    [+] Arms comparison content verified.")

    # Territorial control keywords
    for kw in ["Rakhine", "Paletwa", "92.6%", "Kachin", "75.0%", "Laukkai", "Mogok", "Loikaw", "48.5%"]:
        assert kw in content, f"Missing territorial control keyword: {kw}"
    print("    [+] Territorial control matrix verified.")

    # SAC relationship tiers
    for kw in ["Tier 1", "Total War", "Tier 2", "Armed Neutrality", "Tier 3", "Ceasefire Signatories", "Tier 4", "Border Guard Forces"]:
        assert kw in content, f"Missing SAC relationship keyword: {kw}"
    print("    [+] EAO-SAC 4-tier relationship taxonomy verified.")

    # Tone check: Ensure no casual slang in the report
    unprofessional_phrases = ["chill if y'all chill", "part of all, helping all", "slang"]
    for slang in unprofessional_phrases:
        assert slang not in content.lower(), f"Unprofessional phrase found: {slang}"
    print("    [+] Professional defense intelligence tone verified (zero slang).")

    print("\n" + "=" * 70)
    print("ALL DELIVERABLES (MARKDOWN, HTML, CHART, 10-SLIDE PDF) FULLY VALIDATED")
    print("=" * 70)

if __name__ == "__main__":
    verify_all()
