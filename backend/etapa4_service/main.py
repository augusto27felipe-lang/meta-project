from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict

from data.db import get_session
from data.models import EventRecord, KeywordRun, Ad


app = FastAPI(title="Etapa4 Service - V3.1")


def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/events")
def list_events(limit: int = 50, db: Session = Depends(get_db)):
    rows = db.query(EventRecord).order_by(EventRecord.id.desc()).limit(limit).all()
    return JSONResponse(
        [
            {
                "id": r.id,
                "type": r.type,
                "payload": r.payload,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]
    )


def _percentile(values, p: float):
    if not values:
        return None
    k = (len(values) - 1) * p
    f = int(k)
    c = min(f + 1, len(values) - 1)
    if f == c:
        return values[int(k)]
    d0 = values[f] * (c - k)
    d1 = values[c] * (k - f)
    return d0 + d1


@app.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    total_ads = db.query(func.count(Ad.id)).scalar() or 0
    total_runs = db.query(func.count(KeywordRun.id)).scalar() or 0
    avg_duration = db.query(func.avg(KeywordRun.duration_s)).scalar()
    # collect durations and compute percentiles in Python (SQLite compatibility)
    flat = [
        d
        for (d,) in db.query(KeywordRun.duration_s)
        .filter(KeywordRun.duration_s.is_not(None))
        .all()
    ]
    p50 = None
    p95 = None
    if flat:
        flat_sorted = sorted(flat)

        def pct(arr, q):
            if not arr:
                return None
            n = len(arr)
            idx = (n - 1) * q
            lo = int(idx)
            hi = min(lo + 1, n - 1)
            if lo == hi:
                return arr[lo]
            return arr[lo] * (hi - idx) + arr[hi] * (idx - lo)

        p50 = pct(flat_sorted, 0.5)
        p95 = pct(flat_sorted, 0.95)

    # per-keyword breakdown
    per_keyword = defaultdict(lambda: {"runs": 0, "ads": 0, "avg_duration": None})
    runs = db.query(KeywordRun).all()
    ads = db.query(Ad).all()
    for r in runs:
        pk = per_keyword[r.keyword]
        pk["runs"] += 1
        if r.duration_s is not None:
            if pk["avg_duration"] is None:
                pk["avg_duration"] = float(r.duration_s)
            else:
                # simple running average (not weighted)
                pk["avg_duration"] = (pk["avg_duration"] + float(r.duration_s)) / 2
    for a in ads:
        per_keyword[a.keyword]["ads"] += 1

    # convert defaultdict to plain dict for JSON
    per_keyword = {k: v for k, v in per_keyword.items()}

    return {
        "total_ads": int(total_ads),
        "total_runs": int(total_runs),
        "avg_duration": float(avg_duration) if avg_duration is not None else None,
        "p50_duration": float(p50) if p50 is not None else None,
        "p95_duration": float(p95) if p95 is not None else None,
        "per_keyword": per_keyword,
    }


@app.get("/ads")
def list_ads(db: Session = Depends(get_db)):
    rows = db.query(Ad).order_by(Ad.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "keyword": r.keyword,
            "title": r.title,
            "domain": r.domain,
            "created_at": r.created_at.isoformat() if r.created_at is not None else None,
        }
        for r in rows
    ]


@app.get("/runs")
def list_runs(db: Session = Depends(get_db)):
    rows = db.query(KeywordRun).order_by(KeywordRun.started_at.desc()).all()
    return [
        {
            "id": r.id,
            "keyword": r.keyword,
            "started_at": r.started_at.isoformat() if r.started_at is not None else None,
            "duration_s": float(r.duration_s) if r.duration_s is not None else None,
            "results_count": int(r.results_count) if r.results_count is not None else None,
            "status": r.status,
        }
        for r in rows
    ]


@app.get("/domains")
def list_domains(db: Session = Depends(get_db)):
    rows = db.query(Ad.domain, func.count(Ad.id)).group_by(Ad.domain).all()
    return [{"domain": d, "count": int(c)} for d, c in rows]
