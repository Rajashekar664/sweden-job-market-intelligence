import sqlite3
from pathlib import Path
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__)

PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_FILE = PROJECT_DIR / "data" / "jobs.db"

@app.route("/api/health")
def health():
    return jsonify({
        "status": "success",
        "message": "Sweden Job Market API is running"
    })
    
    



BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

@app.route("/")
def dashboard():
    return send_from_directory(
        BASE_DIR / "dashboard",
        "index.html"
    )

@app.route("/dashboard/<path:filename>")
def dashboard_files(filename):
    return send_from_directory(
        BASE_DIR / "dashboard",
        filename
    )

@app.route("/data/<path:filename>")
def data_files(filename):
    if filename != "sweden_jobs_cleaned.csv":
        return {"error": "File not found"}, 404

    return send_from_directory(
        PROJECT_DIR / "data",
        filename
    )


# Get all job advertisements from SQLite
@app.route("/api/jobs", methods=["GET"])
def get_jobs():

    if not DB_FILE.exists():
        return jsonify({
            "error": "Database not found"
        }), 404

    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row

            rows = conn.execute("""
                SELECT
                    job_id,
                    job_title,
                    company,
                    city
                FROM jobs
                ORDER BY job_title
            """).fetchall()

        jobs = [dict(row) for row in rows]

        return jsonify({
            "total_jobs": len(jobs),
            "jobs": jobs
        })

    except sqlite3.Error:
        app.logger.exception("Database query failed")
        return jsonify({
            "error": "Unable to retrieve jobs"
        }), 500


@app.route("/api/stats", methods=["GET"])
def get_job_statistics():

    if not DB_FILE.exists():
        return jsonify({
            "error": "Database not found"
        }), 404

    try:
        with sqlite3.connect(DB_FILE) as conn:
            total_jobs = conn.execute(
                "SELECT COUNT(*) FROM jobs"
            ).fetchone()[0]

            total_companies = conn.execute("""
                SELECT COUNT(DISTINCT company)
                FROM jobs
                WHERE company IS NOT NULL
                  AND company != 'Unknown Company'
            """).fetchone()[0]

            total_cities = conn.execute("""
                SELECT COUNT(DISTINCT city)
                FROM jobs
                WHERE city IS NOT NULL
                  AND city != 'Unknown City'
            """).fetchone()[0]

            total_roles = conn.execute("""
                SELECT COUNT(DISTINCT job_title)
                FROM jobs
            """).fetchone()[0]

        return jsonify({
            "total_jobs": total_jobs,
            "total_companies": total_companies,
            "total_cities": total_cities,
            "total_roles": total_roles
        })

    except sqlite3.Error:
        app.logger.exception("Statistics query failed")
        return jsonify({
            "error": "Unable to retrieve statistics"
        }), 500


from flask import request

@app.route("/api/jobs/search", methods=["GET"])
def search_jobs():

    keyword = request.args.get("keyword", "").strip()
    city = request.args.get("city", "").strip()
    company = request.args.get("company", "").strip()

    if not DB_FILE.exists():
        return jsonify({
            "error": "Database not found"
        }), 404

    query = """
        SELECT job_id, job_title, company, city
        FROM jobs
        WHERE 1=1
    """

    params = []

    if keyword:
        query += """
            AND (
                job_title LIKE ? COLLATE NOCASE
                OR company LIKE ? COLLATE NOCASE
                OR city LIKE ? COLLATE NOCASE
            )
        """
        pattern = f"%{keyword}%"
        params.extend([pattern, pattern, pattern])

    if city:
        query += " AND city = ? COLLATE NOCASE"
        params.append(city)

    if company:
        query += " AND company = ? COLLATE NOCASE"
        params.append(company)

    query += " ORDER BY job_title"

    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()

        jobs = [dict(row) for row in rows]

        return jsonify({
            "total_jobs": len(jobs),
            "jobs": jobs
        })

    except sqlite3.Error:
        app.logger.exception("Job search failed")
        return jsonify({
            "error": "Unable to search jobs"
        }), 500


@app.route("/api/skills", methods=["GET"])
def get_skills():

    if not DB_FILE.exists():
        return jsonify({
            "error": "Database not found"
        }), 404

    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row

            rows = conn.execute("""
                SELECT
                    skill_name,
                    job_count,
                    percentage
                FROM skills
                WHERE job_count > 0
                ORDER BY job_count DESC, skill_name ASC
            """).fetchall()

        skills = [dict(row) for row in rows]

        return jsonify({
            "total_skills": len(skills),
            "skills": skills
        })

    except sqlite3.Error:
        app.logger.exception("Skills query failed")
        return jsonify({
            "error": "Unable to retrieve skills"
        }), 500
        

# Retrieve details for one job
@app.route("/api/jobs/<job_id>", methods=["GET"])
def get_job_details(job_id):

    if not DB_FILE.exists():
        return jsonify({
            "error": "Database not found"
        }), 404

    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row

            job = conn.execute("""
                SELECT
                    job_id,
                    job_title,
                    company,
                    city,
                    job_description
                FROM jobs
                WHERE job_id = ?
            """, (job_id,)).fetchone()

        if job is None:
            return jsonify({
                "error": "Job not found"
            }), 404

        return jsonify(dict(job))

    except sqlite3.Error:
        app.logger.exception(
            "Failed to retrieve job details"
        )

        return jsonify({
            "error": "Unable to retrieve job details"
        }), 500

@app.route("/api/jobs/<job_id>/translate", methods=["GET"])
def translate_job_description(job_id):
    if not DB_FILE.exists():
        return jsonify({
            "error": "Database not found"
        }), 404

    with sqlite3.connect(DB_FILE) as conn:
        row = conn.execute(
            "SELECT job_description FROM jobs WHERE job_id = ?",
            (job_id,)
        ).fetchone()

    if row is None:
        return jsonify({"error": "Job not found"}), 404

    description = (row[0] or "").strip()

    if not description:
        return jsonify({"error": "No description available"}), 404

    
    try:
        # Check whether an English translation is already saved
        with sqlite3.connect(DB_FILE) as conn:
            cached = conn.execute("""
                SELECT english_description
                FROM jobs
                WHERE job_id = ?
            """, (job_id,)).fetchone()

        translated = cached[0] if cached and cached[0] else None

        if translated:
            print("Using saved English translation!")
        else:
            import os

            if os.environ.get("RENDER") == "true":
                return jsonify({
                    "error": "English translation is not cached for this job."
                }), 503
            print("Translating description with Argos...")
            
            import argostranslate.translate
            
            translated = argostranslate.translate.translate(
                description,
                "sv",
                "en"
            )

            # Save translation for future requests
            with sqlite3.connect(DB_FILE) as conn:
                conn.execute("""
                    UPDATE jobs
                    SET english_description = ?
                    WHERE job_id = ?
                      AND job_description = ?
                """, (translated, job_id, description))

            print("English translation saved in SQLite!")

        return jsonify({
            "job_id": job_id,
            "original_description": description,
            "english_description": translated
        })



    except Exception:
        app.logger.exception("Translation failed")
        return jsonify({
            "error": "Translation service unavailable."
        }), 503
@app.route("/api/last-updated", methods=["GET"])
def get_last_updated():
    timestamp_file = PROJECT_DIR / "data" / "last_updated.txt"

    if not timestamp_file.exists():
        return jsonify({
            "error": "Collection timestamp not found"
        }), 404

    timestamp = timestamp_file.read_text(
        encoding="utf-8"
    ).strip()

    return jsonify({
        "last_updated": timestamp,
        "label": "Last data collection"
    })
    
@app.route("/api/report/download", methods=["GET"])
def download_report():
    report_file = PROJECT_DIR / "data" / "sweden_job_market_report.pdf"

    if not report_file.exists():
        return jsonify({
            "error": "PDF report not found"
        }), 404

    return send_from_directory(
        report_file.parent,
        report_file.name,
        as_attachment=True
    )

if __name__ == "__main__":
    app.run(port=5000)
