import json

from fastapi import APIRouter, HTTPException

from app.data import store
from app.schemas.plan import PlanAdviceResponse, PlanRequest, PlanResponse
from app.services import gemini

router = APIRouter(tags=["plan"])

SCENARIO_LABEL = {
    "accident": "an unexpected accident expense",
    "luxury": "a luxury (non-essential) purchase",
    "no_income": "income that was not received",
}

SYSTEM_INSTRUCTION = (
    "You are a concise personal-finance planner embedded in a banking dashboard. "
    "Use only the figures provided; amounts are in $ and monthly unless stated. "
    "The user just took a one-off loss. Write a concrete recovery plan tied to their own "
    "history: spending categories, running loans, deposits/income sources and standing orders. "
    "Goal: get the balance back to its pre-loss level. If the account was already in deficit "
    "before the loss (negative average surplus or negative balance), the goal is instead to "
    "reach a positive monthly surplus and balance, i.e. better numbers than before. "
    "Format: plain text only (no markdown, no asterisks, no headings). First line: a one-sentence "
    "headline with the expected time to recover. Then 3-6 lines, each starting with '- ', "
    "ordered by phase or month, each with a specific $ amount or date. At most ~180 words."
)


def _simulate_or_404(body: PlanRequest) -> dict:
    result = store.simulate_plan(body.account_id, body.scenario, body.amount)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Account {body.account_id} not found")
    return result


@router.post("/plan/simulate", response_model=PlanResponse)
def simulate(body: PlanRequest):
    return _simulate_or_404(body)


@router.post("/plan/advice", response_model=PlanAdviceResponse)
def advice(body: PlanRequest):
    sim = _simulate_or_404(body)
    recovery = sim["recovery"]
    data = {
        "scenario": SCENARIO_LABEL[body.scenario],
        "loss_amount": body.amount,
        "month_of_loss": sim["month"],
        "before_and_after_loss": {
            c["title"]: {"before": c["current"], "after": c["projected"]} for c in sim["categories"]
        },
        "rule_based_estimate": {
            "severity": recovery["severity"],
            "months_to_recover": recovery["months"],
            "monthly_recovery_capacity": recovery["monthly_recovery"],
        },
        "account": store.plan_context(body.account_id),
    }
    prompt = (
        f"Data (JSON): {json.dumps(data)}\n\n"
        "Write the recovery plan for this account."
    )
    try:
        text, model = gemini.generate(prompt, SYSTEM_INSTRUCTION)
    except gemini.GeminiNotConfigured as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:  # upstream/API errors
        raise HTTPException(status_code=502, detail=f"Gemini request failed: {e}")
    return {
        "account_id": body.account_id,
        "scenario": body.scenario,
        "amount": body.amount,
        "model": model,
        "text": text,
    }
