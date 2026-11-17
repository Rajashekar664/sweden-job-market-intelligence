#!/usr/bin/env bash
set -e

pip install -r requirements.txt

mkdir -p data

python src/fetch_jobs.py
python src/create_database.py
python src/analyze_skills.py
python src/install_translation_model.py
python src/generate_report.py