from typing import Literal, Optional

from pydantic import BaseModel, Field

ScenarioType = Literal["accident", "no_income", "purchase"]


class ScenarioRequest(BaseModel):
    type: ScenarioType
    amount: float = Field(gt=0, le=1e9)
    account_id: Optional[int] = None


class ScenarioPlanResponse(BaseModel):
    model: str
    in_debt: bool  # whether the plan targets getting out of debt vs. recovering to normal
    text: str
