
import sqlite3
from pathlib import Path
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
DB_FILE = DATA_DIR / "jobs.db"
PDF_FILE = DATA_DIR / "sweden_job_market_report.pdf"

with sqlite3.connect(DB_FILE) as conn:
    total_jobs = conn.execute(
        "SELECT COUNT(*) FROM jobs"
    ).fetchone()[0]

    total_companies = conn.execute(
        "SELECT COUNT(DISTINCT company) FROM jobs"
    ).fetchone()[0]

    top_cities = conn.execute("""
        SELECT city, COUNT(*) AS job_count
        FROM jobs
        GROUP BY city
        ORDER BY job_count DESC
        LIMIT 10
    """).fetchall()

    top_skills = conn.execute("""
        SELECT skill_name, job_count, percentage
        FROM skills
        ORDER BY job_count DESC
        LIMIT 10
    """).fetchall()

styles = getSampleStyleSheet()

doc = SimpleDocTemplate(
    str(PDF_FILE),
    pagesize=A4
)

content = []

content.append(Paragraph(
    "Sweden Job Market Intelligence Report",
    styles["Title"]
))

content.append(Spacer(1, 15))

content.append(Paragraph(
    f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    styles["Normal"]
))

content.append(Spacer(1, 20))

content.append(Paragraph(
    f"<b>Total Jobs:</b> {total_jobs}",
    styles["Normal"]
))

content.append(Paragraph(
    f"<b>Total Companies:</b> {total_companies}",
    styles["Normal"]
))

content.append(Spacer(1, 20))

content.append(Paragraph(
    "Top Cities",
    styles["Heading2"]
))

city_data = [["City", "Job Count"]]
city_data += [
    [str(city), str(count)]
    for city, count in top_cities
]

city_table = Table(city_data)
city_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("PADDING", (0, 0), (-1, -1), 8)
]))

content.append(city_table)
content.append(Spacer(1, 20))

content.append(Paragraph(
    "Top Technical Skills",
    styles["Heading2"]
))

skill_data = [["Skill", "Job Count", "Percentage"]]
skill_data += [
    [str(skill), str(count), f"{percentage}%"]
    for skill, count, percentage in top_skills
]

skill_table = Table(skill_data)
skill_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("PADDING", (0, 0), (-1, -1), 8)
]))

content.append(skill_table)

doc.build(content)

print("PDF report created successfully!")
print("Saved to:", PDF_FILE)
