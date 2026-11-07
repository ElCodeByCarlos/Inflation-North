from fastapi import APIRouter, HTTPException, Query

from app.data.csv_store import get_account_detail
from app.schemas.account import AccountDetail

router = APIRouter(tags=["accounts"])


@router.get("/accounts/{account_id}", response_model=AccountDetail)
def get_account(
    account_id: int,
    limit: int = Query(100, ge=1, le=5000, description="Transactions to return"),
    offset: int = Query(0, ge=0, description="Transaction page offset"),
):
    """Return account metadata plus its owners, cards, loans, standing orders,
    monthly summary, and newest-first transactions."""
    detail = get_account_detail(account_id, limit, offset)
    if detail is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return detail
