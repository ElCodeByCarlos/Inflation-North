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

    def figures(m: dict) -> dict:
        return {
            "income": m["money_in"],
            "expenses": m["money_out"],
            "savings": m["money_in"] - m["money_out"],
            "investments": m["month_end_balance"],
        }

    latest = figures(months[-1])
    previous = figures(months[-2]) if len(months) > 1 else {}
    titles = {"income": "Income", "savings": "Savings", "expenses": "Expenses", "investments": "Balance"}
    categories = [
        {
            "key": key,
            "title": titles[key],
            "amount": round(latest[key], 2),
            "change": _pct_change(latest[key], previous.get(key)),
        }
        for key in ("income", "savings", "expenses", "investments")
    ]
    return months[-1]["month"], categories
