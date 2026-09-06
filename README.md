# Ledger Control — AI Finance Controller

Every order your business processes leaves three separate trails: the store ledger says a sale happened, the payment gateway says money was captured, and the bank says money landed in the account. These three records almost never agree perfectly — dropped webhooks, fee-tier misconfigurations, settlement shortfalls, and orphaned credits quietly pile up, and today most finance teams find them by hand, in spreadsheets, after the money is already gone.

Ledger Control automates that entire loop. It reconciles a batch of orders across all three sources in a single deterministic pass, classifies every mismatch by type and risk level, and surfaces a live dashboard showing exactly where money is stuck and why — down to the individual order. For every high-risk exception, an AI agent drafts a ready-to-send root-cause diagnosis and vendor dispute email, so review time turns into minutes instead of hours.

## Setup
Both options requires Python and Node.js to already be installed on your machine.
OPTION-A(Manual setup)

```bash
cd backend
pip install -r requirements.txt
cp ../.env.example ../.env   # then edit .env with your OWN new Gemini key
uvicorn main:app --reload --port 8000
```
Open http://localhost:8000/docs to try every endpoint interactively.

Option-B —(One-click start)

Just double-click start.bat in the project root. It's fully self-setting-up — no manual pip install or npm install needed, even on a completely fresh clone. It will automatically:

Create the Python virtual environment if it doesn't exist yet
Install all backend dependencies (requirements.txt)
Create .env from .env.example if missing, and open it in Notepad so you can paste in your own Gemini API key (this one step can't be automated — it has to be your own key, not one shipped in the repo)
Install all frontend dependencies (npm install) if node_modules doesn't exist yet
Start the backend and frontend servers, and open the app in your browser

First run only: if .env didn't exist yet, the script will pause after creating it so you can add your key — save the file, close Notepad, then double-click start.bat again to finish setup and launch.

Every run after that: just double-click it — it detects everything is already installed and skips straight to launching both servers and opening your browser at http://localhost:5173.


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
