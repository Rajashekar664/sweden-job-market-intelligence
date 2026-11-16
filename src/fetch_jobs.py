import logging
import pandas as pd
import requests
from datetime import datetime, timezone

from pathlib import Path

Path("data").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

url = "https://jobsearch.api.jobtechdev.se/search"


def show_project_name():
    logging.info("Sweden Job Market Intelligence Platform")
    
show_project_name()

def fetch_jobs():
    
    all_jobs = []


    offset = 0

    while True:
        
        try:
            response = requests.get(
                url,
                params={
                    "q": "data engineer",
                    "limit": 100,
                    "offset": offset
                },
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

        except requests.exceptions.RequestException as error:
            logging.error("API request failed: %s", error)
            raise


        batch = data.get("hits", [])
        all_jobs.extend(batch)

        logging.info(
            "Offset %s: Retrieved %s jobs",
            offset,
            len(batch)
    )

        if len(batch) < 100:
            break

        offset += 100


    logging.info(
        "Total jobs collected: %s",
        len(all_jobs)
    )
    return all_jobs

all_jobs = fetch_jobs()


def transform_jobs(all_jobs):
    jobs_list = []

    for job in all_jobs:
        title = job.get("headline")
        job_id = job.get("id")

        employer = job.get("employer") or {}
        company = employer.get("name")

        location = job.get("workplace_address") or {}
        city = location.get("municipality")
        
        description_data = job.get("description") or {}

        if isinstance(description_data, dict):
            description = description_data.get("text") or ""
        else:
            description = ""

        if not description:
            description = job.get("text") or ""

        job_info = {
            "Job ID": job_id,
            "Job Title": title,
            "Company": company,
            "City": city,
            "Job Description": description
        }

        jobs_list.append(job_info)

    return jobs_list

jobs_list = transform_jobs(all_jobs)

df = pd.DataFrame(jobs_list)

print(df)
df.to_csv("sweden_jobs.csv", index=False)
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

timestamp_file = PROJECT_DIR / "data" / "last_updated.txt"

timestamp_file.write_text(
    datetime.now(timezone.utc).isoformat(timespec="seconds"),
    encoding="utf-8"
)

print("Collection timestamp saved!")

print("Job data saved successfully!")

print("\nDataset Information:")
print(df.info())
print("\nMissing Values:")
print(df.isnull().sum())


def clean_jobs(df):
    df = df.copy()
    
    df = df.dropna(subset=["Job ID", "Job Title"])
    df = df[
    df["Job ID"].astype(str).str.strip().ne("")
    & df["Job Title"].astype(str).str.strip().ne("")
    ].copy()

    df["Company"] = df["Company"].fillna("Unknown Company")
    df["City"] = df["City"].fillna("Unknown City")

    df = df.drop_duplicates(subset=["Job ID"], keep="first")

    return df


df = clean_jobs(df)

if df.empty:
    raise ValueError("No valid job advertisements found!")

logging.info("Dataset contains %s valid jobs", len(df))

# Validate that essential fields have no missing values
assert df["Job ID"].notna().all(), "Missing Job IDs detected"
assert df["Job Title"].notna().all(), "Missing Job Titles detected"

# Validate that Job IDs are unique
assert df["Job ID"].is_unique, "Duplicate Job IDs detected"

logging.info("Data quality validation passed!")

missing_ids = df["Job ID"].isna().sum()

logging.info("Jobs with missing IDs: %s", missing_ids)

missing_titles = df["Job Title"].isna().sum()

logging.info("Jobs with missing titles: %s", missing_titles)

print("\nMissing Values After Cleaning:")
print(df.isnull().sum())


df.to_csv("data/sweden_jobs.csv", index=False)

print("Cleaned job data saved successfully!")

# Check for duplicate records
duplicates = df.duplicated().sum()

print("\nNumber of duplicate records:", duplicates)

# Check the number of remaining jobs
print("\nTotal jobs after removing duplicates:", len(df))

# Save the updated cleaned dataset
df.to_csv("data/sweden_jobs_cleaned.csv", index=False)

print("Duplicate removal completed!")

unique_companies = df["Company"].nunique()

logging.info("Total unique companies: %s", unique_companies)

top_companies = (
    df[df["Company"] != "Unknown Company"]["Company"]
    .value_counts()
    .head(10)
)

print("\nTop 10 Companies Advertising Jobs:")
print(top_companies)

top_cities = (
    df[df["City"] != "Unknown City"]["City"]
    .value_counts()
    .head(10)
)

print("\nTop 10 Cities Advertising Jobs:")
print(top_cities)

city_counts = (
    df[df["City"] != "Unknown City"]["City"]
    .value_counts()
    .rename_axis("City")
    .reset_index(name="Total Jobs")
)

city_counts.to_csv(
    "data/jobs_by_city.csv",
    index=False
)

logging.info("City analysis saved successfully!")


company_counts = (
    df[df["Company"] != "Unknown Company"]["Company"]
    .value_counts()
    .rename_axis("Company")
    .reset_index(name="Total Jobs")
)

company_counts.to_csv(
    "data/jobs_by_company.csv",
    index=False
)

logging.info("Company analysis saved successfully!")
