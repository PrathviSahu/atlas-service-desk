from flask import Blueprint, jsonify, current_app
from ..models.database import get_db

technicians_bp = Blueprint("technicians", __name__)


def _db():
    return get_db(current_app.config["DATABASE_PATH"])


@technicians_bp.route("/technicians", methods=["GET"])
def list_technicians():
    conn = _db()
    rows = conn.execute("SELECT * FROM technicians ORDER BY id").fetchall()
    technicians = []
    for row in rows:
        t = dict(row)
        count_row = conn.execute(
            "SELECT COUNT(*) as cnt FROM requests "
            "WHERE technician_id = ? AND status NOT IN ('resolved','closed')",
            (t["id"],),
        ).fetchone()
        t["assigned_count"] = count_row["cnt"]
        technicians.append(t)
    conn.close()
    return jsonify(technicians), 200
