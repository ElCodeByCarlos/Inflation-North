"""Plan-mode scenario: ask Gemini for a financial plan after a hypothetical shock."""
import json

from fastapi import APIRouter, HTTPException

from app.data import store
from app.data.mock_data import MOCK_DASHBOARD
from app.schemas.scenario import ScenarioPlanResponse, ScenarioRequest
from app.services import gemini

router = APIRouter(tags=["scenario"])

HISTORY_MONTHS = 6

SCENARIO_DESCRIPTIONS = {
    "accident": "an unexpected accident costing a one-off {amount:.2f}",
    "no_income": "losing {amount:.2f} of monthly income (e.g. job loss)",
    "purchase": "a planned one-off purchase of {amount:.2f}",
}

SYSTEM_INSTRUCTION = (
    "You are a practical personal-finance planner embedded in a banking dashboard. "
    "Use only the figures provided; amounts are in USD and monthly unless stated. "
    "If the situation is IN DEBT, give a step-by-step plan to get out of debt "
    "(prioritise overdue loan payments, cut the largest spending categories shown, "
    "estimate how many months it takes). Otherwise give a step-by-step plan to get the "
    "balance and monthly savings back to their normal (pre-scenario) level, with a "
    "realistic monthly target and an estimated number of months. "
    "Reply in plain text only (no markdown, asterisks or headings), at most ~180 words: "
    "one short summary sentence, then 3-5 numbered steps each on its own line."
)


def _account_context(account_id: int) -> dict:
    months = store.get_monthly(account_id)[-HISTORY_MONTHS:]
    loans = store.get_loans(account_id)
    if not months:
        raise HTTPException(status_code=404, detail=f"No monthly data for account {account_id}")
    latest = months[-1]
    return {
        "balance": latest["month_end_balance"],
        "avg_income": sum(m["money_in"] for m in months) / len(months),
        "avg_spending": sum(m["money_out"] for m in months) / len(months),
        "days_below_zero_last_month": latest["days_below_zero"],
        "loans_in_debt": [
            l for l in loans if l.get("defaulted") or l.get("status") == "D"
        ],
        "data": {"recent_months": months, "loans": loans},
    }


def _mock_context() -> dict:
    figures = {c["key"]: c["amount"] for c in MOCK_DASHBOARD["current"]}
    return {
        "balance": figures["savings"],
        "avg_income": figures["income"],
        "avg_spending": figures["expenses"],
        "days_below_zero_last_month": 0,
        "loans_in_debt": [],
        "data": {"current_figures": MOCK_DASHBOARD["current"]},
    }


@router.post("/scenario/plan", response_model=ScenarioPlanResponse)
def scenario_plan(body: ScenarioRequest):
    if body.account_id is not None:
        if not store.account_exists(body.account_id):
            raise HTTPException(status_code=404, detail=f"Account {body.account_id} not found")
        ctx = _account_context(body.account_id)
    else:
        ctx = _mock_context()

    if body.type == "no_income":
        new_income = max(ctx["avg_income"] - body.amount, 0)
        balance_after = ctx["balance"]
        monthly_net_after = new_income - ctx["avg_spending"]
    else:
        balance_after = ctx["balance"] - body.amount
        monthly_net_after = ctx["avg_income"] - ctx["avg_spending"]

    in_debt = (
        balance_after < 0
        or bool(ctx["loans_in_debt"])
        or ctx["days_below_zero_last_month"] > 0
    )

    situation = {
        "scenario": SCENARIO_DESCRIPTIONS[body.type].format(amount=body.amount),
        "status": "IN DEBT" if in_debt else "NOT IN DEBT",
        "balance_before": round(ctx["balance"], 2),
        "balance_after_scenario": round(balance_after, 2),
        "avg_monthly_income": round(ctx["avg_income"], 2),
        "avg_monthly_spending": round(ctx["avg_spending"], 2),
        "monthly_net_after_scenario": round(monthly_net_after, 2),
        "loans_in_debt": ctx["loans_in_debt"],
    }
    prompt = (
        f"Situation (JSON): {json.dumps(situation, default=str)}\n"
        f"Account history (JSON): {json.dumps(ctx['data'], default=str)}\n\n"
        "Create the financial plan."
    )
    try:
        text, model = gemini.generate(prompt, SYSTEM_INSTRUCTION)
    except gemini.GeminiNotConfigured as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:  # upstream/API errors
        raise HTTPException(status_code=502, detail=f"Gemini request failed: {e}")
    return {"model": model, "in_debt": in_debt, "text": text}
