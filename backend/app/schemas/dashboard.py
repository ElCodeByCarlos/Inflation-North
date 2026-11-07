from typing import List, Literal

from pydantic import BaseModel

Mode = Literal["current", "plan"]


class Category(BaseModel):
    key: Literal["income", "savings", "expenses", "investments"]
    title: str
    amount: float
    change: float  # percent vs. previous period


class Dashboard(BaseModel):
    mode: Mode
    categories: List[Category]
