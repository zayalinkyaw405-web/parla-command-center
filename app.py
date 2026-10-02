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
import spacy
from parla.domains.osint_nlp import OSINTEventExtractor, generate_osint_signature, DEFAULT_OSINT_SECRET
from parla.domains.industrial import IndustrialProcessor
from parla.domains.risk_mapper import RegionalRiskMapper
from parla.core.feedback_loop import FeedbackLoop
from parla.domains.osint_ingestor import OSINTIngestor, IngestedEvent
from parla.domains.real_data_gateway import RealDataGateway, NormalizedTelemetry
from parla.domains.feedback_loop import FeedbackLoop as RLFeedbackLoop, FeedbackSignal
from PIL import Image
from parla.domains.facial_recognition_engine import (
    FacialRecognitionEngine,
    WatchlistGallery,
    WatchlistTarget,
    MatchClassification
)
from parla.core.ledger import OfflineLedger
from Scripts.analyze_visual_media import VisualMediaAnalyzer

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

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🌍 Live Humanitarian Ingest", 
    "🏭 Live Industrial Ingest", 
    "🗺️ Decrypted Risk Map", 
    "🔗 Ledger & Feedback",
    "⚡ Pipeline Gateway",
    "👁️ Optical & Biometric Intelligence"
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

# ==========================================
# TAB 5: PIPELINE GATEWAY (E2E Verification)
# ==========================================
with tab5:
    st.header("⚡ Real-World Ingestion Gateway & End-to-End Pipeline")
    st.info("Execute end-to-end multi-track telemetry pipelines: signed IoT edge streams with RL parameter tuning (Track A) and REST API OSINT conflict feeds with PII scrubbing (Track B).")

    gateway = RealDataGateway()
    osint_ingest = OSINTIngestor(kb_dir=str(PROJECT_ROOT / "Project"))
    rl_feedback = RLFeedbackLoop(kb_dir=str(PROJECT_ROOT / "Project"))

    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.subheader("🏭 Track A: Edge Telemetry & RL Tuning")
        st.caption("Injects HMAC-signed vibration telemetry and executes operator RL parameter adaptation.")
        
        mach_id = st.text_input("Target Machine ID:", value="PUMP-ALPHA-01", key="t5_mach")
        vib_level = st.slider("Simulated Vibration Amplitude (g):", min_value=0.2, max_value=3.5, value=2.5, step=0.1, key="t5_vib")
        
        if st.button("🚀 Run Track A Pipeline", key="run_track_a"):
            with st.spinner("Processing through Industrial Processor & Ledger..."):
                t = np.linspace(0, 1, 1000)
                vibration_data = np.random.normal(0, 0.4, 1000) + vib_level * np.sin(2 * np.pi * 50 * t)
                temp = 72.0
                
                payload = {"machine_id": mach_id, "vibration_data": vibration_data.tolist(), "temperature": temp}
                payload_json = json.dumps(payload, sort_keys=True)
                signature = hmac.new(INDUSTRIAL_SECRET, payload_json.encode(), hashlib.sha256).hexdigest()
                
                result = ind_proc.process_telemetry(mach_id, vibration_data, temp, signature)
                
                if result['status'] == 'PROCESSED':
                    st.success(f"✅ Telemetry Sealed to Ledger! Hash: `{result['ledger_hash'][:24]}...`")
                    st.metric("Urgency", result['directive']['urgency'])
                    st.metric("Failure Mode", result['directive']['failure_mode'])
                    st.write(f"**Explanation:** {result['directive']['explanation']}")
                    
                    # RL Feedback adjustment
                    fb_sig = FeedbackSignal(
                        event_id=result['ledger_hash'][:16],
                        original_prediction=result['directive']['failure_mode'],
                        true_label="VERIFIED_ROTARY_DEFECT" if vib_level > 1.5 else "NOMINAL_LOAD",
                        reward=1.0 if vib_level > 1.5 else -1.0,
                        confidence=result['directive']['confidence']
                    )
                    rl_res = rl_feedback.process_feedback(fb_sig)
                    st.info(f"🧠 RL Adaptation: {rl_res['adjustment_made']} (New DBSCAN eps: {rl_res['new_dbscan_eps']})")
                else:
                    st.error(f"❌ Processing Rejected: {result.get('reason')}")

    with col_t2:
        st.subheader("📰 Track B: REST Conflict Ingest & Scrub")
        st.caption("Simulates external REST API conflict telemetry, normalizes schema, scrubs PII, and appends to KB.")
        
        sample_report = st.text_area(
            "REST API Telemetry Feed:",
            value="At 08:00, artillery shelling was reported near Hpakant. Reporter Aung Ko (aung.ko@news.mm, +95 9 123 456 789) reported civilian displacement near 25.4567, 96.1234. Aid blocked.",
            height=120,
            key="t5_report"
        )
        
        if st.button("🛡️ Run Track B Pipeline", key="run_track_b"):
            with st.spinner("Normalizing & Scrubbing PII..."):
                norm_evt = NormalizedTelemetry(
                    source_type="REST_API",
                    event_id=f"rest_{int(time.time())}_ui",
                    timestamp=time.time(),
                    raw_payload={"source": "Myanmar Peace Monitor", "urls": ["https://example.com/live-report"]},
                    normalized_data={"text": sample_report, "location": "Hpakant", "timestamp_raw": "08:00"}
                )
                
                scrubbed = osint_ingest._redact_pii(norm_evt.normalized_data["text"])
                category = osint_ingest._classify_event(scrubbed, norm_evt.raw_payload)
                
                final_evt = IngestedEvent(
                    timestamp=datetime.now().strftime("%Y-%m-%d"),
                    source="Myanmar Peace Monitor",
                    category=category,
                    summary=scrubbed,
                    original_hash=hashlib.sha256(sample_report.encode()).hexdigest()[:16],
                    source_links=["https://example.com/live-report"]
                )
                osint_ingest._append_to_kb(final_evt)
                
                st.success("✅ REST Feed Ingested & PII Scrubbed!")
                st.metric("Event Classification", category)
                st.text_area("PII Redacted Text:", value=scrubbed, height=80, disabled=True)
                st.info("Appended to Knowledge Base: `Project/news-and-market-trends.md`")

# ==========================================
# TAB 6: OPTICAL & BIOMETRIC INTELLIGENCE
# ==========================================
with tab6:
    st.header("👁️ Optical & Biometric Intelligence Studio")
    st.caption("Visual Media Forensics | High-Dimensional ArcFace Embeddings | VOID Zero-Trace Bystander Anonymization | Merkle Ledger Sealing")

    col_upload, col_settings = st.columns([2, 1])

    with col_settings:
        st.subheader("⚙️ Watchlist & Privacy Controls")
        anonymize_check = st.checkbox("🛡️ VOID Zero-Trace Anonymization", value=True, help="Automatically blur non-target bystander faces in output display.")
        enroll_accountability = st.checkbox(
            "⚖️ Load International Accountability Watchlist (UN FFM / ICC / IIMM)",
            value=True,
            help="Enrolls documented senior military commanders from UN A/HRC/39/64, ICC, and IIMM warrants into facial recognition watchlist."
        )
        enroll_default_target = st.checkbox("🎯 Enroll High-Value Target Watchlist", value=True, help="Enrolls sample tactical Watchlist targets (e.g. TGT-SAC-001).")
        sim_threshold = st.slider("Cosine Match Threshold (Definitive)", min_value=0.50, max_value=0.90, value=0.72, step=0.01)

    with col_upload:
        uploaded_file = st.file_uploader(
            "Upload Image for Multi-Vector Optical & Biometric Ingestion:",
            type=["jpg", "jpeg", "png", "webp"],
            key="tab6_uploader"
        )

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        
        # Initialize analyzer and watchlist
        gallery = WatchlistGallery()
        if enroll_accountability and hasattr(gallery, "load_from_accountability_roster"):
            gallery.load_from_accountability_roster()
        if enroll_default_target:
            tgt = WatchlistTarget(
                target_id="TGT-SAC-001",
                name="SAC Senior Command Target",
                category="ADVERSARY",
                threat_level="EXTREME"
            )
            gallery.enroll(tgt)
        
        ledger_inst = OfflineLedger(db_path=str(DB_PATH)) if DB_PATH.exists() else None
        analyzer = VisualMediaAnalyzer(gallery=gallery, ledger=ledger_inst)
        if analyzer.engine:
            analyzer.engine.definitive_threshold = sim_threshold
        
        # Analyze in-memory
        optical = analyzer.extract_optical_properties(image)
        palette = analyzer.extract_dominant_colors(image)
        exif = analyzer.extract_exif_metadata(image)
        biometrics = analyzer.inspect_biometrics(image, source_id=uploaded_file.name, anonymize=anonymize_check)
        
        st.divider()
        
        # Visual display
        vcol1, vcol2 = st.columns(2)
        with vcol1:
            st.subheader("📸 Ingested Optical Frame")
            st.image(image, use_container_width=True, caption=f"Original: {uploaded_file.name}")
        with vcol2:
            st.subheader("🛡️ Zero-Trace Output Frame")
            if anonymize_check and biometrics.get("redacted_image"):
                st.image(biometrics["redacted_image"], use_container_width=True, caption="Anonymized (Bystanders Redacted via VOID Pillar)")
            else:
                st.image(image, use_container_width=True, caption="Unmodified Display")
                
        # Metrics row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Resolution", optical["resolution"])
        m2.metric("Aspect Ratio", optical["aspect_ratio"].split()[0])
        m3.metric("Luminance", f"{optical['mean_luminance']}/255")
        m4.metric("Faces Detected", biometrics.get("total_faces_detected", 0))
        
        # Tabs for details
        dtab1, dtab2, dtab3 = st.tabs(["🎨 Color Palette & Optics", "🔍 Forensic EXIF & Geolocation", "👤 Biometric Watchlist & Ledger"])
        
        with dtab1:
            st.write(f"**Lighting Assessment:** `{optical['lighting_assessment']}` | **Sharpness Variance (Laplacian):** `{optical['sharpness_variance']}`")
            st.write("#### Dominant Colors (K-Means)")
            pcols = st.columns(len(palette))
            for i, c in enumerate(palette):
                with pcols[i]:
                    st.markdown(f"<div style='background-color:{c['hex']};height:40px;border-radius:6px;border:1px solid #555;'></div>", unsafe_allow_html=True)
                    st.caption(f"**{c['hex']}**\n{c['percentage']}%")
                    
        with dtab2:
            st.write(f"**EXIF Header Detected:** `{exif.get('exif_present')}`")
            st.write(f"**Hardware:** `{exif.get('device_make', 'N/A')} {exif.get('device_model', 'N/A')}`")
            st.write(f"**Software / Pipeline:** `{exif.get('software', 'N/A')}`")
            st.write(f"**Capture Timestamp:** `{exif.get('date_time', 'N/A')}`")
            if exif.get('gps_info'):
                st.warning("⚠️ GPS Micro-coordinates detected in file metadata!")
                st.json(exif['gps_info'])
            else:
                st.success("✅ Clean: Zero GPS micro-coordinates or location tracking leaked in EXIF.")
                
        with dtab3:
            st.write(f"**Targets Matched:** `{biometrics.get('targets_matched', 0)}` | **Bystanders Anonymized:** `{biometrics.get('bystanders_anonymized', 0)}`")
            if biometrics.get("detections"):
                st.dataframe(pd.DataFrame(biometrics["detections"]))
            if biometrics.get("ledger_events"):
                st.success("🔒 Biometric Match Event Committed to Merkle Ledger!")
                for evt in biometrics["ledger_events"]:
                    if evt.get("target_category") == "WAR_CRIMES_ACCOUNTABILITY":
                        st.error(f"🚨 **WAR CRIMES ACCOUNTABILITY HIT:** {evt.get('target_name')} (`{evt.get('target_id')}`)")
                        st.markdown(f"**Admiralty Grade:** `{evt.get('admiralty_grade')}` | **Similarity:** `{evt.get('similarity_score')}`")
                        with st.expander("⚖️ International Legal Evidence Dossier & UN/ICC Citations"):
                            meta = evt.get("metadata", {})
                            st.write(f"**Command Echelon:** {meta.get('command_echelon', 'N/A')}")
                            st.write(f"**Role:** {meta.get('role', 'N/A')}")
                            st.write(f"**Alleged Offenses:** {', '.join(meta.get('alleged_offenses', []))}")
                            st.write(f"**UN FFM Mandate:** {meta.get('un_ffm_mandate', 'N/A')}")
                            st.write(f"**ICC Status:** {meta.get('icc_status', 'N/A')}")
                            st.write(f"**IIMM Case File:** `{meta.get('iimm_case_file', 'N/A')}`")
                            st.write("**Documented Evidence / Incidents:**")
                            for inc in meta.get("documented_incidents", []):
                                st.markdown(f"- {inc}")
                    st.json(evt)
            else:
                st.info("No watchlist target matched above threshold. Zero persistent biometric events created (Zero-Trace).")