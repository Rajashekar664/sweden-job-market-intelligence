
import pandas as pd
import re
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
CSV_FILE = PROJECT_DIR / "data" / "sweden_jobs_cleaned.csv"

df = pd.read_csv(CSV_FILE, dtype=str).fillna("")

# Skills and their matching patterns
SKILLS = {
    "Python": r"\bpython\b",
    "SQL": r"\bsql\b",
    "Azure": r"\bazure\b",
    "AWS": r"\baws\b|amazon web services",
    "Docker": r"\bdocker\b",
    "Kubernetes": r"\bkubernetes\b|\bk8s\b",
    "Apache Spark": r"\bspark\b|\bpyspark\b",
    "Databricks": r"\bdatabricks\b",
    "Airflow": r"\bairflow\b",
    "Power BI": r"\bpower\s*bi\b",
    "Snowflake": r"\bsnowflake\b",
    "dbt": r"\bdbt\b",
    "Java": r"\bjava\b",
    "Scala": r"\bscala\b",
    "Git": r"\bgit\b",
    "Terraform": r"\bterraform\b"
}

results = []

for skill, pattern in SKILLS.items():
    count = df["Job Description"].apply(
        lambda text: bool(
            re.search(pattern, text, re.IGNORECASE)
        )
    ).sum()

    results.append({
        "Skill": skill,
        "Job Count": int(count),
        "Percentage": round(
            count / len(df) * 100, 1
        ) if len(df) else 0
    })

skills_df = pd.DataFrame(results)
skills_df = skills_df.sort_values(
    "Job Count",
    ascending=False
)

print("\nTop Technical Skills:")
print(skills_df.to_string(index=False))

output = PROJECT_DIR / "data" / "skills_analysis.csv"
skills_df.to_csv(output, index=False)

print("\nSkills analysis saved successfully!")


import sqlite3

DB_FILE = PROJECT_DIR / "data" / "jobs.db"

with sqlite3.connect(DB_FILE) as conn:

    conn.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            skill_name TEXT PRIMARY KEY,
            job_count INTEGER NOT NULL,
            percentage REAL NOT NULL
        )
    """)

    # Replace old counts with the latest analysis
    conn.execute("DELETE FROM skills")

    for _, row in skills_df.iterrows():
        conn.execute("""
            INSERT INTO skills
                (skill_name, job_count, percentage)
            VALUES (?, ?, ?)
        """, (
            str(row["Skill"]),
            int(row["Job Count"]),
            float(row["Percentage"])
        ))

    count = conn.execute(
        "SELECT COUNT(*) FROM skills"
    ).fetchone()[0]

print(f"Successfully stored {count} skills in SQLite!")

