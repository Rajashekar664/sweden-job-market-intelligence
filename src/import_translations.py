
import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "jobs.db"
CSV_PATH = ROOT / "translations.csv"

if not CSV_PATH.exists():
    print("No translations.csv found. Skipping import.")
    raise SystemExit(0)

imported = 0

with sqlite3.connect(DB_PATH) as conn:
    with open(CSV_PATH, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            cursor = conn.execute("""
                UPDATE jobs
                SET english_description = ?
                WHERE job_id = ?
                  AND job_description = ?
            """, (
                row["english_description"],
                row["job_id"],
                row["job_description"]
            ))

            imported += cursor.rowcount

print(f"Imported {imported} English translations.")

