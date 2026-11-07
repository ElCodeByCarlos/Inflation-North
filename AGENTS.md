# AGENTS.md

Two app directories, no monorepo tooling: `backend/` (FastAPI) and `frontend/` (React + Vite). Run and install each separately.

## Commands

Backend — run from `backend/`, not the repo root (imports are `app.*`):

```sh
cd backend
.venv/bin/python run.py        # http://127.0.0.1:8000, docs at /docs
```

- Use the checked-in `backend/.venv` (Python 3.13). System `python3` is a newer version without the deps installed.
- Recreate env/deps: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
- README's `py` / `.venv\Scripts\activate` steps are Windows-only; use `source .venv/bin/activate` or the interpreter path above.

Frontend — run from `frontend/`:

```sh
npm run dev      # :5173, proxies /api -> http://127.0.0.1:8000
npm run build    # only verification step available
```

There is no test runner, linter, or typechecker configured. Do not invent `npm test`/`npm run lint` commands.

## Data contract

- `backend/app/main.py` mounts two routers at `/api`: `GET /api/dashboard/{mode}`, `GET /api/accounts/{account_id}`, plus `GET /api/health`.
- Dashboard: `backend/app/schemas/dashboard.py` defines `Mode = "current" | "plan"` and category keys `income | savings | expenses | investments`. `backend/app/data/mock_data.py` is still hardcoded placeholder data for these cards.
- Account: `backend/app/schemas/account.py` defines the response. `backend/app/data/csv_store.py` reads the CSVs in `backend/app/data/` and returns `account`, `district`, `owners`, `cards`, `loans`, `standing_orders`, `monthly_summary`, and newest-first `transactions`. `limit`/`offset` page only transactions; `transaction_total` is the unpaged count. Unknown IDs return 404.
- The CSV store uses the stdlib `csv` module (no pandas). Small tables load once via `lru_cache`; the large `transactions.csv` (100 MB) and `monthly_summary.csv` are scanned lazily and cached per account. Avoid loading them fully into memory.
- CSV parsing quirks to preserve: `days_below_zero` contains values like `0.0` (parse as float then int); district 69 has empty unemployment/crime fields (optional); `loans.csv` quotes `status_meaning` values containing commas.
- Dashboard category keys/modes are duplicated in `frontend/src/constants/categories.js` (`MODES`, `CATEGORY_META`, `FALLBACK_CATEGORIES`) and colored by `--income`/`--savings`/`--expenses`/`--investments` in `frontend/src/styles/global.css`. Adding or renaming a category/mode means updating all three places.

## Gotchas

- Frontend degrades by design: `Dashboard` catches fetch errors and renders zeroed `FALLBACK_CATEGORIES` with a "Backend offline" notice. All-zero cards are not automatically a frontend bug — check the backend first.
- In dev, Vite's `/api` proxy bypasses CORS. Backend CORS allows only `http://localhost:5173`, so open the frontend at `localhost`, not `127.0.0.1`.
- No env files or env vars; nothing to configure.
- Styling: one CSS file per component imported by that component; theme vars and dark mode live in `frontend/src/styles/global.css`.
