import streamlit as st
import sqlite3
import pandas as pd
import json
import time
import hashlib
import datetime
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Parla / Varla Dual-Mode AI Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# --- DATABASE SETUP & HELPERS ---
DB_PATH = "Data/parla_ledger.db"

def get_db_connection():
    """Returns a connection to the local SQLite database."""
    os.makedirs("Data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ledger_blocks (
            seq_id INTEGER PRIMARY KEY AUTOINCREMENT,
            block_hash TEXT NOT NULL,
            prev_hash TEXT NOT NULL,
            domain TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            nonce TEXT NOT NULL,
            payload_hash TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            signature TEXT NOT NULL,
            sync_status TEXT DEFAULT 'PENDING_FORWARD'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quarantine_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            domain TEXT NOT NULL,
            source_id TEXT,
            reason TEXT NOT NULL,
            raw_payload TEXT NOT NULL,
            quarantine_details TEXT
        )
    """)
    conn.commit()
    conn.close()

# Initialize DB on load
init_db()

def query_ledger_by_domain(domains):
    """Safely queries ledger_blocks for a list of domains."""
    try:
        conn = get_db_connection()
        placeholders = ",".join(["?"] * len(domains))
        query = f"SELECT * FROM ledger_blocks WHERE domain IN ({placeholders}) ORDER BY seq_id DESC"
        df = pd.read_sql_query(query, conn, params=domains)
        conn.close()
        return df
    except Exception as e:
        st.warning(f"Database query note: {e}")
        return pd.DataFrame()

def query_quarantine_records():
    """Safely queries quarantine_records."""
    try:
        conn = get_db_connection()
        query = "SELECT * FROM quarantine_records ORDER BY id DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

# --- HARDCODED REGION HASH DICTIONARY ---
REGION_HASH_MAP = {
    "hash_mm_ygn": "Yangon Region",
    "hash_mm_mdy": "Mandalay Region",
    "hash_mm_npt": "Naypyidaw Union Territory",
    "hash_mm_sgg": "Sagaing Region",
    "hash_mm_sha": "Shan State",
    "hash_mm_kachin": "Kachin State",
    "hash_mm_rakhine": "Rakhine State",
    "hash_mm_chin": "Chin State",
    "hash_mm_karen": "Kayin State",
    "hash_mm_tan": "Tanintharyi Region",
    "hash_mm_mgy": "Magway Region",
    "hash_mm_bago": "Bago Region",
    "hash_mm_mon": "Mon State",
    "hash_mm_kaya": "Kayah State",
    "hash_mm_ayeyar": "Ayeyarwady Region"
}

def resolve_region(region_code):
    """Maps hash/code to human readable name."""
    if not region_code:
        return "Unknown Region"
    return REGION_HASH_MAP.get(str(region_code).lower(), f"Region ({region_code})")

# --- UI TOGGLE & THEMING ---
st.markdown("<h2 style='margin-bottom:0;'>🛡️ Dual-Personality OSINT & Telemetry Dashboard</h2>", unsafe_allow_html=True)
mode = st.radio("Select Operating Mode", ["Parla", "Varla"], horizontal=True, index=0)

if mode == "Varla":
    # Dark Red-Team Neon Theme (#0d1117 background, neon green text)
    st.markdown("""
        <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
            background-color: #0d1117 !important;
            color: #00ff66 !important;
            font-family: 'Consolas', 'Courier New', monospace !important;
        }
        [data-testid="stSidebar"] {
            background-color: #161b22 !important;
            border-right: 1px solid #00ff66 !important;
        }
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, div, span, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
            color: #00ff66 !important;
            text-shadow: 0 0 3px rgba(0, 255, 102, 0.4);
        }
        input, textarea, select, div[data-baseweb="select"] {
            background-color: #161b22 !important;
            color: #ffffff !important;
            border: 1px solid #00ff66 !important;
        }
        button, .stButton > button {
            background-color: #00ff66 !important;
            color: #0d1117 !important;
            font-weight: bold !important;
            border: none !important;
            box-shadow: 0 0 10px rgba(0, 255, 102, 0.5) !important;
        }
        button:hover {
            background-color: #00cc52 !important;
            box-shadow: 0 0 15px rgba(0, 255, 102, 0.9) !important;
        }
        [data-testid="stDataFrame"], table {
            background-color: #161b22 !important;
            color: #00ff66 !important;
            border: 1px solid #00ff66 !important;
        }
        button[data-baseweb="tab"] {
            color: #8b949e !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #00ff66 !important;
            border-bottom: 2px solid #00ff66 !important;
        }
        </style>
    """, unsafe_allow_html=True)

# --- MODE 1: PARLA (DEFENSE) ---
if mode == "Parla":
    st.markdown("### 🟦 PARLA MODE: Verified OSINT & Industrial Defense Ledger")
    
    tab1, tab2, tab3 = st.tabs(["🗺️ Decrypted Risk Map", "⚠️ Industrial Alerts", "📥 Ingestion Portal"])

    # --- TAB 1: DECRYPTED RISK MAP ---
    with tab1:
        st.subheader("Decrypted Risk Map & OSINT Intelligence")
        df_osint = query_ledger_by_domain(["osint_nlp", "humanitarian", "eao_conflict_intel"])

        if df_osint.empty:
            st.info("No OSINT records found in ledger (`domain='osint_nlp'`). Use Tab 3 to ingest data.")
        else:
            parsed_records = []
            for _, row in df_osint.iterrows():
                try:
                    payload = json.loads(row["payload_json"])
                except Exception:
                    payload = {}

                region_raw = payload.get("sector") or payload.get("region_hash") or payload.get("region") or "hash_mm_npt"
                human_region = resolve_region(region_raw)
                
                parsed_records.append({
                    "Seq ID": row["seq_id"],
                    "Timestamp": row["timestamp"],
                    "Domain": row["domain"],
                    "Region Code": region_raw,
                    "Human Region": human_region,
                    "Alert / Directive": payload.get("directive") or payload.get("alert_level") or payload.get("text", "OSINT Signal"),
                    "Source ID": payload.get("source_id") or "ANON_NODE",
                    "Block Hash": row["block_hash"][:16] + "..."
                })

            df_parsed = pd.DataFrame(parsed_records)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total OSINT Events", len(df_parsed))
            with col2:
                top_region = df_parsed["Human Region"].mode()[0] if not df_parsed.empty else "N/A"
                st.metric("Highest Signal Sector", top_region)
            with col3:
                st.metric("Decryption Status", "VERIFIED (A1)")

            st.dataframe(df_parsed, use_container_width=True)

    # --- TAB 2: INDUSTRIAL ALERTS ---
    with tab2:
        st.subheader("Industrial Machine Telemetry & Anomaly Alerts")
        df_ind = query_ledger_by_domain(["industrial"])

        if df_ind.empty:
            st.info("No industrial telemetry found in ledger (`domain='industrial'`). Use Tab 3 to ingest data.")
        else:
            ind_records = []
            for _, row in df_ind.iterrows():
                try:
                    p = json.loads(row["payload_json"])
                except Exception:
                    p = {}

                temp = p.get("temperature_c", 0.0)
                vib = p.get("vibration_g", 0.0)
                is_anomaly = temp > 75.0 or vib > 0.8

                ind_records.append({
                    "Seq ID": row["seq_id"],
                    "Timestamp": row["timestamp"],
                    "Machine ID": p.get("machine_id", "TURBINE_UNKNOWN"),
                    "Contact": p.get("contact", "N/A"),
                    "Temp (°C)": temp,
                    "Vibration (g)": vib,
                    "Status": "⚠️ ANOMALY" if is_anomaly else "✅ NORMAL",
                    "Block Hash": row["block_hash"][:16] + "..."
                })

            df_ind_parsed = pd.DataFrame(ind_records)

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Total Machines Monitored", df_ind_parsed["Machine ID"].nunique())
            with c2:
                anomalies = df_ind_parsed[df_ind_parsed["Status"] == "⚠️ ANOMALY"]
                st.metric("Active Machine Anomalies", len(anomalies))
            with c3:
                max_temp = df_ind_parsed["Temp (°C)"].max() if not df_ind_parsed.empty else 0
                st.metric("Peak Temperature (°C)", f"{max_temp:.1f}")

            st.dataframe(df_ind_parsed, use_container_width=True)

    # --- TAB 3: INGESTION ---
    with tab3:
        st.subheader("Data Ingestion Forms")
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("#### 📝 Ingest OSINT Intelligence Text")
            with st.form("osint_form"):
                source_id = st.text_input("Source Identifier", value="EDGE_NODE_01")
                region_hash = st.selectbox("Region Code", list(REGION_HASH_MAP.keys()), format_func=lambda x: f"{x} ({REGION_HASH_MAP[x]})")
                directive_text = st.text_area("Intelligence Directive / Report Text", value="Unusual transponder activity detected near regional facility.")
                submitted_osint = st.form_submit_button("Submit OSINT to Ledger")

                if submitted_osint:
                    conn = get_db_connection()
                    cur = conn.cursor()
                    
                    cur.execute("SELECT block_hash FROM ledger_blocks ORDER BY seq_id DESC LIMIT 1")
                    last = cur.fetchone()
                    prev_hash = last[0] if last else "0" * 64
                    
                    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    payload = {
                        "source_id": source_id,
                        "region_hash": region_hash,
                        "sector": REGION_HASH_MAP.get(region_hash, region_hash),
                        "directive": directive_text,
                        "timestamp": ts
                    }
                    p_json = json.dumps(payload, sort_keys=True)
                    p_hash = hashlib.sha256(p_json.encode('utf-8')).hexdigest()
                    b_hash = hashlib.sha256((prev_hash + p_hash + ts).encode('utf-8')).hexdigest()
                    sig = hashlib.sha256(("parla_secret" + b_hash).encode('utf-8')).hexdigest()

                    cur.execute("""
                        INSERT INTO ledger_blocks (block_hash, prev_hash, domain, timestamp, nonce, payload_hash, payload_json, signature)
                        VALUES (?, ?, 'osint_nlp', ?, ?, ?, ?, ?)
                    """, (b_hash, prev_hash, ts, "nonce_osint", p_hash, p_json, sig))
                    conn.commit()
                    conn.close()
                    st.success("Successfully written OSINT block to ledger (`domain='osint_nlp'`)!")
                    st.rerun()

        with col_right:
            st.markdown("#### 🏭 Ingest Industrial Telemetry CSV")
            uploaded_file = st.file_uploader("Upload Industrial CSV", type=["csv"])
            
            with st.form("industrial_manual_form"):
                m_id = st.text_input("Machine ID", value="TURBINE_05")
                m_temp = st.number_input("Temperature (°C)", value=78.2, step=0.1)
                m_vib = st.number_input("Vibration (g)", value=0.85, step=0.01)
                submitted_ind = st.form_submit_button("Submit Industrial Telemetry")

                if submitted_ind:
                    conn = get_db_connection()
                    cur = conn.cursor()
                    cur.execute("SELECT block_hash FROM ledger_blocks ORDER BY seq_id DESC LIMIT 1")
                    last = cur.fetchone()
                    prev_hash = last[0] if last else "0" * 64
                    
                    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    payload = {
                        "machine_id": m_id,
                        "temperature_c": m_temp,
                        "vibration_g": m_vib,
                        "contact": "operator@facility.internal"
                    }
                    p_json = json.dumps(payload, sort_keys=True)
                    p_hash = hashlib.sha256(p_json.encode('utf-8')).hexdigest()
                    b_hash = hashlib.sha256((prev_hash + p_hash + ts).encode('utf-8')).hexdigest()
                    sig = hashlib.sha256(("parla_secret" + b_hash).encode('utf-8')).hexdigest()

                    cur.execute("""
                        INSERT INTO ledger_blocks (block_hash, prev_hash, domain, timestamp, nonce, payload_hash, payload_json, signature)
                        VALUES (?, ?, 'industrial', ?, ?, ?, ?, ?)
                    """, (b_hash, prev_hash, ts, "nonce_ind", p_hash, p_json, sig))
                    conn.commit()
                    conn.close()
                    st.success("Successfully written Industrial telemetry to ledger (`domain='industrial'`)!")
                    st.rerun()

            if uploaded_file is not None:
                try:
                    csv_df = pd.read_csv(uploaded_file)
                    st.write("Uploaded CSV Preview:", csv_df.head())
                    if st.button("Process & Ingest CSV Rows"):
                        conn = get_db_connection()
                        cur = conn.cursor()
                        count = 0
                        for _, r in csv_df.iterrows():
                            cur.execute("SELECT block_hash FROM ledger_blocks ORDER BY seq_id DESC LIMIT 1")
                            last = cur.fetchone()
                            prev_hash = last[0] if last else "0" * 64
                            ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
                            payload = r.to_dict()
                            p_json = json.dumps(payload, sort_keys=True, default=str)
                            p_hash = hashlib.sha256(p_json.encode('utf-8')).hexdigest()
                            b_hash = hashlib.sha256((prev_hash + p_hash + ts).encode('utf-8')).hexdigest()
                            sig = hashlib.sha256(("parla_secret" + b_hash).encode('utf-8')).hexdigest()

                            cur.execute("""
                                INSERT INTO ledger_blocks (block_hash, prev_hash, domain, timestamp, nonce, payload_hash, payload_json, signature)
                                VALUES (?, ?, 'industrial', ?, ?, ?, ?, ?)
                            """, (b_hash, prev_hash, ts, "nonce_csv", p_hash, p_json, sig))
                            count += 1
                        conn.commit()
                        conn.close()
                        st.success(f"Successfully ingested {count} rows from CSV into ledger!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error parsing CSV: {e}")

# --- MODE 2: VARLA (RED-TEAM) ---
else:
    st.markdown("### 🟥 VARLA MODE: Red-Team Shadow Operations & Payload Injection")

    tab1_v, tab2_v = st.tabs(["💀 Shadow Ledger", "🧪 Payload Injector"])

    # --- TAB 1: SHADOW LEDGER ---
    with tab1_v:
        st.subheader("Varla Shadow Ledger & Quarantine Log")
        df_shadow = query_ledger_by_domain(["varla_shadow", "red_team"])
        df_quarantine = query_quarantine_records()

        col1_v, col2_v = st.columns(2)
        with col1_v:
            st.metric("Shadow Exploits Logged", len(df_shadow))
        with col2_v:
            st.metric("Quarantine Intercepts", len(df_quarantine))

        st.markdown("#### 🔻 Recent Exploits & Red-Team Vectors (`domain='varla_shadow' / 'red_team'`)")
        if df_shadow.empty:
            st.info("No red-team records found in ledger (`domain='varla_shadow'` or `'red_team'`). Use Tab 2 to inject payload.")
        else:
            st.dataframe(df_shadow, use_container_width=True)

        st.markdown("#### ☣️ Fail-Closed Quarantine Audit (`table='quarantine_records'`)")
        if df_quarantine.empty:
            st.info("No quarantined attack payloads in database.")
        else:
            st.dataframe(df_quarantine, use_container_width=True)

    # --- TAB 2: PAYLOAD INJECTOR ---
    with tab2_v:
        st.subheader("Adversarial Payload Injector")
        st.markdown("Submit malformed or adversarial payloads to evaluate Parla zero-trust fail-closed mechanics.")

        with st.form("payload_injection_form"):
            target_domain = st.selectbox("Target Domain", ["varla_shadow", "red_team", "osint_nlp"])
            exploit_type = st.selectbox("Exploit Class", [
                "SQL_INJECTION_MUTATION",
                "EXIF_GEOLOCATION_SPOOF",
                "FORMAT_STRING_MALFORMED",
                "SIGNATURE_HMAC_TAMPER"
            ])
            raw_payload_text = st.text_area("Malicious / Raw Payload Content", value="{'vector': 'EXIF_SPOOF', 'lat': 99.99, 'lng': 99.99, 'attack': \"' OR 1=1 --\"}")
            simulate_quarantine = st.checkbox("Simulate Fail-Closed Quarantine Trigger", value=True)
            
            submitted_payload = st.form_submit_button("🚀 Inject Adversarial Payload")

            if submitted_payload:
                conn = get_db_connection()
                cur = conn.cursor()
                ts = datetime.datetime.now(datetime.timezone.utc).isoformat()

                if simulate_quarantine:
                    # Write to quarantine_records
                    cur.execute("""
                        INSERT INTO quarantine_records (timestamp, domain, source_id, reason, raw_payload, quarantine_details)
                        VALUES (?, ?, 'VARLA_RED_TEAM', ?, ?, ?)
                    """, (ts, target_domain, f"FAIL_CLOSED_{exploit_type}", raw_payload_text, f"Intercepted by VoidNode bridge at {ts}"))
                    conn.commit()
                    conn.close()
                    st.warning(f"Payload intercept confirmed! Quarantined under reason: FAIL_CLOSED_{exploit_type}")
                else:
                    # Write to ledger_blocks under varla_shadow / red_team
                    cur.execute("SELECT block_hash FROM ledger_blocks ORDER BY seq_id DESC LIMIT 1")
                    last = cur.fetchone()
                    prev_hash = last[0] if last else "0" * 64
                    
                    p_json = json.dumps({"exploit_type": exploit_type, "raw_payload": raw_payload_text})
                    p_hash = hashlib.sha256(p_json.encode('utf-8')).hexdigest()
                    b_hash = hashlib.sha256((prev_hash + p_hash + ts).encode('utf-8')).hexdigest()
                    sig = hashlib.sha256(("varla_secret" + b_hash).encode('utf-8')).hexdigest()

                    cur.execute("""
                        INSERT INTO ledger_blocks (block_hash, prev_hash, domain, timestamp, nonce, payload_hash, payload_json, signature)
                        VALUES (?, ?, ?, ?, 'nonce_varla', ?, ?, ?)
                    """, (b_hash, prev_hash, target_domain, ts, p_hash, p_json, sig))
                    conn.commit()
                    conn.close()
                    st.success(f"Adversarial payload committed to shadow ledger under domain='{target_domain}'!")
                
                st.rerun()