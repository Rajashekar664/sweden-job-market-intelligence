"""Tests for the Flask REST API in src/app.py."""


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "success"


def test_get_jobs_returns_all_jobs_sorted_by_title(client):
    response = client.get("/api/jobs")
    body = response.get_json()

    assert response.status_code == 200
    assert body["total_jobs"] == 3
    titles = [job["job_title"] for job in body["jobs"]]
    assert titles == sorted(titles)


def test_stats(client):
    body = client.get("/api/stats").get_json()

    assert body == {
        "total_jobs": 3,
        "total_companies": 3,
        "total_cities": 2,
        "total_roles": 3,
    }


def test_search_by_keyword_is_case_insensitive(client):
    body = client.get("/api/jobs/search?keyword=DATA").get_json()

    assert body["total_jobs"] == 2
    assert {job["job_id"] for job in body["jobs"]} == {"1", "2"}


def test_search_by_city_and_company(client):
    body = client.get("/api/jobs/search?city=stockholm&company=Ericsson").get_json()

    assert body["total_jobs"] == 1
    assert body["jobs"][0]["job_title"] == "Cloud Engineer"


def test_search_with_no_match_returns_empty_list(client):
    body = client.get("/api/jobs/search?keyword=astronaut").get_json()

    assert body == {"total_jobs": 0, "jobs": []}


def test_search_treats_sql_characters_as_plain_text(client):
    # Parameterised queries should stop SQL injection
    response = client.get("/api/jobs/search?keyword=' OR 1=1 --")

    assert response.status_code == 200
    assert response.get_json()["total_jobs"] == 0


def test_skills_hides_skills_with_zero_jobs(client):
    body = client.get("/api/skills").get_json()

    names = [skill["skill_name"] for skill in body["skills"]]
    assert names == ["Python", "SQL"]
    assert "Scala" not in names


def test_job_details(client):
    response = client.get("/api/jobs/1")

    assert response.status_code == 200
    assert response.get_json()["company"] == "Spotify"


def test_job_details_unknown_id_returns_404(client):
    assert client.get("/api/jobs/999").status_code == 404


def test_translate_uses_saved_translation(client):
    body = client.get("/api/jobs/2/translate").get_json()

    assert body["english_description"] == "You have experience with Power BI."


def test_translate_job_without_description_returns_404(client):
    assert client.get("/api/jobs/3/translate").status_code == 404


def test_translate_unknown_job_returns_404(client):
    assert client.get("/api/jobs/999/translate").status_code == 404


def test_translate_on_render_without_cache_returns_503(client, monkeypatch):
    monkeypatch.setenv("RENDER", "true")

    assert client.get("/api/jobs/1/translate").status_code == 503


def test_data_route_only_serves_the_cleaned_csv(client):
    assert client.get("/data/jobs.db").status_code == 404


def test_last_updated(client, data_dir):
    (data_dir / "last_updated.txt").write_text("2026-11-18 10:00", encoding="utf-8")

    body = client.get("/api/last-updated").get_json()

    assert body["last_updated"] == "2026-11-18 10:00"


def test_last_updated_missing_file_returns_404(client):
    assert client.get("/api/last-updated").status_code == 404


def test_report_missing_returns_404(client):
    assert client.get("/api/report/download").status_code == 404


def test_endpoints_return_404_when_database_is_missing(client_without_db):
    for url in ["/api/jobs", "/api/stats", "/api/jobs/search", "/api/skills", "/api/jobs/1"]:
        assert client_without_db.get(url).status_code == 404, url


def test_translate_returns_404_when_database_is_missing(client_without_db):
    assert client_without_db.get("/api/jobs/1/translate").status_code == 404
