# Finance Dashboard

UI shell for a personal finance dashboard: four category cards (Income, Savings,
Expenses, Investments) and a taskbar with **Current** / **Plan** buttons.

## Structure

```
backend/                 Python API (FastAPI)
  run.py                 dev server entry point
  app/
    main.py              app setup, CORS, router registration
    api/routes/          HTTP endpoints (dashboard.py)
    schemas/             Pydantic response models
    data/                placeholder data (replace with real sources)
frontend/                React UI (Vite)
  src/
    App.jsx              root layout, holds the Current/Plan mode
    components/          reusable pieces (Taskbar, CategoryCard)
    pages/               page-level views (Dashboard)
    services/            API calls
    constants/           modes, category metadata, fallback data
    styles/              global theme variables
```

## Run

Backend (http://127.0.0.1:8000, docs at `/docs`):

```
cd backend
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
py run.py
```

Frontend (http://localhost:5173):

```
cd frontend
npm install
npm run dev
```

The frontend proxies `/api` to the backend. If the backend isn't running, the
cards still render with zeroed placeholder values.
