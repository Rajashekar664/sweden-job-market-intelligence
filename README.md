# Sweden Job Market Intelligence Platform

A full-stack job market analytics application that collects, processes, analyzes, and visualizes Data Engineering job advertisements in Sweden.

The platform uses job advertisement data from Sweden's JobTech API to explore hiring trends, technical skills, companies, and geographic demand.

## Features

- **Job Market Dashboard:** Interactive statistics and visualizations of job advertisements.
- **Job Search:** Filter advertisements by keyword, city, and company.
- **Technical Skills Analysis:** Analyze mentions of Python, SQL, Azure, AWS, Databricks, and other technologies in job descriptions.
- **Job Details:** View individual advertisements and full job descriptions.
- **Swedish-to-English Translation:** Translate Swedish job descriptions offline using Argos Translate.
- **Translation Caching:** Store English translations in SQLite to avoid repeated processing.
- **Data Synchronization:** Update job records and remove outdated advertisements.
- **CSV Export:** Download job advertisements matching the selected filters.
- **PDF Report:** Generate and download a summary of job market statistics.
- **Collection Timestamp:** Display when job advertisements were last collected.

## Technology Stack

| Layer | Technologies |
|---|---|
| Data collection | Python, Requests, JobTech API |
| Data processing | Pandas |
| Database | SQLite |
| Backend | Flask |
| Frontend | HTML, CSS, JavaScript |
| Data visualization | Chart.js |
| Translation | Argos Translate |
| PDF generation | ReportLab |
| Version control | Git, GitHub |

## Project Structure

```text
sweden-job-market-intelligence/
├── src/
│   ├── dashboard/
│   │   ├── index.html
│   │   ├── style.css
│   │   └── script.js
│   ├── app.py
│   ├── fetch_jobs.py
│   ├── analyze_jobs.py
│   ├── analyze_skills.py
│   ├── create_database.py
│   ├── add_translation_cache.py
│   ├── install_translation_model.py
│   └── generate_report.py
├── data/                # Generated locally
├── run.py
├── .gitignore
└── README.md
```

## How It Works

1. Fetch Data Engineering job advertisements from the Swedish JobTech API.
2. Clean and validate the data using Pandas.
3. Save the cleaned dataset to CSV.
4. Synchronize job listings with SQLite.
5. Extract and analyze technical skill mentions.
6. Serve job data through Flask REST API endpoints.
7. Display statistics and interactive charts in the web dashboard.
8. Allow users to search, view, translate, and export advertisements.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Rajashekar664/sweden-job-market-intelligence.git
cd sweden-job-market-intelligence
```

### 2. Create a Python virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

Install the required Python libraries:

```bash
python -m pip install flask requests pandas argostranslate reportlab
```

### 4. Prepare the job dataset

```bash
python src/fetch_jobs.py
python src/create_database.py
python src/analyze_skills.py
```

These commands fetch current job advertisements, build the local SQLite database, and calculate technical skill statistics.

### 5. Install the translation model

```bash
python src/install_translation_model.py
python src/add_translation_cache.py
```

The translation model must be downloaded before offline Swedish-to-English translation becomes available.

### 6. Generate the PDF report

```bash
python src/generate_report.py
```

### 7. Start the application

```bash
python src/app.py
```

Open your browser at:

http://127.0.0.1:5000/

## API Endpoints

| Endpoint | Description |
|---|---|
| `/api/health` | Application health status |
| `/api/jobs` | Retrieve job listings |
| `/api/jobs/search` | Search by keyword, city, and company |
| `/api/jobs/<job_id>` | Retrieve one job's details |
| `/api/jobs/<job_id>/translate` | Translate a job description into English |
| `/api/stats` | Job market summary statistics |
| `/api/skills` | Technical skill frequencies |
| `/api/last-updated` | Last data collection timestamp |
| `/api/report/download` | Download the generated PDF report |

## Data Source and Scope

Job advertisements are collected from Sweden's JobTech API.

The current collection focuses on advertisements matching a Data Engineering search query. Therefore, the results represent a subset of Swedish job advertisements, not the entire Swedish labor market.

Technical skills are identified using predefined keyword patterns. A skill mention does not necessarily mean the skill is mandatory for the position.

Job advertisements change over time, and analysis results depend on the collection date.

## Project Status

**Working local full-stack application.**

Core backend, database, dashboard, search, filtering, translation, CSV export, and PDF report functionality have been implemented.

Public deployment and additional automated testing are planned.

## Author

Developed as a portfolio project demonstrating Python data engineering, REST API development, relational databases, data visualization, and full-stack application development.
