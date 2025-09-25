import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.etapa4_service.main import app
from data.db import SessionLocal, engine
from data.models import Base
from data import models

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    # recria o schema em memória para cada teste
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def seed_data():
    with SessionLocal() as db:
        run1 = models.KeywordRun(keyword="python", duration_s=1.0, results_count=2, status="finished")
        run2 = models.KeywordRun(keyword="tkinter", duration_s=2.0, results_count=3, status="finished")
        db.add_all([run1, run2])
        db.add_all([
            models.Ad(unique_id="python:example.com:1", keyword="python", title="Ad1", domain="example.com"),
            models.Ad(unique_id="python:example.com:2", keyword="python", title="Ad2", domain="example.com"),
            models.Ad(unique_id="tkinter:another.com:1", keyword="tkinter", title="Ad3", domain="another.com"),
        ])
        db.commit()


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_ads_runs_domains_metrics():
    seed_data()

    # /ads
    resp = client.get("/ads")
    ads = resp.json()
    assert len(ads) == 3
    assert any(ad["keyword"] == "python" for ad in ads)

    # /runs
    resp = client.get("/runs")
    runs = resp.json()
    assert len(runs) == 2
    assert any(run["keyword"] == "tkinter" for run in runs)

    # /domains
    resp = client.get("/domains")
    domains = resp.json()
    assert {"domain": "example.com", "count": 2} in domains
    assert {"domain": "another.com", "count": 1} in domains

    # /metrics
    resp = client.get("/metrics")
    metrics = resp.json()
    assert metrics["total_ads"] == 3
    assert metrics["total_runs"] == 2
    assert "per_keyword" in metrics
    assert metrics["per_keyword"]["python"]["ads"] == 2
    assert metrics["per_keyword"]["tkinter"]["ads"] == 1
