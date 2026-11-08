from typing import Optional

from fastapi import APIRouter, HTTPException

from app.data import store
from app.data.mock_data import MOCK_DASHBOARD
from app.schemas.dashboard import Dashboard, Mode

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/{mode}", response_model=Dashboard)
def get_dashboard(mode: Mode, account_id: Optional[int] = None):
    # "plan" has no real data source yet, so it stays on mock figures.
    if mode == "current" and account_id is not None:
        result = store.dashboard_categories(account_id)
        if result is None:
            raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
        month, categories = result
        return {"mode": mode, "account_id": account_id, "month": month, "categories": categories}
    return {"mode": mode, "account_id": account_id, "categories": MOCK_DASHBOARD[mode]}
