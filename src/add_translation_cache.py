
import sqlite3
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_FILE = PROJECT_DIR / "data" / "jobs.db"

with sqlite3.connect(DB_FILE) as conn:
    columns = [
        row[1]
        for row in conn.execute("PRAGMA table_info(jobs)")
    ]

    if "english_description" not in columns:
        conn.execute("""
            ALTER TABLE jobs
            ADD COLUMN english_description TEXT
        """)
        print("English description column added!")
    else:
        print("English description column already exists!")

print("Database is ready for translation caching.")
