import sys, os, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# run demo to create data
from subprocess import Popen
p = Popen([sys.executable, os.path.join(ROOT, 'scripts', 'run_demo.py')])
# give demo time to run
time.sleep(2)

import requests

print('GET /metrics')
r = requests.get('http://127.0.0.1:8000/metrics')
print(r.status_code, r.json())

print('GET /events')
r = requests.get('http://127.0.0.1:8000/events')
print(r.status_code)
print(r.text[:1000])

p.terminate()
