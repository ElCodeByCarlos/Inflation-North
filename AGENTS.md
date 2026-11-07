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

- `backend/app/main.py` mounts the dashboard router at `/api`. Only endpoints: `GET /api/dashboard/{mode}` and `GET /api/health`.
- `backend/app/schemas/dashboard.py` is the source of truth: `Mode = "current" | "plan"` and category keys `income | savings | expenses | investments`.
- Those same keys/modes are duplicated in `frontend/src/constants/categories.js` (`MODES`, `CATEGORY_META`, `FALLBACK_CATEGORIES`) and colored by `--income`/`--savings`/`--expenses`/`--investments` in `frontend/src/styles/global.css`. Adding or renaming a category/mode means updating all three places.
- `backend/app/data/mock_data.py` is hardcoded placeholder data; no real data source is wired yet.

## Gotchas

- Frontend degrades by design: `Dashboard` catches fetch errors and renders zeroed `FALLBACK_CATEGORIES` with a "Backend offline" notice. All-zero cards are not automatically a frontend bug — check the backend first.
- In dev, Vite's `/api` proxy bypasses CORS. Backend CORS allows only `http://localhost:5173`, so open the frontend at `localhost`, not `127.0.0.1`.
- No env files or env vars; nothing to configure.
- Styling: one CSS file per component imported by that component; theme vars and dark mode live in `frontend/src/styles/global.css`.
