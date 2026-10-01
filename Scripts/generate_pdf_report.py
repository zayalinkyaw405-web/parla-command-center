"""
Scripts/generate_pdf_report.py
Generates a 5-slide public-facing PDF report with clean typography and proper text wrapping.
Design: High-readability white background, dark-blue headings, crisp bullet points.
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors


def generate_public_report(filename: str = "Myanmar_Civilian_Protection_Report.pdf") -> str:
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()

    # Custom styles for clean, high-contrast readability
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=26,
        spaceAfter=14,
        textColor=colors.HexColor("#0F172A"),
        alignment=1  # Centered
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#475569"),
        spaceAfter=20,
        alignment=1  # Centered
    )

    date_style = ParagraphStyle(
        'CustomDate',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=24,
        alignment=1  # Centered
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=20,
        spaceAfter=16,
        textColor=colors.HexColor("#1E3A8A")  # Dark Blue
    )

    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        spaceAfter=14,
        textColor=colors.HexColor("#1E293B")
    )

    meta_box_style = ParagraphStyle(
        'MetaBox',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        alignment=1
    )

    story = []

    # =========================================================================
    # SLIDE 1 - Title & Scope
    # =========================================================================
    story.append(Spacer(1, 1.2 * inch))
    story.append(Paragraph("Protecting Civilians: Early-Warning Systems and Aerial Threats in Myanmar (2022-2026)", title_style))
    story.append(Paragraph("A Public Report on Humanitarian Technology, Community Resilience, and Civilian Safety", subtitle_style))
    story.append(Paragraph("Date: October 01, 2026", date_style))
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph("<b>Author:</b> Parla Autonomous Operations Research Node<br/><b>Classification:</b> Public Humanitarian Research Briefing", meta_box_style))
    story.append(Spacer(1, 2 * inch))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 2 - How the Early-Warning Network Operates
    # =========================================================================
    story.append(Paragraph("Slide 2: How the Early-Warning Network Operates", heading_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>&bull; Community Sensors:</b> Local, low-cost sound and environmental sensors are placed in vulnerable areas to listen for approaching aircraft and monitor the environment.", bullet_style))
    story.append(Paragraph("<b>&bull; Privacy First:</b> To protect communities, the system automatically blurs exact locations. Data is grouped by broad regions, ensuring no specific addresses or individuals are ever exposed.", bullet_style))
    story.append(Paragraph("<b>&bull; Offline Capability:</b> The network is designed to send alerts even when the internet or mobile networks are intentionally shut down by authorities.", bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 3 - Understanding the Patterns (2022–2026)
    # =========================================================================
    story.append(Paragraph("Slide 3: Understanding the Patterns (2022-2026)", heading_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>&bull; Sound and Satellite Correlation:</b> When local sensors detect the distinct sound of aircraft engines, the system cross-references this with public satellite data showing sudden fires or heat spikes on the ground.", bullet_style))
    story.append(Paragraph("<b>&bull; Regional Risk Mapping:</b> By grouping these verified events, the system identifies broad regional patterns of aerial activity. This helps humanitarian organizations understand where risks are highest without exposing specific villages to danger.", bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 4 - The Critical Window: Saving Lives Through Early Alerts
    # =========================================================================
    story.append(Paragraph("Slide 4: The Critical Window: Saving Lives Through Early Alerts", heading_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>&bull; The 4-to-8 Minute Advantage:</b> Once an aircraft is detected by the acoustic sensors, the local community alarm system triggers immediately. This provides civilians with a critical 4 to 8-minute window to seek shelter or evacuate safely.", bullet_style))
    story.append(Paragraph("<b>&bull; Resilience in Blackouts:</b> Because the alert system operates locally and does not rely on the internet, it continues to function and protect communities even during total communication blackouts.", bullet_style))
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 5 - Data Sources and Humanitarian Commitment
    # =========================================================================
    story.append(Paragraph("Slide 5: Data Sources and Humanitarian Commitment", heading_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph("<b>&bull; Public Data Sources:</b> This analysis relies on aggregated, publicly available data from the Armed Conflict Location & Event Data Project (ACLED), NASA satellite fire data, and UN humanitarian updates.", bullet_style))
    story.append(Paragraph("<b>&bull; Our Commitment:</b> This technology is built strictly to protect civilian lives. It does not collect tactical military data, and all information is handled with the utmost respect for the privacy, security, and safety of the communities involved.", bullet_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<i>This technology provides a practical model for protecting civilians in conflict zones around the world, demonstrating how open-source intelligence and community-level innovation can save lives.</i>", bullet_style))

    # Build the PDF
    try:
        doc.build(story)
        abs_path = os.path.abspath(filename)
        print(f"\n[OK] Success! Public report saved as '{abs_path}'")
        return abs_path
    except Exception as e:
        print(f"\n[ERROR] Error generating PDF: {e}")
        raise e


if __name__ == "__main__":
    out_file = "Myanmar_Civilian_Protection_Report.pdf"
    if len(sys.argv) > 1:
        out_file = sys.argv[1]
    generate_public_report(out_file)
