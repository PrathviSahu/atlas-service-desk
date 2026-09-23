from flask import Blueprint, jsonify, current_app
from ..models.database import get_db

dashboard_bp = Blueprint("dashboard", __name__)


def _db():
    return get_db(current_app.config["DATABASE_PATH"])


@dashboard_bp.route("/dashboard", methods=["GET"])
def get_dashboard():
    conn = _db()

    def count(sql, params=()):
        return conn.execute(sql, params).fetchone()[0]

    total_open = count(
        "SELECT COUNT(*) FROM requests WHERE status NOT IN ('resolved','closed')"
    )
    urgent = count(
        "SELECT COUNT(*) FROM requests WHERE priority = 'urgent' AND status NOT IN ('resolved','closed')"
    )
    unassigned = count(
        "SELECT COUNT(*) FROM requests WHERE technician_id IS NULL AND status NOT IN ('resolved','closed')"
    )
    assigned = count(
        "SELECT COUNT(*) FROM requests WHERE status = 'assigned'"
    )
    waiting = count(
        "SELECT COUNT(*) FROM requests WHERE status = 'waiting'"
    )
    needs_clarification = count(
        "SELECT COUNT(*) FROM requests WHERE needs_clarification = 1 AND status NOT IN ('resolved','closed')"
    )
    duplicates = count(
        "SELECT COUNT(*) FROM requests WHERE is_duplicate = 1"
    )

    # Needs attention: urgent + unassigned, or needs clarification
    attention_rows = conn.execute("""
        SELECT id, customer_id, message, priority, status, technician_id,
               needs_clarification, is_duplicate
        FROM requests
        WHERE (
            (priority = 'urgent' AND status NOT IN ('resolved','closed'))
            OR (needs_clarification = 1 AND status NOT IN ('resolved','closed'))
        )
        ORDER BY
            CASE priority WHEN 'urgent' THEN 0 WHEN 'high' THEN 1 ELSE 2 END,
            received_at ASC
        LIMIT 10
    """).fetchall()

    attention = []
    for row in attention_rows:
        d = dict(row)
        d["is_duplicate"] = bool(d["is_duplicate"])
        d["needs_clarification"] = bool(d["needs_clarification"])
        d["message_snippet"] = d["message"][:80]
        attention.append(d)

    conn.close()

    return jsonify({
        "stats": {
            "total_open": total_open,
            "urgent": urgent,
            "unassigned": unassigned,
            "assigned": assigned,
            "waiting": waiting,
            "needs_clarification": needs_clarification,
            "duplicates": duplicates,
        },
        "needs_attention": attention,
    }), 200
