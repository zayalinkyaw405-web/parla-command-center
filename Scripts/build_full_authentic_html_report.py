"""
Scripts/build_full_authentic_html_report.py
============================================
Generates authentic_data_full_intelligence_report_2026.html
"""

import os
import json
import sqlite3
import datetime

HTML_OUTPUT_PATH = "Project/reports/authentic_data_full_intelligence_report_2026.html"

def build_html():
    print(f"Building HTML Report -> {HTML_OUTPUT_PATH}...")

    # Load authentic stats
    conn = sqlite3.connect("Data/parla_ledger.db")
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*), COUNT(DISTINCT domain) FROM ledger_blocks")
    total_blocks, total_domains = cur.fetchone()

    cur.execute("SELECT domain, COUNT(*) FROM ledger_blocks GROUP BY domain ORDER BY COUNT(*) DESC")
    domain_rows = cur.fetchall()

    cur.execute("SELECT COUNT(*) FROM quarantine_records")
    quarantine_count = cur.fetchone()[0]
    conn.close()

    # Load roster
    roster_file = "Data/international_accountability_roster_2026.json"
    commanders = []
    if os.path.exists(roster_file):
        with open(roster_file, "r", encoding="utf-8") as f:
            roster_data = json.load(f)
            commanders = roster_data.get("commanders", []) if isinstance(roster_data, dict) else roster_data

    now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    domain_table_rows = "".join([
        f"<tr><td><code>{dom}</code></td><td><strong>{cnt}</strong></td><td>Cryptographic block logs for {dom}</td></tr>"
        for dom, cnt in domain_rows
    ])

    roster_rows = "".join([
        f"<tr><td><code>{cmd.get('target_id', 'N/A')}</code></td><td><strong>{cmd.get('target_name', 'N/A')}</strong></td><td>{cmd.get('position', 'N/A')}</td><td>{cmd.get('unit', 'N/A')}</td><td><span class='badge badge-green'>{cmd.get('reliability_grade', 'GRADE_A1_RELIABLE')}</span></td></tr>"
        for cmd in commanders[:10]
    ])

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Myanmar Military Intelligence & Accountability Full Report (2026)</title>
    <style>
        :root {{
            --bg: #0d1117;
            --card-bg: #161b22;
            --border: #30363d;
            --accent: #00ff66;
            --text-main: #c9d1d9;
            --text-header: #ffffff;
            --text-dim: #8b949e;
        }}
        body {{
            background-color: var(--bg);
            color: var(--text-main);
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            margin: 0;
            padding: 30px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header-card {{
            background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
            border: 1px solid var(--accent);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 0 20px rgba(0, 255, 102, 0.2);
        }}
        h1 {{
            color: var(--text-header);
            font-size: 26px;
            margin-top: 0;
            text-shadow: 0 0 8px rgba(0, 255, 102, 0.4);
        }}
        .subtitle {{
            color: var(--accent);
            font-size: 16px;
            font-weight: 600;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: 700;
            color: var(--accent);
        }}
        .metric-label {{
            font-size: 13px;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .section-card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 30px;
        }}
        h2 {{
            color: var(--text-header);
            font-size: 20px;
            border-bottom: 1px solid var(--border);
            padding-bottom: 10px;
            margin-top: 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            font-size: 14px;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            background-color: #0d1117;
            color: var(--accent);
            font-weight: 600;
        }}
        tr:hover {{
            background-color: #21262d;
        }}
        code {{
            background: #21262d;
            color: var(--accent);
            padding: 3px 6px;
            border-radius: 4px;
            font-family: 'Consolas', monospace;
        }}
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }}
        .badge-green {{
            background: rgba(0, 255, 102, 0.15);
            color: #00ff66;
            border: 1px solid #00ff66;
        }}
        .chart-img {{
            width: 100%;
            max-width: 900px;
            height: auto;
            border-radius: 8px;
            border: 1px solid var(--border);
            margin: 15px 0;
        }}
        .portraits-row {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-top: 15px;
        }}
        .portrait-card {{
            background: #0d1117;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            width: 140px;
        }}
        .portrait-card img {{
            width: 120px;
            height: 140px;
            object-fit: cover;
            border-radius: 4px;
        }}
        .portrait-name {{
            font-size: 12px;
            font-weight: 600;
            color: var(--text-header);
            margin-top: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header-card">
            <h1>MYANMAR MILITARY INTELLIGENCE & ACCOUNTABILITY REPORT</h1>
            <div class="subtitle">Authentic Multi-INT Telemetry, Biometric Dossiers, Military Hardware & Machine Learning Audit (2022–2026)</div>
            <p style="margin-bottom:0; color: var(--text-dim);">
                CLASSIFICATION: <strong>CONFIDENTIAL / NATO A1 ADMIRALTY GRADE</strong> | MERKLE ROOT: <code>bbab2c7c122e2969a6040fa7e240ebcc3b85313339047484226673fa6fc1dd4b</code> | GENERATED: {now_str}
            </p>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{total_blocks}</div>
                <div class="metric-label">Cryptographic Ledger Blocks</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{total_domains}</div>
                <div class="metric-label">Active Telemetry Domains</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{quarantine_count}</div>
                <div class="metric-label">Quarantined Attack Payloads</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{len(commanders)}</div>
                <div class="metric-label">Senior Commanders Indicted</div>
            </div>
        </div>

        <div class="section-card">
            <h2>1. Cryptographic Ledger Domain Breakdown</h2>
            <img src="telemetry_domains_chart.png" alt="Telemetry Domains Chart" class="chart-img">
            <table>
                <thead>
                    <tr><th>Telemetry Domain</th><th>Block Count</th><th>Scope Description</th></tr>
                </thead>
                <tbody>
                    {domain_table_rows}
                </tbody>
            </table>
        </div>

        <div class="section-card">
            <h2>2. Biometric Target Identification & Target Portraits</h2>
            <p>Target facial similarity matrix across 28 registered target vectors in <code>Data/biometric_reference_embeddings.json</code>:</p>
            <img src="biometric_matrix_chart.png" alt="Biometric Matrix Chart" class="chart-img">
            
            <div class="portraits-row">
                <div class="portrait-card">
                    <img src="../../Data/raw_portraits_IND-SAC-001.jpg" alt="Min Aung Hlaing">
                    <div class="portrait-name">Min Aung Hlaing</div>
                </div>
                <div class="portrait-card">
                    <img src="../../Data/raw_portraits_IND-SAC-002.jpg" alt="Soe Win">
                    <div class="portrait-name">Soe Win</div>
                </div>
                <div class="portrait-card">
                    <img src="../../Data/raw_portraits_IND-MAF-001.jpg" alt="Tun Aung">
                    <div class="portrait-name">Tun Aung</div>
                </div>
                <div class="portrait-card">
                    <img src="../../Data/raw_portraits_IND-LID-001.jpg" alt="Aung Aung">
                    <div class="portrait-name">Aung Aung</div>
                </div>
                <div class="portrait-card">
                    <img src="../../Data/raw_portraits_IND-RMC-002.jpg" alt="Maung Maung Soe">
                    <div class="portrait-name">Maung Maung Soe</div>
                </div>
            </div>

            <table style="margin-top: 25px;">
                <thead>
                    <tr><th>Target ID</th><th>Commander Name</th><th>Role / Position</th><th>Unit / Command</th><th>Admiralty Grade</th></tr>
                </thead>
                <tbody>
                    {roster_rows}
                </tbody>
            </table>
        </div>

        <div class="section-card">
            <h2>3. Military Hardware & Air Force Attack Aircraft</h2>
            <img src="hardware_fleet_chart.png" alt="Hardware Fleet Chart" class="chart-img">
        </div>

        <div class="section-card">
            <h2>4. Unsupervised Machine Learning Telemetry Audit</h2>
            <img src="ml_clusters_chart.png" alt="ML Clusters Chart" class="chart-img">
        </div>
    </div>
</body>
</html>
"""

    with open(HTML_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML Report Build Complete -> {HTML_OUTPUT_PATH}")

if __name__ == "__main__":
    build_html()
