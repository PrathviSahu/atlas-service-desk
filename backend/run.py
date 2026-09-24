import os
import sqlite3
from app import create_app   # create_app calls init_db() so tables exist after this

app = create_app()


def _seed_if_empty():
    """Insert demo data if the requests table is empty."""
    db_path = os.getenv("DATABASE_PATH", "./atlas.db")
    try:
        conn = sqlite3.connect(db_path)
        count = conn.execute("SELECT COUNT(*) FROM requests").fetchone()[0]
        conn.close()
        if count == 0:
            import subprocess, sys, pathlib
            seed = pathlib.Path(__file__).parent / "seed.py"
            env = {**os.environ, "DATABASE_PATH": db_path}
            subprocess.run([sys.executable, str(seed)], check=True, env=env)
            print(f"[atlas] Seeded demo data → {db_path}")
        else:
            print(f"[atlas] DB already has {count} requests — skip seed")
    except Exception as exc:
        # Non-fatal: app still starts, DB just has no rows
        print(f"[atlas] Seed warning (non-fatal): {exc}")


if __name__ == "__main__":
    with app.app_context():
        _seed_if_empty()
    port = int(os.getenv("PORT", 5001))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
