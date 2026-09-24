import os
from app import create_app

app = create_app()

def _seed_on_startup():
    """Seed demo data on first start if DB is empty."""
    db_path = os.getenv("DATABASE_PATH", "./atlas.db")
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        count = conn.execute("SELECT COUNT(*) FROM requests").fetchone()[0]
        conn.close()
        if count == 0:
            import subprocess, sys
            subprocess.run([sys.executable, "seed.py"], check=True,
                          env={**os.environ, "DATABASE_PATH": db_path})
            print(f"[atlas] Auto-seeded demo data into {db_path}")
        else:
            print(f"[atlas] DB has {count} requests — skipping seed")
    except Exception as e:
        print(f"[atlas] Startup seed warning: {e}")

if __name__ == "__main__":
    with app.app_context():
        _seed_on_startup()
    port = int(os.getenv("PORT", 5001))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
