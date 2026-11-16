
import sqlite3
import pandas as pd
from pathlib import Path

# Locate project folders
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

CSV_FILE = DATA_DIR / "sweden_jobs_cleaned.csv"
DB_FILE = DATA_DIR / "jobs.db"

# Check CSV exists
if not CSV_FILE.exists():
    raise FileNotFoundError(
        f"CSV file not found: {CSV_FILE}"
    )

# Load cleaned job data
df = pd.read_csv(CSV_FILE, dtype=str)

# Check required columns
required = [
    "Job ID",
    "Job Title",
    "Company",
    "City",
    "Job Description"
]

for column in required:
    if column not in df.columns:
        raise ValueError(f"Missing column: {column}")
    
# Validate job IDs before updating SQLite
job_ids = df["Job ID"].astype("string").str.strip()

if job_ids.isna().any() or job_ids.eq("").any():
    raise ValueError("Missing Job IDs found. Database update cancelled.")

if job_ids.duplicated().any():
    raise ValueError("Duplicate Job IDs found. Database update cancelled.")

df["Job ID"] = job_ids

print("Job ID validation passed!")

# Connect to SQLite database
with sqlite3.connect(DB_FILE) as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            job_title TEXT NOT NULL,
            company TEXT,
            city TEXT
        )
    """)

    # Insert or update job records
    for _, job in df.iterrows():
        conn.execute("""
            INSERT INTO jobs
                (job_id, job_title, company, city)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(job_id) DO UPDATE SET
                job_title = excluded.job_title,
                company = excluded.company,
                city = excluded.city
        """, (
            job["Job ID"],
            job["Job Title"],
            job["Company"],
            job["City"]
        ))

    count = conn.execute(
        "SELECT COUNT(*) FROM jobs"
    ).fetchone()[0]

print("Database created successfully!")
print("Database location:", DB_FILE)
print("Total jobs in database:", count)



# Add job descriptions to the existing database

with sqlite3.connect(DB_FILE) as conn:

    columns = [
        row[1]
        for row in conn.execute("PRAGMA table_info(jobs)")
    ]

    if "job_description" not in columns:
        conn.execute("""
            ALTER TABLE jobs
            ADD COLUMN job_description TEXT
        """)

    for _, job in df.iterrows():
        conn.execute("""
            UPDATE jobs
            SET
                english_description = CASE
                    WHEN job_description IS NOT ?
                    THEN NULL
                    ELSE english_description
                END,
                job_description = ?
            WHERE job_id = ?
        """, (
            job["Job Description"],
            job["Job Description"],
            job["Job ID"]
        ))
        

    # Remove jobs that are no longer in the latest CSV
    current_job_ids = df["Job ID"].dropna().tolist()

    if not current_job_ids:
        raise ValueError("CSV contains no job IDs. Deletion cancelled.")

    placeholders = ",".join("?" for _ in current_job_ids)

    conn.execute(
        f"DELETE FROM jobs WHERE job_id NOT IN ({placeholders})",
        current_job_ids
    )

    print("Outdated job listings removed successfully!")


print("Job descriptions stored successfully!")

