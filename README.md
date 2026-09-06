# Autonomous Finance Controller

Migrated from the original Streamlit `app.py` to FastAPI. Business logic
(reconciliation classification rules, AI prompt/cache behavior) is preserved
from the original `reconcile.py` / `agent.py` / `app.py` — only the delivery
layer changed.

## Setup

```bash
cd backend
pip install -r requirements.txt
cp ../.env.example ../.env   # then edit .env with your OWN new Gemini key
uvicorn main:app --reload --port 8000
```

Open http://localhost:8000/docs to try every endpoint interactively.

## Frontend

React + Vite + Tailwind dashboard (dark FinTech style). Talks to the backend
above over HTTP — run both at once, backend on :8000, frontend dev server on
:5173 (already whitelisted in the backend's CORS config).

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

`frontend/.env` sets `VITE_API_BASE_URL=http://localhost:8000` — change it if
your backend runs elsewhere. For a production build: `npm run build` outputs
static files to `frontend/dist/`, servable by any static host (nginx, Vercel,
etc.) as long as it can reach the FastAPI backend.

Pages: **Dashboard** (KPI cards + priority queue), **Exceptions** (full
searchable/filterable/sortable queue with a detail drawer — generate the AI
diagnosis + dispute email, copy, approve, or regenerate), **Analytics**
(loss-by-issue-type and risk-distribution charts, top-10 table),
**Transactions** (tabbed raw-data explorer over store/gateway/bank/exceptions
CSVs), **Settings** (system health, Gemini key status, AI cache stats + clear
cache).

## SECURITY

The original `agent.py` had a Gemini API key hardcoded in source. That key
must be treated as compromised — rotate it in Google AI Studio. This backend
only ever reads the key from the `GEMINI_API_KEY` environment variable.

## Folder layout

```
finance-controller/
├── backend/          <- FastAPI app (this is what you run)
│   ├── main.py
│   ├── api/           endpoints
│   ├── services/       reconciliation / AI / cache logic
│   ├── models/          pydantic schemas
│   └── requirements.txt
├── frontend/         <- React + Vite + Tailwind dashboard (this is the UI)
│   ├── src/
│   │   ├── api/           axios client for the FastAPI backend
│   │   ├── components/    Sidebar, KPI cards, exception queue/table, detail drawer, etc.
│   │   ├── pages/         Dashboard, Exceptions, Analytics, Transactions, Settings
│   │   └── lib/           formatting helpers (INR currency, issue-type labels)
│   └── .env               VITE_API_BASE_URL
├── data/             <- CSVs + AI ticket cache (backend reads these)
├── legacy/           <- your original scripts, kept for reference/regen
│   ├── app.py               (old Streamlit UI — being replaced)
│   ├── reconcile.py          (still the source of reconciliation_exceptions.csv)
│   ├── generate_data.py      (regenerates synthetic data if needed)
│   └── agent.py               (superseded by services/ai_resolution_service.py — has the leaked key, DO NOT reuse)
├── .env.example
└── README.md
```

## Status

- [x] Stage 1: analyzed existing app
- [x] Stage 2: FastAPI backend (verified against real data, bug found & fixed
      in store/gateway/bank amount joining)
- [x] Stage 3: React frontend — all 5 pages built and wired to the live
      backend (dashboard, exception detail drawer with AI resolve/approve/
      regenerate, analytics charts, transactions explorer, settings)
