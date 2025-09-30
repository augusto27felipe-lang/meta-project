import sys
import os

# make project root importable when running this script directly
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.main import app
import uvicorn
import signal
import time
import atexit
import os


PID_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'uvicorn.pid')


def write_pid(pid: int):
    try:
        os.makedirs(os.path.dirname(PID_FILE), exist_ok=True)
        with open(PID_FILE, 'w') as f:
            f.write(str(pid))
    except Exception:
        pass


def remove_pid():
    try:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
    except Exception:
        pass


def _handle_exit(signum, frame):
    # uvicorn will handle shutdown; ensure pid file removed on exit
    remove_pid()


if __name__ == '__main__':
    # register pid removal on normal exit
    atexit.register(remove_pid)
    signal.signal(signal.SIGINT, _handle_exit)
    try:
        # write our pid so an external launcher can see it's running
        write_pid(os.getpid())
    except Exception:
        pass

    # Determine port from CLI --port or UVICORN_PORT env var, default 8000
    port = None
    for arg in sys.argv[1:]:
        if arg.startswith('--port='):
            try:
                port = int(arg.split('=', 1)[1])
            except Exception:
                port = None
    if port is None:
        try:
            port = int(os.environ.get('UVICORN_PORT', '8000'))
        except Exception:
            port = 8000

    # use uvicorn Server to allow graceful shutdown
    config = uvicorn.Config(app, host='127.0.0.1', port=port, log_level='info')
    server = uvicorn.Server(config)

    try:
        server.run()
    finally:
        remove_pid()
