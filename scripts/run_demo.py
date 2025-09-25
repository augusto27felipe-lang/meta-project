import threading
import time
import sys
import os

# package imports will be performed inside main() after sys.path is adjusted


def printer(ev):
    print(f"EVENT -> {ev.type}: {ev.payload}")


def main():
    # ensure project root on path
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)

    from app.events import get_event_bus, run_consumer_loop, Event
    from backend.core.job_manager import JobManager

    bus = get_event_bus()
    mgr = JobManager(bus=bus, max_workers=2)
    mgr.start()

    stop = threading.Event()
    t = threading.Thread(target=run_consumer_loop, args=(printer, stop), daemon=True)
    t.start()

    bus.publish(
        Event(type="intent.start_run", payload={"keywords": ["k1", "k2", "k1"]})
    )
    time.sleep(3)
    stop.set()
    mgr.shutdown()


if __name__ == "__main__":
    main()
