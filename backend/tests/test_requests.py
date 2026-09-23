"""
Backend tests for Atlas Service Desk — R101-R108 and all API behaviours.
Technicians are seeded via a direct SQLite fixture, NOT via API.
"""
import pytest
import json
import sqlite3
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app


@pytest.fixture
def app(tmp_path):
    db = str(tmp_path / "test.db")
    os.environ["DATABASE_PATH"] = db
    os.environ["FRONTEND_ORIGIN"] = "http://localhost:5173"
    application = create_app()
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    return app.test_client()


def _seed_technicians(db_path):
    """Directly insert T1/T2/T3 into SQLite — no API endpoint required."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    for tid, name in [("T1", "Alex Morgan"), ("T2", "Jordan Lee"), ("T3", "Sam Rivera")]:
        conn.execute(
            "INSERT OR REPLACE INTO technicians (id, name, status) VALUES (?, ?, ?)",
            (tid, name, "available"),
        )
    conn.commit()
    conn.close()


@pytest.fixture
def seeded_client(app, client):
    """Seed technicians via DB fixture, then POST requests via API."""
    _seed_technicians(app.config["DATABASE_PATH"])

    requests = [
        {
            "id": "R101", "customer_id": "C01", "channel": "email",
            "message": "Cold-room unit keeps stopping. Stored goods could be affected.",
            "received_at": "2026-09-30T16:10:00",
        },
        {
            "id": "R102", "customer_id": "C02", "channel": "whatsapp",
            "message": "Can you confirm when someone is coming for yesterday's pump request?",
            "received_at": "2026-10-01T08:20:00",
        },
        {
            "id": "R103", "customer_id": "C03", "channel": "phone",
            "message": "Routine inspection request for next week.",
            "received_at": "2026-09-30T11:00:00",
        },
        {
            "id": "R104", "customer_id": "C01", "channel": "email",
            "message": "Following up on the cold-room fault reported yesterday.",
            "received_at": "2026-10-01T08:25:00",
        },
        {
            "id": "R105", "customer_id": "C04", "channel": "phone",
            "message": "Machine not working. Please call us.",
            "received_at": "2026-10-01T08:30:00",
        },
        {
            "id": "R106", "customer_id": "C05", "channel": "email",
            "message": "We are waiting for the replacement part and an update.",
            "received_at": "2026-09-29T14:00:00",
        },
        {
            "id": "R107", "customer_id": "C06", "channel": "whatsapp",
            "message": "Thanks, the unit is running again.",
            "received_at": "2026-09-30T15:00:00",
        },
        {
            "id": "R108", "customer_id": "C07", "channel": "email",
            "message": "Please send someone today for a pressure warning.",
            "received_at": "2026-10-01T08:40:00",
        },
    ]
    for r in requests:
        rv = client.post("/api/requests", json=r)
        assert rv.status_code == 201, f"Seed failed for {r['id']}: {rv.data}"

    return client


# ================================================================
# Basic CRUD
# ================================================================

def test_list_requests_empty(client):
    rv = client.get("/api/requests")
    assert rv.status_code == 200
    assert json.loads(rv.data) == []


def test_create_and_retrieve_request(client):
    payload = {
        "id": "R001",
        "customer_id": "C01",
        "channel": "email",
        "message": "Cold-room unit keeps stopping. Stored goods could be affected.",
        "received_at": "2026-09-30T16:10:00",
    }
    rv = client.post("/api/requests", json=payload)
    assert rv.status_code == 201
    data = json.loads(rv.data)
    assert data["id"] == "R001"
    assert data["priority"] == "urgent"   # auto-detected from "stored goods" keyword

    rv2 = client.get("/api/requests/R001")
    assert rv2.status_code == 200


def test_get_nonexistent_request(client):
    rv = client.get("/api/requests/RXXX")
    assert rv.status_code == 404


def test_create_request_missing_field(client):
    rv = client.post("/api/requests", json={"id": "R999", "channel": "email"})
    assert rv.status_code == 400


def test_create_request_invalid_channel(client):
    rv = client.post(
        "/api/requests",
        json={"id": "R999", "customer_id": "C01", "channel": "telegram",
              "message": "test", "received_at": "2026-10-01T09:00:00"},
    )
    assert rv.status_code == 400


def test_update_priority(client):
    client.post("/api/requests", json={
        "id": "R200", "customer_id": "C01", "channel": "phone",
        "message": "Routine check", "received_at": "2026-10-01T09:00:00",
    })
    rv = client.patch("/api/requests/R200", json={"priority": "high"})
    assert rv.status_code == 200
    assert json.loads(rv.data)["priority"] == "high"


def test_update_invalid_status(client):
    client.post("/api/requests", json={
        "id": "R201", "customer_id": "C01", "channel": "phone",
        "message": "Test", "received_at": "2026-10-01T09:00:00",
    })
    rv = client.patch("/api/requests/R201", json={"status": "flying"})
    assert rv.status_code == 400


def test_update_invalid_priority(client):
    client.post("/api/requests", json={
        "id": "R202", "customer_id": "C01", "channel": "phone",
        "message": "Test", "received_at": "2026-10-01T09:00:00",
    })
    rv = client.patch("/api/requests/R202", json={"priority": "extremely_mega_urgent"})
    assert rv.status_code == 400


def test_update_nonexistent_request(client):
    rv = client.patch("/api/requests/RXXX", json={"priority": "high"})
    assert rv.status_code == 404


def test_no_seed_endpoint_exposed(client):
    """Confirm that the /api/technicians/seed endpoint is NOT in the production API."""
    rv = client.post("/api/technicians/seed", json={"id": "TX", "name": "Test"})
    assert rv.status_code == 404, "Seed endpoint must not be exposed in production"


# ================================================================
# Technician assignment
# ================================================================

def test_technician_assignment(seeded_client, app):
    _seed_technicians(app.config["DATABASE_PATH"])  # ensure techs exist
    rv = seeded_client.patch("/api/requests/R103", json={
        "technician_id": "T1",
        "status": "assigned",
    })
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data["technician_id"] == "T1"
    assert data["status"] == "assigned"


# ================================================================
# Duplicate detection — R104 → R101
# ================================================================

def test_duplicate_detection_r104(seeded_client):
    rv = seeded_client.get("/api/requests/R104/duplicates")
    assert rv.status_code == 200
    candidates = json.loads(rv.data)
    ids = [c["id"] for c in candidates]
    assert "R101" in ids, f"Expected R101 as duplicate candidate, got: {ids}"


def test_mark_duplicate(seeded_client):
    rv = seeded_client.patch("/api/requests/R104", json={
        "is_duplicate": True,
        "duplicate_of": "R101",
    })
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data["is_duplicate"] is True
    assert data["duplicate_of"] == "R101"


def test_remove_duplicate_status(seeded_client):
    # First mark as duplicate
    seeded_client.patch("/api/requests/R104", json={"is_duplicate": True, "duplicate_of": "R101"})
    # Then remove it
    rv = seeded_client.patch("/api/requests/R104", json={"is_duplicate": False, "duplicate_of": None})
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data["is_duplicate"] is False


# ================================================================
# Missing information / clarification — R105, R108
# ================================================================

def test_needs_clarification_r105(seeded_client):
    rv = seeded_client.get("/api/requests/R105")
    data = json.loads(rv.data)
    assert data["needs_clarification"] is True
    assert len(data["missing_information"]) > 0


def test_needs_clarification_r108(seeded_client):
    rv = seeded_client.get("/api/requests/R108")
    data = json.loads(rv.data)
    assert data["needs_clarification"] is True
    assert len(data["missing_information"]) > 0


def test_mark_clarification_resolved(seeded_client):
    rv = seeded_client.patch("/api/requests/R105", json={
        "needs_clarification": False,
        "missing_information": [],
    })
    assert rv.status_code == 200
    assert json.loads(rv.data)["needs_clarification"] is False


# ================================================================
# Priority suggestion — deterministic, not AI
# ================================================================

def test_priority_suggestion_urgent_stored_goods(client):
    rv = client.post("/api/priority-suggestion", json={
        "message": "Cold-room unit keeps stopping. Stored goods could be affected."
    })
    data = json.loads(rv.data)
    assert data["suggested"] == "urgent"
    assert "reason" in data
    assert "AI" not in data["reason"]  # must not claim AI


def test_priority_suggestion_urgent_today(client):
    rv = client.post("/api/priority-suggestion", json={
        "message": "Please send someone today for a pressure warning."
    })
    data = json.loads(rv.data)
    assert data["suggested"] == "urgent"


def test_priority_suggestion_normal(client):
    rv = client.post("/api/priority-suggestion", json={
        "message": "Can we schedule an inspection for next month?"
    })
    data = json.loads(rv.data)
    assert data["suggested"] == "normal"


def test_priority_suggestion_missing_message(client):
    rv = client.post("/api/priority-suggestion", json={})
    assert rv.status_code == 400


# ================================================================
# Dashboard
# ================================================================

def test_dashboard(seeded_client):
    rv = seeded_client.get("/api/dashboard")
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert "stats" in data
    assert "needs_attention" in data
    stats = data["stats"]
    assert stats["total_open"] >= 1
    assert stats["urgent"] >= 1
    assert stats["needs_clarification"] >= 2  # R105 + R108


# ================================================================
# Technicians
# ================================================================

def test_list_technicians(seeded_client, app):
    _seed_technicians(app.config["DATABASE_PATH"])
    rv = seeded_client.get("/api/technicians")
    assert rv.status_code == 200
    data = json.loads(rv.data)
    ids = [t["id"] for t in data]
    assert "T1" in ids
    assert "T2" in ids
    assert "T3" in ids
    # Each technician row must include assigned_count
    for t in data:
        assert "assigned_count" in t


# ================================================================
# Status workflow
# ================================================================

def test_r107_can_be_resolved(seeded_client):
    """R107 is in_progress but customer says unit is running — must be moveable to resolved."""
    rv = seeded_client.patch("/api/requests/R107", json={"status": "resolved"})
    assert rv.status_code == 200
    assert json.loads(rv.data)["status"] == "resolved"


def test_full_status_workflow(client):
    client.post("/api/requests", json={
        "id": "RWFLOW", "customer_id": "CX", "channel": "phone",
        "message": "Boiler fault", "received_at": "2026-10-01T09:00:00",
    })
    for status in ("assigned", "in_progress", "waiting", "resolved", "closed"):
        rv = client.patch("/api/requests/RWFLOW", json={"status": status})
        assert rv.status_code == 200, f"Failed at status: {status}"
        assert json.loads(rv.data)["status"] == status


# ================================================================
# Filters
# ================================================================

def test_filter_by_status(seeded_client):
    rv = seeded_client.get("/api/requests?status=open")
    data = json.loads(rv.data)
    assert len(data) > 0
    for r in data:
        assert r["status"] == "open"


def test_filter_unassigned(seeded_client):
    rv = seeded_client.get("/api/requests?flag=unassigned")
    data = json.loads(rv.data)
    assert len(data) > 0
    for r in data:
        assert r["technician_id"] is None


def test_filter_needs_clarification(seeded_client):
    rv = seeded_client.get("/api/requests?flag=needs_clarification")
    data = json.loads(rv.data)
    ids = [r["id"] for r in data]
    assert "R105" in ids
    assert "R108" in ids
    for r in data:
        assert r["needs_clarification"] is True
