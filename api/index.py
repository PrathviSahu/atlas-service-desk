"""
Vercel Python serverless entry point for Atlas Service Desk.

SQLite lives in /tmp (ephemeral on Vercel). Demo data is seeded inline
on every cold start so the evaluator always sees R101-R108 / T1-T3.
"""
import sys, os, pathlib, sqlite3

_root = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(_root / 'backend'))

DB_PATH = '/tmp/atlas.db'
os.environ['DATABASE_PATH'] = DB_PATH
os.environ['FRONTEND_ORIGIN'] = '*'

from app import create_app          # creates the schema via init_db()
from app.models.database import init_db

app = create_app()

# ── Inline seed ────────────────────────────────────────────────────────────
# Seeds unconditionally on every cold start.
# init_db() already ran inside create_app(), so the tables exist.
_TECHNICIANS = [
    ("T1", "Alex Morgan",  "available"),
    ("T2", "Jordan Lee",   "available"),
    ("T3", "Sam Rivera",   "available"),
]

_REQUESTS = [
    # (id, customer, channel, message, received_at, priority, status,
    #  technician_id, is_dup, dup_of, needs_clarif, missing_info, notes)
    ("R101","C01","email",
     "Cold-room unit keeps stopping. Stored goods could be affected.",
     "2026-09-30T16:10:00","urgent","open",None,0,None,0,None,
     "Received via email. Stored goods at risk — urgent."),
    ("R102","C02","whatsapp",
     "Can you confirm when someone is coming for yesterday's pump request?",
     "2026-10-01T08:20:00","high","assigned","T1",0,None,0,None,
     "Assigned T1; no visit time recorded."),
    ("R103","C03","phone",
     "Routine inspection request for next week.",
     "2026-09-30T11:00:00","normal","open",None,0,None,0,None,None),
    ("R104","C01","email",
     "Following up on the cold-room fault reported yesterday.",
     "2026-10-01T08:25:00","urgent","open",None,0,None,0,None,
     "Possible duplicate of R101 — same customer, cold-room issue."),
    ("R105","C04","phone",
     "Machine not working. Please call us.",
     "2026-10-01T08:30:00","normal","open",None,0,None,1,
     "Equipment identifier missing",None),
    ("R106","C05","email",
     "We are waiting for the replacement part and an update.",
     "2026-09-29T14:00:00","normal","waiting","T2",0,None,0,None,
     "Assigned T2; waiting for replacement part."),
    ("R107","C06","whatsapp",
     "Thanks, the unit is running again.",
     "2026-09-30T15:00:00","normal","in_progress","T3",0,None,0,None,
     "Customer confirmed resolved — update status to Resolved."),
    ("R108","C07","email",
     "Please send someone today for a pressure warning.",
     "2026-10-01T08:40:00","urgent","open",None,0,None,1,
     "Equipment identifier missing",None),
]

def _seed_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("DELETE FROM requests")
        conn.execute("DELETE FROM technicians")
        for t in _TECHNICIANS:
            conn.execute(
                "INSERT OR REPLACE INTO technicians (id, name, status) VALUES (?,?,?)", t)
        for r in _REQUESTS:
            conn.execute("""
                INSERT OR REPLACE INTO requests
                  (id, customer_id, channel, message, received_at, priority, status,
                   technician_id, is_duplicate, duplicate_of,
                   needs_clarification, missing_information, notes)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""", r)
        conn.commit()
        conn.close()
        print(f"[atlas] seeded {len(_TECHNICIANS)} technicians, {len(_REQUESTS)} requests", flush=True)
    except Exception as exc:
        print(f"[atlas] seed error: {exc}", flush=True)

_seed_db()

# Vercel looks for 'app' or 'handler'
handler = app
