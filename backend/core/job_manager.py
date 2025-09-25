import threading
from concurrent.futures import ThreadPoolExecutor
import time
from typing import List, Dict
from app.events import get_event_bus, Event, run_consumer_loop
from data.db import SessionLocal
from data.models import Ad, KeywordRun
from backend.core.adapters.mock_adapter import MockAdapter


class JobManager:
    """JobManager orquestra adapters and persistence, publishing progress events."""

    def __init__(self, bus=None, max_workers: int = 4):
        self.bus = bus or get_event_bus()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.adapter = MockAdapter()
        self._lock = threading.Lock()
        self._stop = threading.Event()
        # consumer listens to intents
        self.consumer_thread = threading.Thread(
            target=run_consumer_loop,
            args=(self._handle_intent, self._stop),
            daemon=True,
        )

    def start(self):
        # start adapter if needed
        try:
            self.adapter.start()
        except Exception:
            pass
        self.consumer_thread.start()

    def shutdown(self, wait: bool = True):
        self._stop.set()
        self.executor.shutdown(wait=wait)

    def _handle_intent(self, ev: Event):
        if ev.type == "intent.start_run":
            payload = ev.payload or {}
            keywords = payload.get("keywords", [])
            country = payload.get("country", "US")
            self.start_keywords_job(keywords, country=country)

        elif ev.type == "intent.stop_run":
            self.bus.publish(Event(type="job.stop_requested", payload={}))
            self._stop.set()

    def start_keywords_job(self, keywords: List[str], country: str = "US"):
        """Public API: start a keywords job asynchronously."""
        self.bus.publish(
            Event(
                type="job.started", payload={"keywords": keywords, "country": country}
            )
        )
        # dispatch to executor so caller isn't blocked
        self.executor.submit(self._run_keywords_job, keywords, country)

    def _run_keywords_job(self, keywords: List[str], country: str):
        with self._lock:
            for kw in keywords:
                if self._stop.is_set():
                    break
                try:
                    # start run record
                    run_record = None
                    start_ts = time.time()
                    with SessionLocal() as session:
                        run_record = KeywordRun(
                            keyword=kw,
                            started_at=None,
                            duration_s=0.0,
                            results_count=0,
                            status="running",
                        )
                        session.add(run_record)
                        session.commit()
                        session.refresh(run_record)

                    self.bus.publish(
                        Event(
                            type="job.progress",
                            payload={"keyword": kw, "status": "searching"},
                        )
                    )
                    ads = self.adapter.search(kw, country=country)

                    persisted: List[Dict] = []
                    # persist in DB with safe upsert (query by unique_id then update/insert)
                    with SessionLocal() as session:
                        for ad in ads:
                            unique_id = (
                                ad.get("unique_id")
                                or ad.get("id")
                                or f"{kw}:{time.time()}"
                            )
                            existing = (
                                session.query(Ad)
                                .filter_by(unique_id=unique_id)
                                .one_or_none()
                            )
                            if existing is not None:
                                # update fields
                                existing.keyword = kw
                                existing.country = ad.get("country", country)
                                existing.domain = ad.get("domain")
                                existing.title = ad.get("title")
                                existing.body = ad.get("body")
                                existing.media_url = ad.get("media_url")
                                session.add(existing)
                            else:
                                ad_obj = Ad(
                                    unique_id=unique_id,
                                    keyword=kw,
                                    country=ad.get("country", country),
                                    domain=ad.get("domain"),
                                    title=ad.get("title"),
                                    body=ad.get("body"),
                                    media_url=ad.get("media_url"),
                                )
                                session.add(ad_obj)
                            persisted.append({"unique_id": unique_id})
                        session.commit()

                    duration = time.time() - start_ts
                    # update run_record with duration and results
                    with SessionLocal() as session:
                        rr = session.get(KeywordRun, run_record.id)
                        rr.duration_s = duration
                        rr.results_count = len(persisted)
                        rr.status = "finished"
                        session.add(rr)
                        session.commit()

                    self.bus.publish(
                        Event(
                            type="job.keyword_done",
                            payload={
                                "keyword": kw,
                                "count": len(persisted),
                                "ads": persisted,
                            },
                        )
                    )
                except Exception as e:
                    self.bus.publish(
                        Event(
                            type="job.error", payload={"keyword": kw, "error": str(e)}
                        )
                    )

            self.bus.publish(Event(type="job.finished", payload={"keywords": keywords}))


def run_manager_forever():
    mgr = JobManager()
    mgr.start()
    return mgr


if __name__ == "__main__":
    m = run_manager_forever()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        m.shutdown()
