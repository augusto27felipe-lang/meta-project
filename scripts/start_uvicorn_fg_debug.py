import sys
import os
import signal
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.etapa4_service.main import app
import uvicorn


def _on_signal(sig, frame):
    print(f"Received signal: {sig}, frame={frame}")


for s in (signal.SIGINT, signal.SIGTERM):
    try:
        signal.signal(s, _on_signal)
    except Exception:
        # Not all signals are supported on all platforms
        pass


def main():
    print("[debug runner] about to start uvicorn (debug logging)")
    try:
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")
    except Exception:
        print("[debug runner] exception during uvicorn.run:")
        traceback.print_exc()
        raise
    finally:
        print("[debug runner] uvicorn.run returned, exiting")


if __name__ == "__main__":
    main()
