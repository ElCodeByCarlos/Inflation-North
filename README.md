# Inflation North — Finance Dashboard

A personal-finance dashboard for exploring retail banking data. The UI pairs four
summary cards (Income, Savings, Expenses, Balance) with an account picker, an
account activity panel, and an AI assistant that answers questions about the
figures. The API serves real data from a bundled CSV dataset; a **Plan** mode is
still backed by placeholder figures.

## Features

- **Current / Plan modes** — `Current` reflects an account's latest month of real
  data; `Plan` shows mock budget figures.
- **Searchable account picker** — filter ~4,500 accounts by ID, district, or
  statement frequency.
- **Summary cards** — income, expenses, savings (money in − money out), and
  investments (shown as **Balance**, using month-end balance). Each card shows the
  percent change versus the previous month.
- **Account details** — owners and authorized users, cards, loans, standing
  orders, a 12-month summary, and a paged transaction table.
- **AI insights** — a Gemini-powered question box (`POST /api/insights/{mode}`)
  that answers using the current dashboard figures.
- **Graceful degradation** — if the backend is unavailable, the frontend renders
  zeroed placeholder cards and an offline notice instead of failing.

## Structure

```
backend/                      Python API (FastAPI)
  run.py                      dev server entry point (uvicorn, reload on :8000)
  .env.example                Gemini configuration template
  app/
    main.py                   app setup, dotenv, CORS, lifespan, router mounting
    api/routes/               dashboard.py, accounts.py, insights.py
    schemas/                  Pydantic response models (dashboard, accounts, insights)
    services/gemini.py        Gemini client with model fallback chain
    data/
      store.py                in-memory pandas store; the only data access path
      csv_store.py            older csv-module reader, no longer wired in
      *.csv                   bundled banking dataset
      mock_data.py            placeholder dashboard figures for Plan mode

frontend/                     React UI (Vite)
  src/
    App.jsx                   loads accounts, holds selected mode + account
    components/
      Taskbar/                brand, account picker, Current/Plan buttons
      AccountPicker/          searchable, keyboard-accessible account selector
      CategoryCard/           summary card with amount and period change
      AccountDetails/         account metadata, tables, paged transactions
      AiInsights/             Gemini question form and answer panel
    pages/Dashboard/          main dashboard layout
    pages/AccountDashboard/   standalone account page (not currently routed)
    viewModels/               AccountDashboard data hook
    services/api.js           fetch wrappers for every endpoint
    constants/categories.js   modes, category metadata, offline fallback data
    styles/global.css         theme tokens, dark mode, app-wide layout
```

## Data

`backend/app/data/` contains the classic PKDD'99 financial/banking dataset plus a
derived monthly rollup:

| File | Contents |
| --- | --- |
| `accounts.csv` | ~4,500 accounts (district, statement frequency, open date) |
| `districts.csv` | 77 districts with population, salary, unemployment, crime stats |
| `clients.csv` | ~5,300 clients (gender, birth date, district) |
| `dispositions.csv` | links clients to accounts as `owner` or `authorized user` |
| `cards.csv` | cards, keyed by `disposition_id` |
| `loans.csv` | loans, status, monthly payment, default flag |
| `standing_orders.csv` | recurring transfers |
| `transactions.csv` | ~1M transactions (~98 MB) |
| `monthly_summary.csv` | ~185k per-account monthly aggregates |

`store.py` loads the CSVs once at startup (FastAPI lifespan), sorts and indexes
them in memory with pandas, and serves every read from there. Joins follow
`accounts.district_id → districts`, `dispositions → clients`, and
`dispositions.disposition_id → cards`; the remaining tables key on `account_id`.

`GET /api/dashboard/{mode}?account_id=X` derives the cards from that account's
latest `monthly_summary` row and compares it with the month before. `plan` mode
and requests without an `account_id` fall back to `mock_data.py`.

## Getting started

### Backend

Requires Python 3.13 and the packages in `backend/requirements.txt`
(FastAPI, uvicorn, pandas, google-genai, python-dotenv). Run from `backend/` so
the `app.*` imports resolve.

```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py                      # http://127.0.0.1:8000, docs at /docs
```

The first boot takes a few seconds while the CSVs are parsed. If a `.venv` is
already checked in, use `.venv/bin/python run.py` instead of recreating it.

### Frontend

```sh
cd frontend
npm install
npm run dev                        # http://localhost:5173
```

Vite proxies `/api` to `http://127.0.0.1:8000`. Open the app at `localhost`
(not `127.0.0.1`) so it matches the backend's CORS allowlist.

Other frontend scripts: `npm run build` (the only verification step) and
`npm run preview`. There is no test runner, linter, or typechecker.

### AI insights configuration

Copy `backend/.env.example` to `backend/.env` and set `GEMINI_API_KEY`. Without
it the rest of the app works; only insight requests fail with `503`.

Optional overrides:

```ini
GEMINI_MODEL=gemini-3.8-flash
GEMINI_FALLBACK_MODELS=gemini-3.5-flash,gemini-3.1-flash-lite
GEMINI_VERTEXAI=false
```

The client tries the primary model first and falls back on 404, 429, or 5xx
responses.

## API

All routes are under `/api`.

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check (`{"status": "ok"}`). |
| `GET` | `/dashboard/{mode}` | Cards for `current` or `plan`. Optional `account_id`; with an account in `current` mode it returns real figures and the source `month`. |
| `GET` | `/accounts` | All accounts with `district_name`. |
| `GET` | `/accounts/{account_id}` | Full account detail: account, district, clients/roles/cards, loans, standing orders, monthly summary, and the first page of transactions. Optional `tx_limit` (default 50, 0–500). |
| `GET` | `/accounts/{account_id}/transactions` | Newest-first transaction page. `limit` (default 50, 1–500) and `offset` (default 0). |
| `POST` | `/insights/{mode}` | Gemini insight for the mode. Body: `{"question": "..."}` (optional, max 1000 chars). Returns `{mode, model, text}`; `503` if unconfigured, `502` on upstream failure. |

## Implementation notes

- The category keys (`income`, `savings`, `expenses`, `investments`) and modes
  (`current`, `plan`) are duplicated in `backend/app/schemas/dashboard.py`,
  `frontend/src/constants/categories.js`, and the CSS color variables in
  `frontend/src/styles/global.css`. Update all three when changing them.
- Styling is hand-rolled: one CSS file per component, theme tokens and dark mode
  in `global.css`. There is no component library or CSS framework.
- `AccountDashboard`, `AccountPageViewModel`, and the `react-router` dependency
  are not wired into the current app; account details are rendered inside the
  main dashboard instead.
