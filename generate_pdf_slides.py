"""
generate_pdf_slides.py
Generates a publication-grade, 10-slide executive presentation report in PDF format (A4 Landscape).
Covers Myanmar Arms Dynamics, Territorial Power, and EAO-SAC Strategic Relationships (2026).
Uses ReportLab with high-density visual styling, data tables, and embedded chart figures.
"""
import sys
import os
import subprocess

# Auto-relaunch under .venv python if reportlab or matplotlib is missing
try:
    import reportlab
    import matplotlib
except ImportError:
    venv_py = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "Scripts", "python.exe")
    if os.path.exists(venv_py) and sys.executable != venv_py:
        result = subprocess.run([venv_py] + sys.argv)
        sys.exit(result.returncode)
    raise

from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas

PAGE_WIDTH, PAGE_HEIGHT = landscape(A4)

class SlideCanvas(canvas.Canvas):
    """Custom canvas that draws running professional header and footer on every slide."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_slide_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_slide_decorations(self, total_pages):
        self.saveState()
        
        # Slide Top Accent Bar
        self.setFillColor(colors.HexColor("#0f172a")) # Slate dark
        self.rect(0, PAGE_HEIGHT - 18, PAGE_WIDTH, 18, fill=1, stroke=0)
        
        # Header text
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#94a3b8"))
        self.drawString(28, PAGE_HEIGHT - 12.5, "PARLA AUTONOMOUS OPERATIONS RESEARCH NODE  |  DEFENSE INTELLIGENCE TELEMETRY 2026")
        self.drawRightString(PAGE_WIDTH - 28, PAGE_HEIGHT - 12.5, "NATO 6x6 ADMIRALTY STANDARD: A1 VERIFIED")
        
        # Footer Line
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.8)
        self.line(28, 22, PAGE_WIDTH - 28, 22)
        
        # Footer Text
        self.setFont("Helvetica", 7.0)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(28, 12, "CONFIDENTIAL OSINT DISPATCH  |  REF: PARLA-STRAT-DECK-2026-Q4  |  MYANMAR CONFLICT STUDY")
        page_str = f"Slide {self._pageNumber} of {total_pages}"
        self.drawRightString(PAGE_WIDTH - 28, 12, page_str)
        
        self.restoreState()


def create_10_slide_report():
    out_dir = Path("Project/reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / "Myanmar_Strategic_Report_2026_10Slides.pdf"
    root_pdf_path = Path("Myanmar_Strategic_Report_2026_10Slides.pdf")
    
    chart_path = out_dir / "eao_arms_territory_sac_chart_2026.png"
    if not chart_path.exists():
        chart_path = Path("eao_control_chart.png")

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=landscape(A4),
        leftMargin=28,
        rightMargin=28,
        topMargin=26,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette Typography Styles
    title_style = ParagraphStyle(
        'DeckTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a')
    )
    
    subtitle_style = ParagraphStyle(
        'DeckSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569')
    )

    slide_heading = ParagraphStyle(
        'SlideHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0f172a')
    )
    
    slide_subheading = ParagraphStyle(
        'SlideSubHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#2563eb')
    )

    body_style = ParagraphStyle(
        'DeckBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.5,
        textColor=colors.HexColor('#1e293b')
    )

    bold_body = ParagraphStyle(
        'DeckBoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.0,
        leading=8.8,
        textColor=colors.HexColor('#1e293b')
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell,
        fontName='Helvetica-Bold'
    )

    badge_red = ParagraphStyle(
        'BadgeRed',
        parent=table_cell,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#b91c1c')
    )
    
    badge_blue = ParagraphStyle(
        'BadgeBlue',
        parent=table_cell,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1d4ed8')
    )

    badge_purple = ParagraphStyle(
        'BadgePurple',
        parent=table_cell,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#6b21a8')
    )

    story = []

    # =========================================================================
    # SLIDE 1: Title Slide & Executive Context
    # =========================================================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("STRATEGIC DEFENSE INTELLIGENCE REPORT (2026)", slide_subheading))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Myanmar Arms Dynamics, Territorial Power & EAO-SAC Strategic Relationships", title_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("An Operations Research Synthesis of Battlefield Telemetry, Domestic Manufacturing, Force Balances, and Sovereign Fragmentation", subtitle_style))
    story.append(Spacer(1, 18))

    exec_summary_data = [
        [
            Paragraph("<b>EVIDENTIARY HORIZON</b>", table_cell_bold),
            Paragraph("<b>TERRITORIAL STATUS</b>", table_cell_bold),
            Paragraph("<b>FORCE ASYMMETRY</b>", table_cell_bold),
            Paragraph("<b>STRATEGIC POSTURE</b>", table_cell_bold)
        ],
        [
            Paragraph("<b>Multi-INT Fusion:</b> 2021–Q4 2026 battlefield observation. Integrates verified OSINT, NATO 6x6 Admiralty assessments, satellite thermal telemetry (NASA FIRMS), and flight radar sorties.", table_cell),
            Paragraph("<b>State Collapse:</b> The military junta (SAC) controls only 21%–33% of national landmass, isolated strictly to central urban fortified enclaves. Resistance/EAOs govern 48.5% of territory.", table_cell),
            Paragraph("<b>Drone & Air Denial:</b> SAC air dominance neutralized below 3,800m by FN-6/HN-5 MANPADS. Resistance forces lead an asymmetric drone revolution with 25,000+ synchronized FPV/hexacopter sorties.", table_cell),
            Paragraph("<b>Polycentric Governance:</b> A 4-tier posture taxonomy classifies EAOs from total offensive eradication (3BA, K7) to armed neutrality (UWSA), fractured ceasefires, and proxy militias.", table_cell)
        ]
    ]
    t1 = Table(exec_summary_data, colWidths=[192, 192, 192, 192])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t1)
    
    story.append(Spacer(1, 20))
    doc_creds = [
        [
            Paragraph("<b>Research Node:</b> Parla Autonomous Operations Research Hub", table_cell),
            Paragraph("<b>Classification:</b> STRATEGIC OSINT // REL TO HUMANITARIAN PARTNERS", table_cell),
            Paragraph("<b>Published:</b> Mid-to-Late 2026 Edition", table_cell)
        ]
    ]
    t_creds = Table(doc_creds, colWidths=[256, 256, 256])
    t_creds.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f1f5f9')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 6)
    ]))
    story.append(t_creds)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 2: National Macro Sovereign Landmass Allocation
    # =========================================================================
    story.append(Paragraph("PILLAR 2: SPATIAL TELEMETRY & SOVEREIGN LANDMASS", slide_subheading))
    story.append(Paragraph("Slide 2: National Macro Sovereign Allocation (2026 Landscape)", slide_heading))
    story.append(Spacer(1, 8))

    macro_table_data = [
        [
            Paragraph("SOVEREIGNTY CATEGORY", table_header),
            Paragraph("LANDMASS ALLOCATION", table_header),
            Paragraph("OPERATIONAL GOVERNANCE & CONTROLLED ASSETS", table_header)
        ],
        [
            Paragraph("<b>Resistance & EAO Controlled</b>", table_cell_bold),
            Paragraph("<font color='#1d4ed8'><b>48.5%</b> (Range: 42% – 55%)</font>", table_cell),
            Paragraph("Continuous liberated peripheral mountain belts, international border crossings with China, Thailand, and India, and lucrative jade/rare-earth/gemstone extractive corridors.", table_cell)
        ],
        [
            Paragraph("<b>Actively Contested Frontlines</b>", table_cell_bold),
            Paragraph("<font color='#b45309'><b>26.5%</b> (Range: 20% – 37%)</font>", table_cell),
            Paragraph("Shifting rural-to-urban transition zones, interdicted highways (Asian Highway 1), active artillery/bombardment corridors, and dynamic PDF-junta skirmish sectors in Sagaing/Magway.", table_cell)
        ],
        [
            Paragraph("<b>SAC Junta Administrative Core</b>", table_cell_bold),
            Paragraph("<font color='#0f172a'><b>25.0%</b> (Range: 21% – 33%)</font>", table_cell),
            Paragraph("Strictly confined to heavily fortified garrison enclaves: Naypyidaw administrative fortress, Yangon commercial port, Mandalay city core, and fortified riverine naval stations.", table_cell)
        ]
    ]
    t2 = Table(macro_table_data, colWidths=[180, 160, 428])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 7),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (0, 2), (-1, 2), colors.white),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#f8fafc')),
    ]))
    story.append(t2)
    story.append(Spacer(1, 14))

    # Analytical takeaways
    s2_points = [
        [
            Paragraph("<b>Strategic Fragmentation:</b> The SAC has lost the ability to execute nationwide administrative governance. The military operates not as a sovereign government, but as a heavily besieged urban garrison army reliant on punitive standoff aerial bombardments.", body_style),
            Paragraph("<b>Logistical Severance:</b> Over 80% of overland arterial highways connecting the central plains to frontier borders are severed by resistance checkpoints. Ground supply columns require multi-battalion armored escorts that frequently succumb to ambushes.", body_style)
        ]
    ]
    t2_pts = Table(s2_points, colWidths=[384, 384])
    t2_pts.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f1f5f9')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 8)
    ]))
    story.append(t2_pts)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 3: State-by-State Territorial Dominance Matrix
    # =========================================================================
    story.append(Paragraph("PILLAR 2: REGIONAL CONTROL ANALYTICS", slide_subheading))
    story.append(Paragraph("Slide 3: State-by-State Territorial Dominance Matrix (2026)", slide_heading))
    story.append(Spacer(1, 6))

    state_matrix_data = [
        [
            Paragraph("FACTION / COALITION", table_header),
            Paragraph("THEATER / STATE", table_header),
            Paragraph("DOMINANCE", table_header),
            Paragraph("KEY LIBERATED TOWNSHIPS & ASSETS", table_header),
            Paragraph("SAC REMNANT GARRISONS", table_header)
        ],
        [
            Paragraph("Arakan Army (AA)", table_cell_bold),
            Paragraph("Rakhine & Paletwa", table_cell),
            Paragraph("<b>92.6%</b>", badge_red),
            Paragraph("Paletwa, Kyauktaw, Mrauk-U, Minbya, Ponnagyun, Buthidaung, Maungdaw, Thandwe", table_cell),
            Paragraph("Sittwe capital & Kyaukphyu deep-sea port perimeter", table_cell)
        ],
        [
            Paragraph("United Wa State Army (UWSA)", table_cell_bold),
            Paragraph("Wa Special Region 2", table_cell),
            Paragraph("<b>95.0%–100%</b>", badge_purple),
            Paragraph("Panghsang, Mong Pawk, Hopang, Panlong, Military Region 171", table_cell),
            Paragraph("Zero junta presence; complete de facto statehood", table_cell)
        ],
        [
            Paragraph("KNDF / KNPP / IEC", table_cell_bold),
            Paragraph("Kayah (Karenni) State", table_cell),
            Paragraph("<b>85.0%</b>", badge_blue),
            Paragraph("Demoso, Bawlake, Hpasawng, Mese border gate, Mawchi tungsten mines", table_cell),
            Paragraph("Loikaw Regional Operations Command hilltop", table_cell)
        ],
        [
            Paragraph("Chinland Council / CB", table_cell_bold),
            Paragraph("Chin State", table_cell),
            Paragraph("<b>82.5%</b>", badge_blue),
            Paragraph("Mindat, Kanpetlet, Matupi, Tedim, Rihkhawdar border crossing", table_cell),
            Paragraph("Portions of Hakha & Falam hilltops under siege", table_cell)
        ],
        [
            Paragraph("Kachin Independence Army (KIA)", table_cell_bold),
            Paragraph("Kachin & N. Shan", table_cell),
            Paragraph("<b>75.0%</b>", badge_blue),
            Paragraph("Lweje China border port, Pangwa & Sadung rare earths, Sumprabum, Laiza", table_cell),
            Paragraph("Myitkyina capital & Bhamo airport perimeter", table_cell)
        ],
        [
            Paragraph("Three Brotherhood (MNDAA/TNLA)", table_cell_bold),
            Paragraph("Northern Shan State", table_cell),
            Paragraph("<b>75.0%</b>", badge_blue),
            Paragraph("Laukkai, Chinshwehaw, Kunlong, Kyaukme, Hsipaw, Mogok ruby valley", table_cell),
            Paragraph("Contested outskirts of Naungcho & Lashio buffer", table_cell)
        ],
        [
            Paragraph("KNU / KNLA Brigades 1–7", table_cell_bold),
            Paragraph("Kayin State & Tanintharyi", table_cell),
            Paragraph("<b>65.0%</b>", badge_blue),
            Paragraph("Kawthoolei administrative districts, Asian Highway 1 interdiction", table_cell),
            Paragraph("Hpa-an capital & fortified highway bases", table_cell)
        ],
        [
            Paragraph("People's Defence Forces (NUG)", table_cell_bold),
            Paragraph("Central Dry Zone", table_cell),
            Paragraph("<b>55.0% (Rural)</b>", table_cell),
            Paragraph("Depayin, Tabayin, Gangaw, Pauk, Chaung-U rural valleys (Pa-Ah-Ya)", table_cell),
            Paragraph("Urban cores (Monywa, Sagaing, Mandalay)", table_cell)
        ]
    ]
    t3 = Table(state_matrix_data, colWidths=[130, 110, 75, 260, 193])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 4.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.white])
    ]))
    story.append(t3)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 4: Strategic Border Gates & Extractive Mineral Basins
    # =========================================================================
    story.append(Paragraph("PILLAR 2: GEO-ECONOMIC TELEMETRY", slide_subheading))
    story.append(Paragraph("Slide 4: Strategic Border Corridors & Natural Resource Basins", slide_heading))
    story.append(Spacer(1, 8))

    border_data = [
        [
            Paragraph("GEOPOLITICAL CHOKEPOINT", table_header),
            Paragraph("CONTROLLING ACTOR", table_header),
            Paragraph("ECONOMIC & MILITARY SIGNIFICANCE", table_header)
        ],
        [
            Paragraph("<b>Chinshwehaw & Laukkai Gate</b> (China)", table_cell_bold),
            Paragraph("MNDAA (Kokang Special Region)", table_cell),
            Paragraph("Primary overland bilateral trade gateway; generates massive customs revenue; completely severed from Naypyidaw treasury.", table_cell)
        ],
        [
            Paragraph("<b>Pangwa & Sadung Basins</b> (China)", table_cell_bold),
            Paragraph("Kachin Independence Army (KIA)", table_cell),
            Paragraph("Global hub of heavy rare-earth extraction (dysprosium/terbium); provides crucial leverage over regional clean-tech manufacturing.", table_cell)
        ],
        [
            Paragraph("<b>Myawaddy / Mae Sot Corridor</b> (Thailand)", table_cell_bold),
            Paragraph("KNU / KNLA (Asian Highway 1)", table_cell),
            Paragraph("Historically routed >70% of overland border commerce with Thailand; SAC customs authority extinguished; approach roads interdicted.", table_cell)
        ],
        [
            Paragraph("<b>Mogok Gemstone Valley</b> (Mandalay/Shan)", table_cell_bold),
            Paragraph("Ta'ang National Liberation Army (TNLA)", table_cell),
            Paragraph("Historic 'Valley of Rubies'; world-class sapphire and ruby mines seized during Operation 1027 Phase 2; junta completely evicted.", table_cell)
        ],
        [
            Paragraph("<b>Hpakant Jade Quarry Corridor</b> (Kachin)", table_cell_bold),
            Paragraph("Kachin Independence Army (KIA)", table_cell),
            Paragraph("Multi-billion dollar jadeite extractive basin; provides independent fiscal self-sufficiency for KIA multi-brigade standing forces.", table_cell)
        ]
    ]
    t4 = Table(border_data, colWidths=[190, 170, 408])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 6.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.white])
    ]))
    story.append(t4)
    story.append(Spacer(1, 14))

    s4_box = [
        [
            Paragraph("<b>Fiscal Inversion:</b> The loss of border gates and resource extraction nodes has depleted the SAC of foreign currency reserves. Simultaneously, EAO administrations have established institutional customs and taxation bureaus, transforming insurgent movements into fully funded state-like governance entities.", body_style)
        ]
    ]
    t4_box = Table(s4_box, colWidths=[768])
    t4_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eff6ff')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#bfdbfe')),
        ('PADDING', (0, 0), (-1, -1), 8)
    ]))
    story.append(t4_box)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 5: Domestic Defense Industrial Base (KaPaSa vs. EAOs)
    # =========================================================================
    story.append(Paragraph("PILLAR 1: COMPARATIVE DEFENSE INDUSTRIES", slide_subheading))
    story.append(Paragraph("Slide 5: Domestic Manufacturing: SAC KaPaSa vs. EAO Armories", slide_heading))
    story.append(Spacer(1, 8))

    arms_data = [
        [
            Paragraph("ARMAMENT BUREAU", table_header),
            Paragraph("FACILITIES & BASE", table_header),
            Paragraph("CORE PRODUCTION LINES & CALIBERS", table_header),
            Paragraph("SUPPLY CHAIN VULNERABILITIES", table_header)
        ],
        [
            Paragraph("<b>SAC KaPaSa (DDI)</b><br/>Directorate of Defence Industries", table_cell_bold),
            Paragraph("25 heavy factories along Irrawaddy corridor (Magway, Bago, Mandalay)", table_cell),
            Paragraph("• MA-1/2/3/4 (5.56x45mm NATO)<br/>• MA-15 GPMG (7.62x51mm NATO)<br/>• MAM-01/02 MLRS (122mm/240mm)<br/>• FAB-500 & ODAB-500 thermobaric bombs", table_cell),
            Paragraph("Critical dependence on imported CNC spares, alloy steels, and chemical precursors via Singapore/China maritime routes.", table_cell)
        ],
        [
            Paragraph("<b>KIO Technical Dept</b><br/>Kachin Independence Organization", table_cell_bold),
            Paragraph("3 armories in Laiza and Mai Ja Yang frontier", table_cell),
            Paragraph("• K-09 / K-10 rifles (7.62x39mm Soviet)<br/>• 60mm & 81mm cast-iron mortar shells<br/>• Directional bounding fragmentation mines", table_cell),
            Paragraph("Smuggled bar-stock steel and explosive chemical precursors sourced across China border crossings.", table_cell)
        ],
        [
            Paragraph("<b>UWSA Armament Bureau</b><br/>Wa Special Region 2", table_cell_bold),
            Paragraph("4 industrial facilities in Panghsang & Mong Pawk", table_cell),
            Paragraph("• Type 81-Wa assault rifles (7.62x39mm)<br/>• 7.62x39mm & 12.7x108mm ammunition stamping<br/>• 120mm heavy siege mortar systems", table_cell),
            Paragraph("Heavy industrial reliance on cross-border Chinese component and raw metal trade pipelines.", table_cell)
        ],
        [
            Paragraph("<b>Decentralized PDF Cells</b><br/>Anti-Coup Resistance Clandestine", table_cell_bold),
            Paragraph("Hundreds of mobile distributed jungle workshops", table_cell),
            Paragraph("• FGC-9 Mk II carbines (9x19mm Parabellum)<br/>• Electrochemical machined (ECM) rifled barrels<br/>• Modular 3D-printed drone drop release hooks", table_cell),
            Paragraph("Vulnerable to localized raw filament shortages, lithium-polymer drone battery seizures, and junta power blackouts.", table_cell)
        ]
    ]
    t5 = Table(arms_data, colWidths=[150, 150, 240, 228])
    t5.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 6.0),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.white])
    ]))
    story.append(t5)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 6: Comparative Artillery, MLRS & Siege Ordnance
    # =========================================================================
    story.append(Paragraph("PILLAR 1: KINETIC INDIRECT FIREPOWER", slide_subheading))
    story.append(Paragraph("Slide 6: Comparative Artillery, MLRS & Siege Systems", slide_heading))
    story.append(Spacer(1, 8))

    artillery_data = [
        [
            Paragraph("SYSTEM DOMAIN", table_header),
            Paragraph("SAC MILITARY JUNTA ARSENAL", table_header),
            Paragraph("RESISTANCE & EAO ARSENAL", table_header),
            Paragraph("OPERATIONAL ASYMMETRY & OUTCOME", table_header)
        ],
        [
            Paragraph("<b>Infantry Mortars</b>", table_cell_bold),
            Paragraph("MA-6 (60mm), MA-8 (81mm), MA-9 (120mm heavy mortars). Standard factory ammunition.", table_cell),
            Paragraph("KIO 60/81mm, UWSA 120mm siege mortars, improvised drone-dropped mortar bombs.", table_cell),
            Paragraph("EAOs achieve superior tactical flexibility through drone-spotted rapid shoot-and-scoot mortar deployments.", table_cell)
        ],
        [
            Paragraph("<b>Field Tube Artillery</b>", table_cell_bold),
            Paragraph("122mm D-30 Howitzers, 105mm OTO Melara, 155mm Soltam heavy guns. Static firebases.", table_cell),
            Paragraph("Captured 122mm D-30 batteries (captured en masse during Op 1027), improvised siege mortars.", table_cell),
            Paragraph("SAC retains maximum firing range (>15km) but suffers fatal garrison isolation and high ammunition burn rates under siege.", table_cell)
        ],
        [
            Paragraph("<b>Multiple Launch Rockets (MLRS)</b>", table_cell_bold),
            Paragraph("MAM-01 (122mm 40-tube truck-mounted), MAM-02 (240mm heavy saturation rockets).", table_cell),
            Paragraph("Type 90 (122mm MLRS - UWSA/MNDAA), 107mm Type 63 single-tube standoff rockets.", table_cell),
            Paragraph("SAC uses unguided MLRS for broad area terror; resistance utilizes 107mm rockets for precision standoff strikes on airbases.", table_cell)
        ],
        [
            Paragraph("<b>Anti-Armor & Bunker Defenses</b>", table_cell_bold),
            Paragraph("RPG-7, Carl Gustaf 84mm, Type 69 RPG, heavily fortified concrete bunker pillboxes.", table_cell),
            Paragraph("RPG-7, RPG-2, FPV Kamikaze Drones with shaped-charge PG-7V warheads.", table_cell),
            Paragraph("Resistance FPV drones dive directly into pillbox firing slits, neutralizing fortified positions without requiring frontal assaults.", table_cell)
        ]
    ]
    t6 = Table(artillery_data, colWidths=[130, 200, 200, 238])
    t6.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 6.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.white])
    ]))
    story.append(t6)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 7: Air Superiority vs. Asymmetric Air Denial
    # =========================================================================
    story.append(Paragraph("PILLAR 1: AERIAL WARFARE DYNAMICS", slide_subheading))
    story.append(Paragraph("Slide 7: Air Superiority vs. Asymmetric Air Denial Mesh", slide_heading))
    story.append(Spacer(1, 8))

    air_data = [
        [
            Paragraph("SAC AERIAL CAPABILITY", table_header),
            Paragraph("EAO ASYMMETRIC AIR DENIAL MESH", table_header)
        ],
        [
            Paragraph("<b>Advanced Strike Fighters:</b><br/>• Sukhoi Su-30SME (Mach 2.0, AL-31FP turbofans, ODAB-500 thermobaric bombs)<br/>• Mikoyan MiG-29B/SE (Mach 2.25, RD-33 engines, FAB-500 demolition bombs)<br/><br/><b>Light Attack & CAS Workhorses:</b><br/>• Yak-130 & K-8W (1.2–8.0 kHz compressor whine, S-8 rockets, 23mm gun pods)<br/>• Mi-35P Hind Gunships (18.5–23.0 Hz rotor slap, twin 30mm autocannon)<br/>• Y-12 Transport Bombers (High-altitude unguided barrel-bomb gravity drops)<br/><br/><b>Operational Doctrine:</b><br/>Due to ground logistical paralysis, SAC relies exclusively on 15–30 daily air sorties to terrorize civilian settlements and relieve besieged outposts.", table_cell),
            Paragraph("<b>Multi-Tiered Air Defense Assets:</b><br/>• <b>FN-6 & HN-5 MANPADS:</b> Passive infrared homing missiles brokered via UWSA; operational ceiling ~3,800m. Forces SAC jets to inaccurate high-altitude bombing.<br/>• <b>Mobile Heavy AAA:</b> Truck-mounted 14.5mm ZPU-4 and 12.7mm DShK anti-aircraft technicals providing lethal low-altitude perimeter defense.<br/>• <b>Acoustic Doppler Early Warning:</b> Parla edge acoustic sensors detecting turbofan harmonics, providing 4–8 minute shelter alert windows.<br/><br/><b>Kinetic Attrition Telemetry (2021–2026):</b><br/>Over <b>50+ confirmed SAC military airframes downed or destroyed</b> by MANPADS, anti-aircraft fire, and runway drone strikes (including FTC-2000G, K-8W, Mi-17, Mi-35P, and CH-4 UAVs).", table_cell)
        ]
    ]
    t7 = Table(air_data, colWidths=[384, 384])
    t7.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f8fafc')),
    ]))
    story.append(t7)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 8: Tactical Drone Warfare Revolution
    # =========================================================================
    story.append(Paragraph("PILLAR 1: ASYMMETRIC DRONE TELEMETRY", slide_subheading))
    story.append(Paragraph("Slide 8: The Tactical Drone Warfare Revolution", slide_heading))
    story.append(Spacer(1, 8))

    drone_data = [
        [
            Paragraph("DRONE OPERATIONAL DOMAIN", table_header),
            Paragraph("TECHNICAL SPECIFICATIONS & TACTICAL APPLICATION", table_header),
            Paragraph("BATTLEFIELD IMPACT & STRATEGIC SHIFT", table_header)
        ],
        [
            Paragraph("<b>Agricultural Hexacopter Bombers</b>", table_cell_bold),
            Paragraph("Custom heavy-lift carbon-fiber frames (e.g. modified DJI Agras platforms) carrying 2 to 6 mortar bombs (60mm/81mm) or shaped demolition blocks with 3D-printed release servos.", table_cell),
            Paragraph("Replaces conventional field artillery; provides precision vertical dive-bombing on junta ammunition depots, barracks, and communication masts.", table_cell)
        ],
        [
            Paragraph("<b>FPV Kamikaze Strike Drones</b>", table_cell_bold),
            Paragraph("First-Person-View high-speed racing drones equipped with analog 5.8 GHz video links, signal-hopping 915 MHz ELRS control, and PG-7V shaped-charge anti-tank warheads.", table_cell),
            Paragraph("Complete neutralization of SAC light armored combat vehicles (BTR-3U, EE-9 Cascavel) and surgical strikes into bunker ventilation slits.", table_cell)
        ],
        [
            Paragraph("<b>Operation 1027 Saturation Sorties</b>", table_cell_bold),
            Paragraph("Coordinated multi-drone swarm strikes deployed by the Three Brotherhood Alliance (AA, MNDAA, TNLA) exceeding 25,000 synchronized combat drops.", table_cell),
            Paragraph("Paralyzed the SAC Northeast Regional Military Command (Lashio) artillery battalions, creating safe assault lanes for infantry breakthrough.", table_cell)
        ],
        [
            Paragraph("<b>SAC Counter-Drone Response</b>", table_cell_bold),
            Paragraph("High-altitude Chinese-supplied CH-4 and Rainbow reconnaissance-strike UAVs; portable Russian/Chinese RF backpack directional jammers.", table_cell),
            Paragraph("Constrained by resistance frequency-hopping protocols, foliage camouflage, and vulnerability of SAC jammers to direct FPV kinetic strikes.", table_cell)
        ]
    ]
    t8 = Table(drone_data, colWidths=[170, 310, 288])
    t8.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 6.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.white])
    ]))
    story.append(t8)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 9: EAO-SAC Strategic Relationships (4-Tier Taxonomy)
    # =========================================================================
    story.append(Paragraph("PILLAR 3: STRATEGIC FACTIONAL ALIGNMENTS", slide_subheading))
    story.append(Paragraph("Slide 9: EAO-SAC Strategic Relationships: 4-Tier Posture Taxonomy", slide_heading))
    story.append(Spacer(1, 8))

    tax_data = [
        [
            Paragraph("TIER & POSTURE", table_header),
            Paragraph("ACTORS & ESTIMATED MANPOWER", table_header),
            Paragraph("STRATEGIC DOCTRINE & ENGAGEMENT WITH SAC", table_header)
        ],
        [
            Paragraph("<b>TIER 1</b><br/><font color='#b91c1c'><b>Total War & Active Eradication</b></font>", table_cell_bold),
            Paragraph("• Three Brotherhood Alliance (AA, TNLA, MNDAA)<br/>• K7 Revolutionary Coalition (KIA, KNU, KNDF, CNF, NUG/PDF)<br/><b>Total: >140,000 active combatants</b>", table_cell),
            Paragraph("Irreconcilable military hostility. Systematically dismantling junta Regional Military Commands (Northeast Command fallen; Western Command besieged). Demands complete abolition of military dictatorship and realization of federal democracy.", table_cell)
        ],
        [
            Paragraph("<b>TIER 2</b><br/><font color='#6b21a8'><b>Armed Neutrality & Autonomy</b></font>", table_cell_bold),
            Paragraph("• United Wa State Army (UWSA - ~30,000)<br/>• NDAA (Mong La Special Region 4 - ~4,500)<br/>• Shan State Progress Party (SSPP - ~8,000)<br/><b>Total: >42,000 active combatants</b>", table_cell),
            Paragraph("Pragmatic non-aggression with SAC ground troops while serving as the primary arms and ammunition broker for northern resistance forces. Assumed administrative control of Hopang and Panlong peacefully in 2024.", table_cell)
        ],
        [
            Paragraph("<b>TIER 3</b><br/><font color='#b45309'><b>Fractured Ceasefire Signatories</b></font>", table_cell_bold),
            Paragraph("• Restoration Council of Shan State (RCSS)<br/>• NMSP vs. NMSP-AD (Mon State)<br/>• PNLO vs. PNLA (Pa-O / Shan South)", table_cell),
            Paragraph("Severe generational and operational schisms. Frontline battalions (NMSP-AD, PNLA) broke the Nationwide Ceasefire Agreement (NCA) to launch joint combat against SAC alongside PDFs, while aging political councils retain contact with Naypyidaw.", table_cell)
        ],
        [
            Paragraph("<b>TIER 4</b><br/><font color='#334155'><b>Border Guard Forces & Proxies</b></font>", table_cell_bold),
            Paragraph("• Pa-O National Army (PNO)<br/>• Shanni Nationalities Army (SNA)<br/>• Zomi Revolutionary Army (ZRA)<br/>• Karen BGF / KNA (Saw Chit Thu)", table_cell),
            Paragraph("Local militia survival and illicit revenue preservation. PNO and SNA actively fight anti-junta resistance forces to defend regional garrison approaches. Karen BGF rebranded to KNA and declared tactical neutrality to protect border casino scam compounds.", table_cell)
        ]
    ]
    t9 = Table(tax_data, colWidths=[150, 230, 388])
    t9.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 6.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.white])
    ]))
    story.append(t9)
    story.append(PageBreak())

    # =========================================================================
    # SLIDE 10: Force Balance Outlook & Humanitarian Early-Warning Protocol
    # =========================================================================
    story.append(Paragraph("PILLAR 4: STRATEGIC OUTLOOK & EARLY-WARNING", slide_subheading))
    story.append(Paragraph("Slide 10: Strategic Force Balance & Civilian Early-Warning Advisory", slide_heading))
    story.append(Spacer(1, 8))

    s10_data = [
        [
            Paragraph("STRATEGIC DOMAIN", table_header),
            Paragraph("CURRENT TRAJECTORY (MID-TO-LATE 2026)", table_header),
            Paragraph("OPERATIONAL DIRECTIVE & RECOMMENDATIONS", table_header)
        ],
        [
            Paragraph("<b>SAC Attrition Spiral</b>", table_cell_bold),
            Paragraph("Over 40,000+ casualties, surrenders, and desertions. Enforcement of forced conscription has generated mass evasion and surrendered recruit battalions.", table_cell),
            Paragraph("SAC ground combat power is irreversibly exhausted. Anticipate accelerated garrison collapses across Ann, Sittwe, and southern Shan approaches.", table_cell)
        ],
        [
            Paragraph("<b>Logistical Collapse</b>", table_cell_bold),
            Paragraph("Loss of overland border customs and mineral basins has severed foreign currency streams. Inability to purchase foreign aviation fuel or CNC machine tooling.", table_cell),
            Paragraph("Air sortie rates will face severe degradation by late 2026 due to engine fatigue, airframe micro-cracking, and spare parts depletion.", table_cell)
        ],
        [
            Paragraph("<b>Acoustic Early Warning</b>", table_cell_bold),
            Paragraph("Parla acoustic edge sensors detect turbofan engine roar (40–120 Hz) and helicopter rotor slap (18.5–23.0 Hz) at ranges up to 15 km.", table_cell),
            Paragraph("Pre-position autonomous listening nodes around central markets, schools, and hospitals to trigger <b>4 to 8-minute siren alarms</b> before munition impact.", table_cell)
        ],
        [
            Paragraph("<b>Zero-Trace Accountability</b>", table_cell_bold),
            Paragraph("All strike dispatches, tail numbers, and munitions types are sanitized of source PII and fuzzed to 0.1° sector hashes.", table_cell),
            Paragraph("Commit verified records atomically into the offline Merkle ledger (SHA-256) to establish evidentiary archives for international war-crimes tribunals.", table_cell)
        ]
    ]
    t10 = Table(s10_data, colWidths=[150, 300, 318])
    t10.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 6.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.white])
    ]))
    story.append(t10)
    story.append(Spacer(1, 14))

    conclusion_box = [
        [
            Paragraph("<b>Concluding Operations Research Assessment:</b> The Myanmar civil war has passed the threshold of central state preservation. The future governance of Myanmar will not be dictated by Naypyidaw, but by negotiated confederated accords between ethnic revolutionary authorities and federal democratic resistance coalitions.", body_style)
        ]
    ]
    t10_box = Table(conclusion_box, colWidths=[768])
    t10_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eff6ff')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#bfdbfe')),
        ('PADDING', (0, 0), (-1, -1), 8)
    ]))
    story.append(t10_box)

    # Build the document
    doc.build(story, canvasmaker=SlideCanvas)
    
    # Also write a copy directly to root for user convenience
    import shutil
    shutil.copyfile(pdf_path, root_pdf_path)
    
    print(f"[+] Successfully compiled 10-slide executive presentation PDF to:\n    - {pdf_path}\n    - {root_pdf_path}")

if __name__ == "__main__":
    create_10_slide_report()
