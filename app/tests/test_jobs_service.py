from app.services.jobs_service import score_job


def test_score_job_title_match():
    job = {
        "title": "Développeur Python",
        "company": "OpenAI",
        "location": "Paris",
    }

    score = score_job(job, "python")

    assert score >= 10


def test_score_job_no_match():
    job = {
        "title": "Comptable",
        "company": "Entreprise",
        "location": "Lyon",
    }

    score = score_job(job, "python")

    assert score == 0


def test_score_job_company_match():
    job = {
        "title": "Développeur",
        "company": "Python Factory",
        "location": "Marseille",
    }

    score = score_job(job, "python")

    assert score >= 5