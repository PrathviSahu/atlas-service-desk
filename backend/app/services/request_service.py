"""
Business logic for service requests.
"""
import sqlite3
from flask import current_app
from ..models.database import get_db
from ..utils.priority import suggest_priority
from ..utils.duplicate import find_duplicate_candidates
from ..utils.clarification import check_missing_info

VALID_STATUSES = {"open", "assigned", "in_progress", "waiting", "resolved", "closed"}
VALID_PRIORITIES = {"urgent", "high", "normal", "low"}
VALID_CHANNELS = {"email", "whatsapp", "phone"}


def _db():
    return get_db(current_app.config["DATABASE_PATH"])


def _row_to_dict(row) -> dict:
    d = dict(row)
    d["is_duplicate"] = bool(d["is_duplicate"])
    d["needs_clarification"] = bool(d["needs_clarification"])
    raw_missing = d.get("missing_information")
    if raw_missing and isinstance(raw_missing, str):
        d["missing_information"] = [m for m in raw_missing.split("|") if m]
    else:
        d["missing_information"] = []
    return d


def get_all_requests(filters: dict = None) -> list[dict]:
    conn = _db()
    query = "SELECT * FROM requests ORDER BY received_at DESC"
    rows = conn.execute(query).fetchall()
    conn.close()
    results = [_row_to_dict(r) for r in rows]

    if filters:
        status_filter = filters.get("status")
        priority_filter = filters.get("priority")
        flag_filter = filters.get("flag")

        if status_filter:
            results = [r for r in results if r["status"] == status_filter]
        if priority_filter:
            results = [r for r in results if r["priority"] == priority_filter]
        if flag_filter == "unassigned":
            results = [r for r in results if not r["technician_id"]]
        elif flag_filter == "needs_clarification":
            results = [r for r in results if r["needs_clarification"]]
        elif flag_filter == "duplicate":
            results = [r for r in results if r["is_duplicate"]]

    return results


def get_request_by_id(request_id: str) -> dict | None:
    conn = _db()
    row = conn.execute("SELECT * FROM requests WHERE id = ?", (request_id,)).fetchone()
    conn.close()
    if not row:
        return None
    return _row_to_dict(row)


def create_request(data: dict) -> dict:
    required = ["id", "customer_id", "channel", "message", "received_at"]
    for field in required:
        if not data.get(field):
            raise ValueError(f"Missing required field: {field}")

    channel = data.get("channel", "").lower()
    if channel not in VALID_CHANNELS:
        raise ValueError(f"Invalid channel. Must be one of: {', '.join(VALID_CHANNELS)}")

    message = data["message"]

    # Auto-apply priority suggestion if not explicitly supplied
    supplied_priority = data.get("priority")
    if supplied_priority and supplied_priority in VALID_PRIORITIES:
        priority = supplied_priority
    else:
        suggestion = suggest_priority(message)
        priority = suggestion["suggested"]

    # Auto-detect missing info
    missing = check_missing_info(message)
    needs_clarification = 1 if missing else 0
    missing_str = "|".join(missing) if missing else None

    conn = _db()
    try:
        conn.execute(
            """
            INSERT INTO requests
              (id, customer_id, channel, message, received_at,
               priority, status, technician_id,
               needs_clarification, missing_information)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["id"],
                data["customer_id"],
                channel,
                message,
                data["received_at"],
                priority,
                data.get("status", "open"),
                data.get("technician_id"),
                needs_clarification,
                missing_str,
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        conn.close()
        raise ValueError(f"Database error: {e}")
    conn.close()
    return get_request_by_id(data["id"])


def update_request(request_id: str, updates: dict) -> dict | None:
    existing = get_request_by_id(request_id)
    if not existing:
        return None

    allowed_fields = {
        "priority", "status", "technician_id", "notes",
        "is_duplicate", "duplicate_of", "needs_clarification",
        "missing_information",
    }
    patch = {k: v for k, v in updates.items() if k in allowed_fields}

    if "status" in patch and patch["status"] not in VALID_STATUSES:
        raise ValueError(f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}")
    if "priority" in patch and patch["priority"] not in VALID_PRIORITIES:
        raise ValueError(f"Invalid priority. Must be one of: {', '.join(VALID_PRIORITIES)}")

    # Coerce booleans to int for SQLite
    if "is_duplicate" in patch:
        patch["is_duplicate"] = 1 if patch["is_duplicate"] else 0
    if "needs_clarification" in patch:
        patch["needs_clarification"] = 1 if patch["needs_clarification"] else 0
    if "missing_information" in patch and isinstance(patch["missing_information"], list):
        patch["missing_information"] = "|".join(patch["missing_information"])

    if not patch:
        return existing

    set_clause = ", ".join(f"{k} = ?" for k in patch)
    values = list(patch.values()) + [request_id]

    conn = _db()
    conn.execute(
        f"UPDATE requests SET {set_clause}, updated_at = datetime('now') WHERE id = ?",
        values,
    )
    conn.commit()
    conn.close()
    return get_request_by_id(request_id)


def get_duplicate_candidates(request_id: str) -> list[dict]:
    request = get_request_by_id(request_id)
    if not request:
        return []
    all_reqs = get_all_requests()
    return find_duplicate_candidates(request, all_reqs)


def get_priority_suggestion(message: str) -> dict:
    return suggest_priority(message)
