"""
list_tables.py
"""
import sqlite3
import os

ledger_path = "c:/Users/james/VuZiNat/iot_agent/Data/parla_ledger.db"

print(f"{'=' * 60}")
print(f"DATABASE: {ledger_path}")
print(f"File size: {os.path.getsize(ledger_path)} bytes")
print(f"{'=' * 60}")

conn = sqlite3.connect(ledger_path)
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

if not tables:
    print("\n✗ NO TABLES FOUND")
    print("The database is empty. We need to create the ledger table.")
else:
    print(f"\n📋 TABLES FOUND: {len(tables)}")
    for table in tables:
        table_name = table[0]
        print(f"\n  Table: {table_name}")
        
        # Get schema for this table
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"  Columns: {len(columns)}")
        for col in columns:
            print(f"    - {col[1]} ({col[2]})")
        
        # Count rows
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  Row count: {count}")

conn.close()
print(f"\n{'=' * 60}")
