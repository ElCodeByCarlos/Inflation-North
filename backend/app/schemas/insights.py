from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.dashboard import Mode


class InsightRequest(BaseModel):
    question: Optional[str] = Field(default=None, max_length=1000)


class InsightResponse(BaseModel):
    mode: Mode
    model: str
    text: str
