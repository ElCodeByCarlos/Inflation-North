"""In-memory data store backed by the CSV files in this directory.

All reads go through this module so that future write/manipulation logic
(edits, what-if scenarios, persistence) has a single place to live.
Call `load()` once at startup (see `app.main` lifespan).
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent

_loaded = False
_accounts: pd.DataFrame
_districts: dict[int, dict]
_clients: dict[int, dict]
_cards_by_disp: dict[int, list[dict]]
_tables: dict[str, pd.DataFrame] = {}
_indexes: dict[str, dict[int, Any]] = {}

# Per-account tables, with the sort order used when returning rows.
_PER_ACCOUNT = {
    "dispositions": (["type"], [False]),  # "owner" before "authorized user"
    "loans": (["loan_start"], [True]),
    "standing_orders": (["order_id"], [True]),
    "monthly_summary": (["month"], [True]),
    "transactions": (["date", "transaction_id"], [False, False]),  # newest first
}


def _records(df: pd.DataFrame) -> list[dict]:
    """DataFrame -> list of dicts with NaN converted to None (JSON-safe)."""
    if df.empty:
        return []
    return df.astype(object).where(df.notna(), None).to_dict("records")


def load() -> None:
    global _loaded, _accounts, _districts, _clients, _cards_by_disp
    if _loaded:
        return
    start = time.perf_counter()

    _accounts = pd.read_csv(DATA_DIR / "accounts.csv").sort_values("account_id")
    _districts = {r["district_id"]: r for r in _records(pd.read_csv(DATA_DIR / "districts.csv"))}
    _clients = {r["client_id"]: r for r in _records(pd.read_csv(DATA_DIR / "clients.csv"))}

    _cards_by_disp = {}
    for card in _records(pd.read_csv(DATA_DIR / "cards.csv")):
        _cards_by_disp.setdefault(card["disposition_id"], []).append(card)

    for name, (sort_cols, ascending) in _PER_ACCOUNT.items():
        df = pd.read_csv(DATA_DIR / f"{name}.csv")
        df = df.sort_values(["account_id", *sort_cols], ascending=[True, *ascending], kind="stable")
        df = df.reset_index(drop=True)
        _tables[name] = df
        _indexes[name] = df.groupby("account_id", sort=False).indices

    _loaded = True
    print(f"[store] loaded CSV data in {time.perf_counter() - start:.1f}s")


def _rows(name: str, account_id: int, start: int = 0, stop: int | None = None) -> list[dict]:
    positions = _indexes[name].get(account_id)
    if positions is None:
        return []
    return _records(_tables[name].iloc[positions[start:stop]])


def account_exists(account_id: int) -> bool:
    return account_id in _accounts["account_id"].values


def list_accounts() -> list[dict]:
    out = []
    for r in _records(_accounts):
        district = _districts.get(r["district_id"], {})
        out.append({**r, "district_name": district.get("district_name")})
    return out


def get_transactions(account_id: int, limit: int = 50, offset: int = 0) -> dict:
    total = len(_indexes["transactions"].get(account_id, []))
    return {
        "account_id": account_id,
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": _rows("transactions", account_id, offset, offset + limit),
    }


def get_monthly(account_id: int) -> list[dict]:
    return _rows("monthly_summary", account_id)


def get_account_detail(account_id: int, tx_limit: int = 50) -> dict | None:
    match = _accounts[_accounts["account_id"] == account_id]
    if match.empty:
        return None
    account = _records(match)[0]

    clients = []
    for disp in _rows("dispositions", account_id):
        client = _clients.get(disp["client_id"], {"client_id": disp["client_id"]})
        clients.append(
            {
                **client,
                "district_name": _districts.get(client.get("district_id"), {}).get("district_name"),
                "disposition_id": disp["disposition_id"],
                "role": disp["type"],
                "cards": _cards_by_disp.get(disp["disposition_id"], []),
            }
        )

    return {
        "account": account,
        "district": _districts.get(account["district_id"]),
        "clients": clients,
        "loans": _rows("loans", account_id),
        "standing_orders": _rows("standing_orders", account_id),
        "monthly_summary": get_monthly(account_id),
        "transactions": get_transactions(account_id, limit=tx_limit),
    }


def _pct_change(current: float, previous: float | None) -> float:
    if not previous:
        return 0.0
    return round((current - previous) / abs(previous) * 100, 1)


def dashboard_categories(account_id: int) -> tuple[str | None, list[dict]] | None:
    """Card figures from the account's latest month vs. the month before.

    Returns (month, categories), or None if the account is unknown.
    """
    if not account_exists(account_id):
        return None
    months = get_monthly(account_id)
    if not months:
        return None, []

    latest = _figures(months[-1])
    previous = _figures(months[-2]) if len(months) > 1 else {}
    categories = [
        {
            "key": key,
            "title": _TITLES[key],
            "amount": round(latest[key], 2),
            "change": _pct_change(latest[key], previous.get(key)),
        }
        for key in _CATEGORY_KEYS
    ]
    return months[-1]["month"], categories


_CATEGORY_KEYS = ("income", "savings", "expenses", "investments")
_TITLES = {"income": "Income", "savings": "Savings", "expenses": "Expenses", "investments": "Balance"}


def _figures(m: dict) -> dict:
    return {
        "income": m["money_in"],
        "expenses": m["money_out"],
        "savings": m["money_in"] - m["money_out"],
        "investments": m["month_end_balance"],
    }


# ---------------------------------------------------------------------------
# Plan mode: "what if I lose X?" simulation + recovery plan
# ---------------------------------------------------------------------------

HISTORY_MONTHS = 12  # window used for "typical month" averages
MAX_RECOVERY_MONTHS = 120  # give up after 10 years -> "does not recover"
GREEN_MAX_MONTHS = 3
YELLOW_MAX_MONTHS = 12

# Share of discretionary spending the plan asks the user to cut, per scenario.
_CUT_RATE = {"accident": 0.15, "luxury": 0.30, "no_income": 0.20}
_RUNNING_LOAN = {"C", "D"}  # C = running OK, D = running, client in debt
_INCOME_SOURCES = {
    "cash_deposits": "cash deposits",
    "transfers_in": "incoming transfers",
    "pension_in": "pension payments",
}


def _money(x: float) -> str:
    return f"-${-x:,.0f}" if x < 0 else f"${x:,.0f}"


def _add_months(month: str, n: int) -> str:
    y, m = map(int, month[:7].split("-"))
    total = y * 12 + (m - 1) + n
    return f"{total // 12:04d}-{total % 12 + 1:02d}"


def _months_between(start: str, end: str) -> int:
    y1, m1 = map(int, start[:7].split("-"))
    y2, m2 = map(int, end[:7].split("-"))
    return (y2 * 12 + m2) - (y1 * 12 + m1)


_DISCRETIONARY = ("cash_withdrawals_genuine", "card_withdrawals", "transfers_out_other")
# monthly_summary columns passed to Gemini as the account's recent history.
_HISTORY_FIELDS = (
    "month", "money_in", "money_out", "cash_deposits", "transfers_in", "pension_in",
    "interest_in", "household_bills", "insurance", "loan_payments", "bank_fees",
    *_DISCRETIONARY, "month_end_balance", "days_below_zero",
)


def _avg(history: list[dict], *fields: str) -> float:
    """Average per month of the summed `fields` over `history` rows."""
    if not history:
        return 0.0
    return sum(sum(r.get(f) or 0.0 for f in fields) for r in history) / len(history)


def _running_loans(account_id: int, month: str | None) -> list[dict]:
    """Running loans (status C/D) with their end month and months left after `month`."""
    if month is None:
        return []
    loans = []
    for loan in _rows("loans", account_id):
        if loan["status"] not in _RUNNING_LOAN:
            continue
        end = _add_months(loan["loan_start"], int(loan["duration_months"]))
        ends_in = _months_between(month, end)
        if ends_in > 0:
            loans.append({**loan, "end": end, "ends_in": ends_in})
    return loans


def plan_context(account_id: int) -> dict:
    """Recent history + commitments for an account, for the Gemini planner prompt."""
    months = get_monthly(account_id)
    history = months[-HISTORY_MONTHS:]
    month = months[-1]["month"] if months else None
    avg_in = _avg(history, "money_in")
    avg_out = _avg(history, "money_out")
    r2 = lambda x: round(x, 2)  # noqa: E731
    return {
        "latest_month": month,
        "averages_last_12_months": {
            "money_in": r2(avg_in),
            "money_out": r2(avg_out),
            "surplus": r2(avg_in - avg_out),
            "discretionary_spending": r2(_avg(history, *_DISCRETIONARY)),
            **{f: r2(_avg(history, f)) for f in (
                "cash_deposits", "transfers_in", "pension_in", "household_bills",
                "insurance", "loan_payments",
            )},
        },
        "monthly_history": [
            {f: (r2(r[f]) if isinstance(r[f], float) else r[f]) for f in _HISTORY_FIELDS}
            for r in history
        ],
        "running_loans": [
            {
                "loan_id": l["loan_id"],
                "monthly_payment": l["monthly_payment"],
                "ends": l["end"],
                "status": l["status_meaning"],
            }
            for l in _running_loans(account_id, month)
        ],
        "standing_orders": [
            {"amount": o["amount"], "purpose": o["purpose"] or "unspecified"}
            for o in _rows("standing_orders", account_id)
        ],
    }


def simulate_plan(account_id: int, scenario: str, amount: float) -> dict | None:
    """Apply a one-off loss to the latest month and build a recovery plan.

    Scenarios: "accident" / "luxury" add `amount` to that month's expenses;
    "no_income" removes `amount` from that month's income (capped at the
    income actually received). "Back to normal" means the balance returns to
    its pre-loss level, funded by the typical monthly surplus, a cut in
    discretionary spending, and loan payments that end during the period.

    Returns None if the account is unknown.
    """
    if not account_exists(account_id):
        return None
    months = get_monthly(account_id)
    if not months:
        zero = {k: 0.0 for k in _CATEGORY_KEYS}
        months = [{"month": None, "money_in": 0.0, "money_out": 0.0, "month_end_balance": 0.0}]
        history = []
    else:
        history = months[-HISTORY_MONTHS:]
        zero = None

    latest_row = months[-1]
    month = latest_row["month"]
    current = zero or _figures(latest_row)

    # --- apply the loss to the latest month ---------------------------------
    projected = dict(current)
    if scenario == "no_income":
        loss = min(amount, max(current["income"], 0.0))
        projected["income"] -= loss
    else:
        loss = amount
        projected["expenses"] += loss
    projected["savings"] -= loss
    projected["investments"] -= loss

    categories = [
        {
            "key": k,
            "title": _TITLES[k],
            "current": round(current[k], 2),
            "projected": round(projected[k], 2),
        }
        for k in _CATEGORY_KEYS
    ]

    # --- typical month from history ------------------------------------------
    def avg(*fields: str) -> float:
        return _avg(history, *fields)

    avg_in = avg("money_in")
    avg_out = avg("money_out")
    surplus = avg_in - avg_out
    discretionary = avg(*_DISCRETIONARY)
    cut_rate = _CUT_RATE[scenario]
    cut = discretionary * cut_rate

    loans = _running_loans(account_id, month)

    # --- month-by-month recovery --------------------------------------------
    recovered_in: int | None = 0 if loss <= 0 else None
    remaining = loss
    base = surplus + cut
    for m in range(1, MAX_RECOVERY_MONTHS + 1):
        if remaining <= 0:
            break
        freed = sum(l["monthly_payment"] for l in loans if l["ends_in"] < m)
        remaining -= base + freed
        if remaining <= 0:
            recovered_in = m
    first_month_capacity = base + sum(l["monthly_payment"] for l in loans if l["ends_in"] < 1)

    # --- severity + message ---------------------------------------------------
    pre_balance = current["investments"]
    post_balance = projected["investments"]
    if loss <= 0:
        severity = "green"
        message = "No loss entered yet. Pick a scenario and enter an amount to see its impact."
    elif recovered_in is None:
        severity = "red"
        message = (
            f"Severe impact: at your current pace the balance would not get back to "
            f"{_money(pre_balance)} within {MAX_RECOVERY_MONTHS // 12} years. "
            "This is a major hit to your finances."
        )
    else:
        if recovered_in <= GREEN_MAX_MONTHS:
            severity = "green"
        elif recovered_in <= YELLOW_MAX_MONTHS:
            severity = "yellow"
        else:
            severity = "red"
        # Going overdrawn is never a "good standing" outcome.
        if post_balance < 0 and severity == "green":
            severity = "yellow"
        plural = "month" if recovered_in == 1 else "months"
        message = {
            "green": f"Short recovery: about {recovered_in} {plural}. "
            "Your finances can absorb this loss comfortably.",
            "yellow": f"Moderate impact: about {recovered_in} {plural} to recover. "
            "Manageable, but stick to the plan below.",
            "red": f"Severe impact: about {recovered_in} {plural} to recover. "
            "This is a major hit to your finances.",
        }[severity]

    # --- plan steps -----------------------------------------------------------
    steps: list[str] = []
    if loss > 0:
        if post_balance < 0:
            steps.append(
                f"The loss pushes your balance to {_money(post_balance)}. Cover the overdraft "
                "first to avoid negative-balance fees."
            )
        if scenario == "no_income" and loss < amount:
            steps.append(
                f"Only {_money(loss)} of income was received in {month}, so the loss is capped at that."
            )
        if surplus > 0:
            steps.append(
                f"Keep your usual monthly surplus of {_money(surplus)} in the account "
                f"(12-month average: {_money(avg_in)} in vs {_money(avg_out)} out)."
            )
        else:
            steps.append(
                f"Over the last 12 months you spent {_money(-surplus)} more than you earned per "
                "month on average. The spending cut below has to cover that gap first."
            )
        if discretionary > 0:
            steps.append(
                f"Cut discretionary spending (cash/card withdrawals and other transfers, avg "
                f"{_money(discretionary)}/month) by {cut_rate:.0%}: {_money(cut)} extra per month."
            )
        for l in loans:
            if l["status"] == "D":
                steps.append(
                    f"Loan #{l['loan_id']} is behind on payments. Bring it up to date before "
                    "rebuilding savings."
                )
            if recovered_in is None or l["ends_in"] < recovered_in:
                steps.append(
                    f"Loan #{l['loan_id']} ({_money(l['monthly_payment'])}/month) ends in "
                    f"{l['end']}. Redirect that payment to rebuilding your balance."
                )
            else:
                steps.append(
                    f"Loan #{l['loan_id']} payments of {_money(l['monthly_payment'])}/month "
                    f"continue until {l['end']}."
                )
        orders = _rows("standing_orders", account_id)
        if orders:
            total = sum(o["amount"] for o in orders)
            biggest = max(orders, key=lambda o: o["amount"])
            steps.append(
                f"Review your {len(orders)} standing order{'s' if len(orders) != 1 else ''} "
                f"({_money(total)}/month; largest: {biggest['purpose'] or 'unspecified'}, "
                f"{_money(biggest['amount'])})."
            )
        if scenario == "accident":
            insurance = avg("insurance")
            steps.append(
                f"You pay about {_money(insurance)}/month in insurance. Check whether this "
                "accident is claimable before drawing on savings."
                if insurance > 0
                else "No insurance payments are on record. Consider cover to soften future accidents."
            )
        elif scenario == "luxury":
            steps.append(
                f"Postpone further non-essential purchases until the balance is back to "
                f"{_money(pre_balance)}."
            )
        else:
            field, label = max(_INCOME_SOURCES.items(), key=lambda kv: avg(kv[0]))
            if avg(field) > 0:
                steps.append(
                    f"Most of your income arrives as {label} (avg {_money(avg(field))}/month). "
                    "Confirm when the missing payment will resume."
                )

    return {
        "account_id": account_id,
        "month": month,
        "scenario": scenario,
        "amount": amount,
        "categories": categories,
        "recovery": {
            "severity": severity,
            "months": recovered_in,
            "target_month": _add_months(month, recovered_in) if month and recovered_in else None,
            "monthly_recovery": round(first_month_capacity, 2),
            "message": message,
            "steps": steps,
        },
    }
