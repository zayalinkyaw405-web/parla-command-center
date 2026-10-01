"""
app.py
Parla Unified Command Center (Production Edition)
Combines: Real-World Ingestion, Decoder Ring, Feedback Loop, and Ledger Audit.
"""

import streamlit as st
import sqlite3
import json
import hashlib
import hmac
import pandas as pd
import numpy as np
import time
from pathlib import Path
import sys
import io

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from parla.domains.osint_nlp import OSINTEventExtractor, generate_osint_signature, DEFAULT_OSINT_SECRET
from parla.domains.industrial import IndustrialProcessor
from parla.domains.risk_mapper import RegionalRiskMapper
from parla.core.feedback_loop import FeedbackLoop

# --- CONFIGURATION ---
DB_PATH = PROJECT_ROOT / "Data" / "parla_ledger.db"
INDUSTRIAL_SECRET = b"parla_industrial_offline_key_2026"

st.set_page_config(page_title="Parla Command Center", page_icon="🛡️", layout="wide")

# --- THE AUTHORIZED DECODER RING (Embedded for UI) ---
AUTHORIZED_MAP = {
    "MYANMAR_REGION_SAGAING": "Sagaing (Central Dry Zone)",
    "MYANMAR_REGION_RAKHINE": "Rakhine (Western Coast)",
    "MYANMAR_REGION_SHAN_NORTH": "Northern Shan State",
    "MYANMAR_REGION_KACHIN": "Kachin State (North)",
    "MYANMAR_REGION_CHIN": "Chin State (West)",
    "MYANMAR_REGION_KAYAH": "Kayah State (East)",
    "MYANMAR_REGION_KAYIN": "Kayin State (South-East)",
    "MYANMAR_REGION_MAGWAY": "Magway (Central)",
    "MYANMAR_REGION_MANDALAY": "Mandalay (Central)",
    "MYANMAR_REGION_YANGON": "Yangon (South)",
    "MYANMAR_REGION_UNSPECIFIED": "Unspecified / Coords Redacted"
}

def get_human_name(region_hash: str) -> str:
    """Translates a Zero-Trust hash back to a human-readable name."""
    for internal_name, human_name in AUTHORIZED_MAP.items():
        if hashlib.sha256(internal_name.encode('utf-8')).hexdigest() == region_hash:
            return human_name
    return f"Unknown Zone ({region_hash[:8]}...)"

# --- HELPER FUNCTIONS ---
def get_db_connection():
    if not DB_PATH.exists(): return None
    return sqlite3.connect(str(DB_PATH))

def verify_chain_integrity(limit=50):
    conn = get_db_connection()
    if not conn: return False
    cursor = conn.cursor()
    cursor.execute("SELECT seq_id, block_hash, prev_hash FROM ledger_blocks ORDER BY seq_id DESC LIMIT ?", (limit,))
    blocks = cursor.fetchall()
    conn.close()
    if len(blocks) < 2: return True
    for i in range(len(blocks) - 1):
        if blocks[i][2] != blocks[i+1][1]: return False
    return True

# --- INITIALIZATION ---
@st.cache_resource
def load_processors():
    return OSINTEventExtractor(), IndustrialProcessor(), FeedbackLoop(), RegionalRiskMapper()

osint_proc, ind_proc, feedback_loop, risk_mapper = load_processors()

# --- MAIN UI ---
st.title("🛡️ Parla Autonomous Command Center")
st.caption("Zero-Trust | Offline-First | Real-World Ingestion | Adaptive Intelligence")

if not DB_PATH.exists():
    st.error("❌ Ledger database not found. Please run the stress test first to initialize the DB.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs([
    "🌍 Live Humanitarian Ingest", 
    "🏭 Live Industrial Ingest", 
    "🗺️ Decrypted Risk Map", 
    "🔗 Ledger & Feedback"
])

# ==========================================
# TAB 1: LIVE HUMANITARIAN INGEST (Real OSINT)
# ==========================================
with tab1:
    st.header("📥 Real-World OSINT Field Report Ingestion")
    st.info("Paste authentic, unredacted field reports below. Parla will instantly strip PII, hash locations, classify the threat, and seal it to the Zero-Trust ledger.")
    
    with st.form("osint_ingest_form"):
        raw_text = st.text_area("Paste Raw Field Report:", height=150, placeholder="e.g., Heavy artillery shelling reported in Tabayin, Sagaing today. Ko Aung (+95-9-1234567) says 3 families fled...")
        source_id = st.text_input("Source ID (Optional):", value="FIELD_OP_01")
        submitted = st.form_submit_button("🛡️ Process, Redact & Seal to Ledger")
        
        if submitted and raw_text:
            with st.spinner("Applying Zero-Trust PII Redaction & Cryptographic Sealing..."):
                # Sign the payload
                sig = generate_osint_signature(raw_text, secret_key=DEFAULT_OSINT_SECRET)
                
                # Process
                result = osint_proc.process_osint_payload(
                    raw_text=raw_text, 
                    signature=sig, 
                    source_id=source_id
                )
                
                if result['status'] == 'SEALED':
                    st.success("✅ SUCCESS: Report sealed to ledger.")
                    evt = result['event']
                    human_loc = get_human_name(evt['region_hash'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Event Classified", evt['event_type'])
                        st.metric("Confidence", f"{evt['confidence']:.2f}")
                    with col2:
                        st.metric("Decrypted Location", human_loc)
                        st.metric("Action Required", evt.get('action', 'MONITOR'))
                        
                    with st.expander("🔍 View PII Redaction Proof"):
                        st.text(result['event'].get('redacted_text_snippet', 'N/A'))
                else:
                    st.error(f"❌ FAILED: {result.get('reason', 'Unknown error')}")

# ==========================================
# TAB 2: LIVE INDUSTRIAL INGEST (Real CSV)
# ==========================================
with tab2:
    st.header("📊 Real-World Industrial Sensor Telemetry")
    st.info("Upload a CSV file containing real machine sensor data. Expected columns: `machine_id`, `vibration_rms`, `temperature`.")
    
    # Provide a sample CSV for testing
    sample_csv = "machine_id,vibration_rms,temperature\nPUMP-001,0.45,42.1\nPUMP-002,2.80,68.5\nPUMP-001,0.50,43.0\n"
    st.download_button("⬇️ Download Sample CSV Template", sample_csv, "sample_telemetry.csv", "text/csv")
    
    uploaded_file = st.file_uploader("Upload Real Sensor CSV", type=["csv"])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("### Preview of Uploaded Data")
        st.dataframe(df, width="stretch")
        
        if st.button("🏭 Process & Seal Telemetry to Ledger"):
            progress_bar = st.progress(0)
            success_count = 0
            
            for index, row in df.iterrows():
                machine_id = str(row.get('machine_id', 'UNKNOWN'))
                vib_rms = float(row.get('vibration_rms', 0.0))
                temp = float(row.get('temperature', 25.0))
                
                # Convert RMS to a realistic 1000-point waveform for the EMD processor
                t = np.linspace(0, 1, 1000)
                vibration_data = vib_rms * np.sin(2 * np.pi * 50 * t) + np.random.normal(0, vib_rms * 0.1, 1000)
                
                # Sign payload
                payload = {"machine_id": machine_id, "vibration_data": vibration_data.tolist(), "temperature": temp}
                payload_json = json.dumps(payload, sort_keys=True)
                signature = hmac.new(INDUSTRIAL_SECRET, payload_json.encode(), hashlib.sha256).hexdigest()
                
                # Process
                result = ind_proc.process_telemetry(machine_id, vibration_data, temp, signature)
                if result['status'] == 'PROCESSED':
                    success_count += 1
                    
                progress_bar.progress((index + 1) / len(df))
                
            st.success(f"✅ SUCCESS: {success_count}/{len(df)} telemetry records sealed to ledger.")

# ==========================================
# TAB 3: DECRYPTED RISK MAP
# ==========================================
with tab3:
    st.header("🗺️ Decrypted Humanitarian Risk Intelligence")
    
    report = risk_mapper.calculate_regional_risk(days=90)
    
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Regions Monitored", report['total_regions_monitored'])
    with col2: st.metric("Analysis Window", f"{report['analysis_window_days']} Days")
    with col3: 
        top_risk = report['regions'][0]['risk_score'] if report['regions'] else 0
        st.metric("Highest Risk Score", f"{top_risk:.1f}")

    st.divider()
    
    if report['regions']:
        df_risk = pd.DataFrame(report['regions'])
        
        # DECODER RING INTEGRATION: Translate hashes to real names for the chart
        df_risk['Human_Name'] = df_risk['region_hash'].apply(get_human_name)
        df_risk = df_risk.sort_values(by='risk_score', ascending=True)
        
        st.subheader("Real-World Regional Risk Heatmap")
        st.bar_chart(df_risk.set_index('Human_Name')['risk_score'])
        
        st.subheader("Threat Breakdown by Decrypted Region")
        for region in report['regions']:
            human_name = get_human_name(region['region_hash'])
            with st.expander(f"📍 {human_name} (Risk Score: {region['risk_score']})"):
                st.write(f"**Total Events:** {region['total_events']}")
                st.write(f"**Latest Activity:** {region['latest_activity']}")
                for evt, count in region['event_breakdown'].items():
                    st.write(f"- **{evt}:** {count} incidents")
    else:
        st.info("No OSINT events recorded yet. Use Tab 1 to ingest real reports.")

# ==========================================
# TAB 4: LEDGER & FEEDBACK
# ==========================================
with tab4:
    st.header("🔗 Zero-Trust Ledger & Adaptive Feedback")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ledger_blocks")
    total_blocks = cursor.fetchone()[0]
    cursor.execute("SELECT domain, COUNT(*) FROM ledger_blocks GROUP BY domain")
    df_domains = pd.DataFrame(cursor.fetchall(), columns=['Domain', 'Count'])
    conn.close()
    
    col1, col2 = st.columns(2)
    with col1: st.metric("Total Sealed Blocks", total_blocks)
    with col2:
        if verify_chain_integrity(): st.success("✅ Cryptographic Chain: VALID")
        else: st.error("❌ Cryptographic Chain: BROKEN")
        
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Domain Distribution")
        st.bar_chart(df_domains.set_index('Domain')['Count'])
        
    with col2:
        st.subheader("🧠 Adaptive Thresholds (Live)")
        thresholds = feedback_loop.get_current_thresholds()
        if thresholds:
            for evt, thresh in thresholds.items():
                st.metric(evt, f">= {thresh}")
        else:
            st.info("No feedback yet. Default: 0.70")

    st.divider()
    st.subheader("📥 Recent Alert Queue (Human-in-the-Loop)")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT seq_id, payload_json FROM ledger_blocks WHERE domain = 'osint_nlp' ORDER BY seq_id DESC LIMIT 5")
    recent_blocks = cursor.fetchall()
    conn.close()
    
    for seq_id, payload_json in recent_blocks:
        payload = json.loads(payload_json)
        event = payload.get('structured_event', payload.get('event', {}))
        evt_type = event.get('event_type', 'UNKNOWN')
        confidence = event.get('confidence', 0.0)
        human_loc = get_human_name(event.get('region_hash', ''))
        
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([2, 2, 3, 1, 1])
            with c1: st.markdown(f"**{evt_type}**")
            with c2: st.markdown(f"Conf: **{confidence:.2f}**")
            with c3: st.markdown(f"📍 {human_loc}")
            with c4:
                if st.button("✅ Confirm", key=f"c_{seq_id}"):
                    feedback_loop.record_feedback(f"OSINT-{seq_id}", evt_type, confidence, "CONFIRM", "Dashboard")
                    st.rerun()
            with c5:
                if st.button("❌ Reject", key=f"r_{seq_id}"):
                    feedback_loop.record_feedback(f"OSINT-{seq_id}", evt_type, confidence, "REJECT", "Dashboard")
                    st.rerun()
            st.divider()