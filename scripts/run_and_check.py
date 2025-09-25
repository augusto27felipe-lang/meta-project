import sys, os, time, subprocess
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ensure DB schema
print('Seeding DB...')
subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'seed.py')], check=True)

# run demo to generate data
print('Running demo...')
demo = subprocess.Popen([sys.executable, os.path.join(ROOT, 'scripts', 'run_demo.py')])
# give demo time
time.sleep(2)
# demo should exit or we terminate
try:
    demo.terminate()
except Exception:
    pass

# inspect DB using metrics() function
from data.db import SessionLocal
from backend.etapa4_service.main import metrics

with SessionLocal() as db:
    print('METRICS:', metrics(db=db))

# list sample ads and runs
from data.models import Ad, KeywordRun
with SessionLocal() as db:
    ads = db.query(Ad).limit(10).all()
    runs = db.query(KeywordRun).limit(10).all()
    print('ADS COUNT:', db.query(Ad).count())
    for a in ads:
        print('AD:', a.unique_id, a.keyword, a.title)
    print('RUNS COUNT:', db.query(KeywordRun).count())
    for r in runs:
        print('RUN:', r.id, r.keyword, r.duration_s, r.results_count, r.status)

print('Done')
