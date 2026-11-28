import sqlite3
import sys
from pathlib import Path

import pytest

# Make the "src" folder importable so we can import app.py
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC_DIR))

import app as app_module  # noqa: E402


SAMPLE_JOBS = [
    ("1", "Data Engineer", "Spotify", "Stockholm",
     "Vi söker en data engineer med Python och SQL.", None),
    ("2", "Data Analyst", "Volvo", "Göteborg",
     "Du har erfarenhet av Power BI.", "You have experience with Power BI."),
    ("3", "Cloud Engineer", "Ericsson", "Stockholm", "", None),
]

SAMPLE_SKILLS = [
    ("Python", 10, 50.0),
    ("SQL", 8, 40.0),
    ("Scala", 0, 0.0),
]


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    """Create a temporary data folder with a small test database."""
    data = tmp_path / "data"
    data.mkdir()
    db_file = data / "jobs.db"

    with sqlite3.connect(db_file) as conn:
        conn.execute("""
            CREATE TABLE jobs (
                job_id TEXT PRIMARY KEY,
                job_title TEXT NOT NULL,
                company TEXT,
                city TEXT,
                job_description TEXT,
                english_description TEXT
            )
        """)
        conn.executemany("INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?)", SAMPLE_JOBS)
        conn.execute("""
            CREATE TABLE skills (
                skill_name TEXT PRIMARY KEY,
                job_count INTEGER NOT NULL,
                percentage REAL NOT NULL
            )
        """)
        conn.executemany("INSERT INTO skills VALUES (?, ?, ?)", SAMPLE_SKILLS)

    # Point the app at the test database instead of the real one
    monkeypatch.setattr(app_module, "DB_FILE", db_file)
    monkeypatch.setattr(app_module, "PROJECT_DIR", tmp_path)
    return data


@pytest.fixture
def client(data_dir):
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as test_client:
        yield test_client


@pytest.fixture
def client_without_db(tmp_path, monkeypatch):
    """A client whose database file does not exist."""
    monkeypatch.setattr(app_module, "DB_FILE", tmp_path / "data" / "missing.db")
    monkeypatch.setattr(app_module, "PROJECT_DIR", tmp_path)
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as test_client:
        yield test_client
