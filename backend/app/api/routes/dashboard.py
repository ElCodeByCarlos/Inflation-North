from fastapi import APIRouter

from app.data.mock_data import MOCK_DASHBOARD
from app.schemas.dashboard import Dashboard, Mode

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/{mode}", response_model=Dashboard)
def get_dashboard(mode: Mode):
    return {"mode": mode, "categories": MOCK_DASHBOARD[mode]}
