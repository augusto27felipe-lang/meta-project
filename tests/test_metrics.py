import pytest
from data.db import SessionLocal, engine
from data.models import Base
from data import models
from backend.etapa4_service.main import metrics


@pytest.fixture(autouse=True)
def setup_db():
    # recreate schema for each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_metrics_empty_db():
    with SessionLocal() as db:
        result = metrics(db=db)
    assert result["total_ads"] == 0
    assert result["total_runs"] == 0
    assert result["avg_duration"] is None


def test_metrics_single_run():
    with SessionLocal() as db:
        run = models.KeywordRun(
            keyword="k1", duration_s=1.23, results_count=5, status="finished"
        )
        db.add(run)
        db.commit()
        result = metrics(db=db)
    assert result["total_runs"] == 1
    assert abs(result["avg_duration"] - 1.23) < 1e-6
    assert result["p50_duration"] == result["p95_duration"] == 1.23


def test_metrics_multiple_runs():
    with SessionLocal() as db:
        runs = [
            models.KeywordRun(
                keyword="k1", duration_s=1.0, results_count=2, status="finished"
            ),
            models.KeywordRun(
                keyword="k2", duration_s=2.0, results_count=3, status="finished"
            ),
            models.KeywordRun(
                keyword="k3", duration_s=3.0, results_count=4, status="finished"
            ),
        ]
        db.add_all(runs)
        db.commit()
        result = metrics(db=db)
    assert result["total_runs"] == 3
    assert abs(result["avg_duration"] - 2.0) < 1e-6
    # p50 deve ser 2.0, p95 próximo de 3.0
    assert abs(result["p50_duration"] - 2.0) < 1e-6
    assert result["p95_duration"] <= 3.0
