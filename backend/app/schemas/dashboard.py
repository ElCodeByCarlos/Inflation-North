from typing import List, Literal, Optional

from pydantic import BaseModel

Mode = Literal["current", "plan"]


class Category(BaseModel):
    key: Literal["income", "savings", "expenses", "investments"]
    title: str
    amount: float
    change: float  # percent vs. previous period


class Dashboard(BaseModel):
    mode: Mode
    account_id: Optional[int] = None
    month: Optional[str] = None  # "YYYY-MM" the figures come from (real data only)
    categories: List[Category]
