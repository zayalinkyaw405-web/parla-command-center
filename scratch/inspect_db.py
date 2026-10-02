import sqlite3

conn = sqlite3.connect('Data/parla_ledger.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

for t in tables:
    tname = t[0]
    cursor.execute(f"PRAGMA table_info({tname});")
    print(f"\nSchema for {tname}:", cursor.fetchall())
    cursor.execute(f"SELECT * FROM {tname} LIMIT 3;")
    print(f"Sample data for {tname}:", cursor.fetchall())
