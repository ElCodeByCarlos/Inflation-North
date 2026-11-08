from pathlib import Path

from dotenv import load_dotenv

# Load backend/.env (GEMINI_API_KEY etc.) before anything reads env vars.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from contextlib import asynccontextmanager  # noqa: E402

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from app.api.routes import accounts, dashboard, insights, scenario  # noqa: E402
from app.data import store  # noqa: E402


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Parse the CSVs (incl. ~100 MB transactions.csv) once at boot.
    store.load()
    yield


app = FastAPI(title="Finance Dashboard API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounts.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(insights.router, prefix="/api")
app.include_router(scenario.router, prefix="/api")
app.include_router(accounts.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
