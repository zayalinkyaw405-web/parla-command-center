import os
import json
import sqlite3
import glob

def analyze_all():
    print("=" * 70)
    print("      AUTHENTIC DATASET AUDIT & INVENTORY CALCULATIONS      ")
    print("=" * 70)

    # 1. SQLite Ledger Blocks & Quarantine Records
    db_path = "Data/parla_ledger.db"
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*), COUNT(DISTINCT domain) FROM ledger_blocks")
        blocks_count, domain_count = cur.fetchone()
        
        cur.execute("SELECT domain, COUNT(*) FROM ledger_blocks GROUP BY domain")
        domains_breakdown = cur.fetchall()

        cur.execute("SELECT COUNT(*) FROM quarantine_records")
        quarantine_count = cur.fetchone()[0]
        conn.close()

        print(f"\n[1. SQLITE LEDGER DATABASE - Data/parla_ledger.db]")
        print(f"  - Total Cryptographic Ledger Blocks: {blocks_count}")
        print(f"  - Total Distinct Telemetry Domains: {domain_count}")
        print(f"  - Quarantined Malicious/Spoofed Payloads: {quarantine_count}")
        print("  - Domain Breakdown:")
        for dom, cnt in domains_breakdown:
            print(f"      * {dom}: {cnt} blocks")

    # 2. Authentic JSON Intelligence Telemetry Datasets
    json_files = glob.glob("Data/*.json")
    print(f"\n[2. AUTHENTIC JSON INTELLIGENCE DATASETS - Data/*.json]")
    total_json_records = 0
    for jf in sorted(json_files):
        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    cnt = len(data)
                elif isinstance(data, dict):
                    cnt = len(data.keys())
                else:
                    cnt = 1
                total_json_records += cnt
                print(f"  - {os.path.basename(jf)}: {cnt} records ({os.path.getsize(jf)} bytes)")
        except Exception as e:
            print(f"  - {os.path.basename(jf)}: Error reading ({e})")
    print(f"  -> Total Authentic JSON Telemetry Records: {total_json_records}")

    # 3. Knowledge Base
    kb_path = "parla/core/knowledge_base.py"
    if os.path.exists(kb_path):
        kb_size = os.path.getsize(kb_path)
        with open(kb_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        print(f"\n[3. EMBEDDED OSINT KNOWLEDGE BASE - parla/core/knowledge_base.py]")
        print(f"  - Size: {kb_size} bytes ({kb_size/1024:.1f} KB)")
        print(f"  - Total Code/Data Lines: {len(lines)}")

    # 4. Biometric Embeddings & Target Portraits
    embed_path = "Data/biometric_reference_embeddings.json"
    portraits_dir = "Data/biometric_portraits"
    if os.path.exists(embed_path):
        with open(embed_path, "r", encoding="utf-8") as f:
            embeds = json.load(f)
        portrait_count = len(glob.glob("Data/raw_portraits_*.jpg"))
        print(f"\n[4. BIOMETRIC 512-D EMBEDDINGS & TARGET PORTRAITS]")
        print(f"  - Registered Target Commanders: {len(embeds)}")
        print(f"  - Authentic Target Photographs: {portrait_count}")
        for t_id, meta in embeds.items():
            dim = len(meta.get("embedding", []))
            name = meta.get("target_name") or meta.get("name")
            role = meta.get("role") or meta.get("position")
            print(f"      * [{t_id}] {name} ({role}) - {dim}-d vector")

    # 5. ML Data Mining & Unsupervised Clustering Outputs
    mine_path = "mine_outputs/mining_metrics.json"
    if os.path.exists(mine_path):
        with open(mine_path, "r", encoding="utf-8") as f:
            mine_metrics = json.load(f)
        print(f"\n[5. UNSUPERVISED ML DATA MINING & CLUSTERING - mine_outputs/]")
        print(f"  - Mining Metrics: {json.dumps(mine_metrics, indent=6)}")

    # 6. RL Feedback Learning Logs
    rl_path = "Project/rl_learning_log.md"
    if os.path.exists(rl_path):
        with open(rl_path, "r", encoding="utf-8") as f:
            rl_content = f.read()
        print(f"\n[6. REINFORCEMENT LEARNING FEEDBACK LOGS - Project/rl_learning_log.md]")
        print(f"  - Log Size: {len(rl_content)} characters")

if __name__ == "__main__":
    analyze_all()
