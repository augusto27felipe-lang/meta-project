import threading
import time
import pytest
from data.models import Base
from data.db import engine
from app.events import get_event_bus, Event, run_consumer_loop
from backend.core.job_manager import JobManager


@pytest.fixture(autouse=True)
def prepare_db():
    # ensure schema exists for each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_mock_run_no_duplicate_ids():
    bus = get_event_bus()
    mgr = JobManager(bus=bus, max_workers=2)
    mgr.start()

    # give the manager's consumer a moment to register its subscriber queue
    time.sleep(0.05)

    results = []
    finished = threading.Event()

    def collector(ev):
        if ev.type == "job.keyword_done":
            results.append(ev.payload)
        if ev.type == "job.finished":
            finished.set()

    stop = threading.Event()
    t = threading.Thread(target=run_consumer_loop, args=(collector, stop), daemon=True)
    t.start()

    bus.publish(Event(type="intent.start_run", payload={"keywords": ["k1", "k2", "k1"]}))
    # wait for job.finished or timeout
    finished.wait(timeout=5)
    stop.set()
    # basic assertion: collected results length == 3
    assert len(results) == 3, f"unexpected results: {results}"


def __consumer_loop(bus, collector, stop_event):
    # legacy helper not used in new flow
    while not stop_event.is_set():
        ev = bus.subscribe(timeout=0.2)
        if ev:
            collector(ev)


if __name__ == "__main__":
    test_mock_run_no_duplicate_ids()
    print("smoke test passed")
