
import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "jobs.db"
OUTPUT_PATH = ROOT / "translations.csv"

with sqlite3.connect(DB_PATH) as conn:
    rows = conn.execute("""
        SELECT job_id, job_description, english_description
        FROM jobs
        WHERE english_description IS NOT NULL
          AND TRIM(english_description) != ''
    """).fetchall()

with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow([
        "job_id",
        "job_description",
        "english_description"
    ])
    writer.writerows(rows)

print(f"Exported {len(rows)} translations to translations.csv")
