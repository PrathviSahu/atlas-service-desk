# Atlas Service Desk

A lightweight service request intake, triage, and dispatch tool for Atlas Industrial Services.

Built for the Kraxys sprint. Live demo: see deployment URL in submission.

---

## What it does

Atlas receives service requests through email, phone, and WhatsApp. Before this tool, requests were copied manually into a spreadsheet and urgent or duplicate requests were easily missed.

This product replaces that spreadsheet with an operational queue that handles:

- **Intake** — structured request capture with channel tracking
- **Triage** — rule-based priority suggestion, duplicate detection, missing-info flagging
- **Dispatch** — technician assignment with live workload visibility
- **Status tracking** — full workflow from Open → Assigned → In Progress → Waiting → Resolved → Closed

### Key screens

| Screen | Purpose |
|---|---|
| Operations Dashboard | Live stats: open, urgent, unassigned, waiting, needs clarification, duplicates. Needs Attention panel. Technician workload. |
| Request Inbox | Filterable queue of all requests with priority/status/technician/flag columns. 7 filter modes. |
| Request Modal | Full triage view: message, fields, priority suggestion, duplicate candidates, clarification alert, editable status/technician/notes. |

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11 + Flask + SQLite |
| Frontend | React 18 + Vite |
| Styling | Vanilla CSS (no framework) |
| Tests | pytest (28 tests) |

No authentication. No paid APIs. Runs fully locally for development.

---

## Deployment

The production setup uses two services:

```
React Frontend  →  Vercel
Flask Backend   →  Render (Flask + SQLite)
```

The frontend communicates with the backend via `VITE_API_BASE`. For local development, Vite's proxy handles `/api` → `localhost:5001` automatically.

### Deploy the backend (Render)

1. Go to [render.com](https://render.com) → New Web Service → Connect `PrathviSahu/atlas-service-desk`
2. Render will detect `render.yaml` automatically. Settings:
   - **Root directory:** `backend`
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `python run.py`
3. Add environment variables in Render dashboard:
   - `DATABASE_PATH` = `./atlas.db`
   - `FRONTEND_ORIGIN` = `https://<your-vercel-url>.vercel.app`
4. After first deploy, run the seed: `python seed.py` via Render Shell, or it auto-seeds on startup when the DB is empty.

### Deploy the frontend (Vercel)

```bash
cd frontend
vercel --prod --yes
```

Set the environment variable in Vercel dashboard (or CLI):
```bash
vercel env add VITE_API_BASE production
# Enter: https://<your-render-service>.onrender.com/api
```

Then redeploy:
```bash
vercel --prod --yes
```

### CORS

The backend `FRONTEND_ORIGIN` env var must exactly match your Vercel URL. Update it in the Render dashboard if your Vercel URL differs from the default.

---

## Local setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm 9+

### 1. Clone the repository

```bash
git clone <repo-url>
cd atlas-service-desk
```

### 2. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # defaults are fine for local use
```

### 3. Start the backend

```bash
source venv/bin/activate
DATABASE_PATH=./atlas.db python3 run.py
```

Backend runs on **http://localhost:5001**

> **macOS note**: Port 5000 conflicts with AirPlay Receiver — the app defaults to 5001.

### 4. Seed demo data

```bash
DATABASE_PATH=./atlas.db python3 seed.py
```

This loads R101–R108 (8 requests) and T1–T3 (3 technicians). Safe to re-run — it wipes and reseeds.

### 5. Frontend

```bash
cd ../frontend
npm install
npm run dev
```

Frontend runs on **http://localhost:5173**

Open your browser at **http://localhost:5173** — done.

---

## Reset demo data

To return to the clean starting state at any time:

```bash
cd backend
source venv/bin/activate
DATABASE_PATH=./atlas.db python3 seed.py
```

---

## Environment variables

All variables have working defaults. Copy `.env.example` to `.env` in the `backend/` directory if you want to override.

| Variable | Default | Description |
|---|---|---|
| `DATABASE_PATH` | `./atlas.db` | SQLite file path |
| `PORT` | `5001` | Backend port |
| `FLASK_DEBUG` | `0` | Set to `1` to enable Flask debug mode |
| `FRONTEND_ORIGIN` | `http://localhost:5173` | CORS allowed origin |

---

## API reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/requests` | List requests. Filter via query params (see below). |
| POST | `/api/requests` | Create a new request. |
| GET | `/api/requests/<id>` | Get single request by ID. |
| PATCH | `/api/requests/<id>` | Update priority, status, technician, notes, duplicate flags, clarification flags. |
| GET | `/api/requests/<id>/duplicates` | Get duplicate candidates for a request. |
| POST | `/api/priority-suggestion` | Body: `{"message": "..."}`. Returns rule-based priority suggestion. |
| GET | `/api/technicians` | List technicians with current assigned counts. |
| GET | `/api/dashboard` | Summary stats + needs-attention list. |

### Filter parameters for `GET /api/requests`

```
?priority=urgent          # urgent | high | normal | low
?status=waiting           # open | assigned | in_progress | waiting | resolved | closed
?flag=unassigned          # requests with no technician assigned
?flag=needs_clarification # requests missing required information
?flag=duplicate           # requests marked as duplicates
```

### Priority suggestion

`POST /api/priority-suggestion` accepts `{"message": "..."}` and returns:

```json
{
  "suggested": "urgent",
  "reason": "Message contains keywords indicating urgency."
}
```

This is a **deterministic keyword-based heuristic, not AI**. The coordinator can always override. The UI labels it clearly as "Rule-based heuristic, not AI."

---

## Running tests

```bash
cd backend
source venv/bin/activate
python3 -m pytest tests/ -v
```

**28/28 tests pass** covering:

- Request listing, creation, retrieval, update
- Invalid field validation (status, priority, channel)
- 404 on missing resources
- Technician assignment
- Duplicate detection and marking (R104 → R101 direction)
- Remove duplicate status
- Needs-clarification flags (R105, R108) and mark-as-clarified
- Priority suggestion (urgent keywords, today keyword, normal)
- Priority suggestion missing message → 400
- Dashboard statistics
- Status workflow (open → resolved)
- All filter modes (status, priority, flag)
- `/api/technicians/seed` is NOT exposed (returns 404)

---

## Assumptions

These were made explicitly because the brief does not supply skills, capacity, SLAs, or commercial details:

1. **Priority levels**: Urgent / High / Normal / Low — standard ITIL-style tiers.
2. **Status workflow**: Open → Assigned → In Progress → Waiting → Resolved → Closed.
3. **Priority suggestion**: Keyword-based deterministic heuristic. Conservative by design — coordinator can override.
4. **Duplicate detection**: Same customer ID + overlapping keywords in message. Not ML — deterministic.
5. **Missing information**: Flagged when no equipment identifier is detectable in the message.
6. **Demo clock**: Relative timestamps use 09:00 on 1 October 2026 as "now" for the seeded dataset.
7. **No authentication**: Intentionally omitted — single-team internal operational tool at MVP scope.

---

## Deliberately excluded scope

Per the brief: *"Build the smallest convincing solution you believe Atlas would actually pay for."*

- ❌ Real email / WhatsApp / phone channel integrations
- ❌ Authentication and user accounts
- ❌ Customer portal or customer-facing features
- ❌ Technician scheduling / route optimisation
- ❌ SLA timers or automated escalation
- ❌ Billing, invoicing, or payment handling
- ❌ Mobile application
- ❌ AI / LLM calls for any feature
- ❌ Real-time push updates (WebSocket / polling)
- ❌ Kafka, microservices, Kubernetes

---

## Known limitations

1. **No real-time sync** — coordinator must click Refresh to see changes by others.
2. **SQLite** — single-writer; fine for demo, would use PostgreSQL for multi-user production.
3. **No pagination** — inbox table shows all records; acceptable for the demo dataset size.
4. **Keyword heuristic** — conservative; may not catch every edge case in real data.

---

## Demo sequence (3 minutes)

**Before the demo:** run `python3 seed.py` to reset to the clean state.

| Time | What to show | What to say |
|---|---|---|
| 0:00 | Dashboard | "Atlas tracks requests in a spreadsheet today. This replaces that — live triage across all channels." Show 8 open, 3 urgent, 2 needing clarification. |
| 0:30 | Click R101 (Needs Attention panel) | "R101 came in by email — cold-room unit failing, stored goods at risk. The system flagged it urgent because of the stored-goods language." |
| 1:00 | Assign T1, Save | "One click to assign Alex Morgan. Status moves to Assigned. Dashboard updates live." |
| 1:20 | Open R104 | "Same customer, same issue reported the next day. The system surfaces R101 as a possible duplicate." |
| 1:40 | Mark as duplicate of R101 | "One click — R104 is closed and flagged. R101 lives on as the active request." |
| 2:00 | Open R108 | "R108 is also urgent, but missing the equipment identifier. Coordinator is alerted before dispatching." |
| 2:25 | Return to Dashboard | "The operational picture updates in real time — who has what, what's stuck, what needs a call back." |
| 2:50 | Summary | "That's the full loop: intake, triage, dispatch. Deliberately minimal — this is what Atlas would actually use." |

---

## AI use disclosure

AI assistance (Antigravity / Gemini) was used during this sprint for:

- Scoping and architectural brainstorming
- Generating initial Flask route and React component structure
- Writing and iterating on test cases
- Debugging edge cases (duplicate detection direction, modal state sync bug)

All product decisions, scope judgments, feature choices, and the final implementation review were made and verified by the developer.
