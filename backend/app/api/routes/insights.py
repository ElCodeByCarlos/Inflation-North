import json

from fastapi import APIRouter, HTTPException

from app.data.mock_data import MOCK_DASHBOARD
from app.schemas.dashboard import Mode
from app.schemas.insights import InsightRequest, InsightResponse
from app.services import gemini

router = APIRouter(tags=["insights"])

SYSTEM_INSTRUCTION = (
    "You are a concise personal-finance assistant embedded in a dashboard. "
    "Base your answer only on the figures provided. Amounts are monthly; 'change' is "
    "percent vs. the previous period. Reply in plain text only (no markdown, no "
    "asterisks or headings), at most ~120 words, with 2-4 short actionable points "
    "each on its own line starting with '- '."
)


@router.post("/insights/{mode}", response_model=InsightResponse)
def get_insights(mode: Mode, body: InsightRequest | None = None):
    data = {"current": MOCK_DASHBOARD["current"], "plan": MOCK_DASHBOARD["plan"]}
    question = (body.question if body else None) or (
        "Summarise how the current figures compare with the plan and what to focus on."
        if mode == "current"
        else "Assess whether this plan is realistic compared with the current figures."
    )
    prompt = (
        f"Dashboard view: {mode}\n"
        f"Data (JSON): {json.dumps(data)}\n\n"
        f"Question: {question}"
    )
    try:
        text, model = gemini.generate(prompt, SYSTEM_INSTRUCTION)
    except gemini.GeminiNotConfigured as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:  # upstream/API errors
        raise HTTPException(status_code=502, detail=f"Gemini request failed: {e}")
    return {"mode": mode, "model": model, "text": text}
