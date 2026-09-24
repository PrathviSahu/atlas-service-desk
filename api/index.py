"""
Vercel Python serverless entry point for Atlas Service Desk.

SQLite lives in /tmp (ephemeral per Vercel instance). The database is
seeded automatically on cold start so the demo data is always present.
"""
import sys, os, pathlib

# Add backend/ to Python path so all app imports resolve
_root = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(_root / 'backend'))

os.environ['DATABASE_PATH'] = '/tmp/atlas.db'
os.environ['FRONTEND_ORIGIN'] = '*'

from app import create_app   # this also creates the DB schema via init_db()

app = create_app()

# Seed demo data on cold start.
# create_app already created the tables; seed.py inserts the rows.
# Safe to call every cold start — seed.py does DELETE then INSERT OR REPLACE.
def _seed():
    try:
        import importlib.util
        seed_path = _root / 'backend' / 'seed.py'
        spec = importlib.util.spec_from_file_location('seed', seed_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as exc:
        # Log but don't crash — the app still works with an empty DB
        print(f'[atlas] auto-seed failed: {exc}', flush=True)

with app.app_context():
    _seed()

# Vercel looks for a callable named 'app' or 'handler'
handler = app
