"""
check_schema.py
Auto-detects ledger location and displays schema.
"""
import sqlite3
import os

# Auto-detect ledger location
possible_paths = [
    "../../Data/parla_ledger.db",           # From parla/domains/
    "../Data/parla_ledger.db",              # From parla/
    "Data/parla_ledger.db",                 # From project root
    "./Data/parla_ledger.db",               # From project root
    "c:/Users/james/VuZiNat/iot_agent/Data/parla_ledger.db",  # Absolute
]

ledger_path = None
for path in possible_paths:
    if os.path.exists(path):
        ledger_path = path
        break

if not ledger_path:
    print("✗ LEDGER NOT FOUND")
    print("\nSearching entire project...")
    for root, dirs, files in os.walk("c:/Users/james/VuZiNat/iot_agent"):
        if "parla_ledger.db" in files:
            ledger_path = os.path.join(root, "parla_ledger.db")
            print(f"✓ FOUND: {ledger_path}")
            break

if not ledger_path:
    print("✗ LEDGER DOES NOT EXIST YET")
    print("The ledger will be created when you first run the stress test or OSINT miner.")
    exit()

print(f"\n{'=' * 60}")
print(f"LEDGER LOCATION: {os.path.abspath(ledger_path)}")
print(f"{'=' * 60}")

conn = sqlite3.connect(ledger_path)
cursor = conn.cursor()

# Get schema
cursor.execute("PRAGMA table_info(ledger)")
columns = cursor.fetchall()

print("\n📋 LEDGER SCHEMA:")
for col in columns:
    print(f"  Column {col[0]}: {col[1]} ({col[2]})")

# Get row count
cursor.execute("SELECT COUNT(*) FROM ledger")
count = cursor.fetchone()[0]
print(f"\n📊 TOTAL BLOCKS: {count}")

# Show sample rows
print("\n📄 SAMPLE DATA (last 3 blocks):")
cursor.execute("SELECT * FROM ledger ORDER BY rowid DESC LIMIT 3")
rows = cursor.fetchall()
col_names = [desc[0] for desc in cursor.description]

for i, row in enumerate(rows, 1):
    print(f"\n  Block {i}:")
    for col_name, value in zip(col_names, row):
        # Truncate long values for readability
        val_str = str(value)
        if len(val_str) > 80:
            val_str = val_str[:77] + "..."
        print(f"    {col_name}: {val_str}")

conn.close()
print(f"\n{'=' * 60}")