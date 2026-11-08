from typing import List

from fastapi import APIRouter, HTTPException, Query

from app.data import store
from app.schemas.accounts import AccountDetail, AccountSummary, TransactionPage

router = APIRouter(tags=["accounts"])


@router.get("/accounts", response_model=List[AccountSummary])
def list_accounts():
    return store.list_accounts()


@router.get("/accounts/{account_id}", response_model=AccountDetail)
def get_account(account_id: int, tx_limit: int = Query(50, ge=0, le=500)):
    detail = store.get_account_detail(account_id, tx_limit=tx_limit)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
    return detail


@router.get("/accounts/{account_id}/transactions", response_model=TransactionPage)
def get_transactions(
    account_id: int,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    if not store.account_exists(account_id):
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
    return store.get_transactions(account_id, limit=limit, offset=offset)
