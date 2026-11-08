from typing import List, Literal, Optional

from pydantic import BaseModel, Field

Scenario = Literal["accident", "luxury", "no_income"]
Severity = Literal["green", "yellow", "red"]


class PlanRequest(BaseModel):
    account_id: int
    scenario: Scenario
    amount: float = Field(ge=0, le=100_000_000)  # size of the loss


class PlanCategory(BaseModel):
    key: Literal["income", "savings", "expenses", "investments"]
    title: str
    current: float  # latest month, as shown in the Current view
    projected: float  # same month with the loss applied


class Recovery(BaseModel):
    severity: Severity
    months: Optional[int] = None  # None = cannot recover at current pace
    target_month: Optional[str] = None  # "YYYY-MM" the balance is expected back
    monthly_recovery: float  # amount set aside per month under the plan
    message: str
    steps: List[str]


class PlanAdviceResponse(BaseModel):
    account_id: int
    scenario: Scenario
    amount: float
    model: str
    text: str


class PlanResponse(BaseModel):
    account_id: int
    month: Optional[str] = None
    scenario: Scenario
    amount: float
    categories: List[PlanCategory]
    recovery: Recovery
