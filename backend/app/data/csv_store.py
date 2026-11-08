"""Read the bundled CSV dataset.

The dataset ships as CSV files next to this module. Small tables are loaded once
and cached; the large transaction and monthly-summary files are scanned lazily
and cached per account so a request does not load the whole file into memory.
"""

import csv
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

DATA_DIR = Path(__file__).resolve().parent


def _rows(filename: str) -> Iterable[Dict[str, str]]:
    path = DATA_DIR / filename
    with path.open(newline="", encoding="utf-8") as handle:
        yield from csv.DictReader(handle)


def _float(value: Optional[str]) -> float:
    return float(value)  # type: ignore[arg-type]


def _opt_str(value: Optional[str]) -> Optional[str]:
    return value or None


def _opt_float(value: Optional[str]) -> Optional[float]:
    return float(value) if value else None


def _opt_int(value: Optional[str]) -> Optional[int]:
    return int(value) if value else None


def _date(value: str) -> date:
    return date.fromisoformat(value)


@lru_cache(maxsize=1)
def accounts() -> Dict[int, Dict[str, Any]]:
    return {
        int(row["account_id"]): {
            "account_id": int(row["account_id"]),
            "district_id": int(row["district_id"]),
            "frequency": row["frequency"],
            "account_opened": _date(row["account_opened"]),
        }
        for row in _rows("accounts.csv")
    }


@lru_cache(maxsize=1)
def districts() -> Dict[int, Dict[str, Any]]:
    return {
        int(row["district_id"]): {
            "district_id": int(row["district_id"]),
            "district_name": row["district_name"],
            "region": row["region"],
            "inhabitants": int(row["inhabitants"]),
            "municipalities_under_500": int(row["municipalities_under_500"]),
            "municipalities_500_1999": int(row["municipalities_500_1999"]),
            "municipalities_2000_9999": int(row["municipalities_2000_9999"]),
            "municipalities_over_10000": int(row["municipalities_over_10000"]),
            "num_cities": int(row["num_cities"]),
            "urban_ratio_pct": _float(row["urban_ratio_pct"]),
            "average_salary": _float(row["average_salary"]),
            "unemployment_rate_2022": _opt_float(row["unemployment_rate_2022"]),
            "unemployment_rate_2023": _float(row["unemployment_rate_2023"]),
            "entrepreneurs_per_1000": _float(row["entrepreneurs_per_1000"]),
            "crimes_2022": _opt_int(row["crimes_2022"]),
            "crimes_2023": int(row["crimes_2023"]),
        }
        for row in _rows("districts.csv")
    }


@lru_cache(maxsize=1)
def clients() -> Dict[int, Dict[str, Any]]:
    return {
        int(row["client_id"]): {
            "client_id": int(row["client_id"]),
            "gender": row["gender"],
            "birth_date": _date(row["birth_date"]),
            "district_id": int(row["district_id"]),
        }
        for row in _rows("clients.csv")
    }


@lru_cache(maxsize=1)
def dispositions_by_account() -> Dict[int, List[Dict[str, Any]]]:
    grouped: Dict[int, List[Dict[str, Any]]] = {}
    for row in _rows("dispositions.csv"):
        grouped.setdefault(int(row["account_id"]), []).append(
            {
                "disposition_id": int(row["disposition_id"]),
                "client_id": int(row["client_id"]),
                "type": row["type"],
            }
        )
    return grouped


@lru_cache(maxsize=1)
def cards_by_disposition() -> Dict[int, List[Dict[str, Any]]]:
    grouped: Dict[int, List[Dict[str, Any]]] = {}
    for row in _rows("cards.csv"):
        grouped.setdefault(int(row["disposition_id"]), []).append(
            {
                "card_id": int(row["card_id"]),
                "card_type": row["card_type"],
                "issued": _date(row["issued"]),
            }
        )
    return grouped


@lru_cache(maxsize=1)
def loans_by_account() -> Dict[int, List[Dict[str, Any]]]:
    grouped: Dict[int, List[Dict[str, Any]]] = {}
    for row in _rows("loans.csv"):
        grouped.setdefault(int(row["account_id"]), []).append(
            {
                "loan_id": int(row["loan_id"]),
                "loan_start": _date(row["loan_start"]),
                "amount": _float(row["amount"]),
                "duration_months": int(row["duration_months"]),
                "monthly_payment": _float(row["monthly_payment"]),
                "status": row["status"],
                "status_meaning": row["status_meaning"],
                "defaulted": row["defaulted"] == "1",
            }
        )
    return grouped


@lru_cache(maxsize=1)
def standing_orders_by_account() -> Dict[int, List[Dict[str, Any]]]:
    grouped: Dict[int, List[Dict[str, Any]]] = {}
    for row in _rows("standing_orders.csv"):
        grouped.setdefault(int(row["account_id"]), []).append(
            {
                "order_id": int(row["order_id"]),
                "to_bank": row["to_bank"],
                "to_account": row["to_account"],
                "amount": _float(row["amount"]),
                "purpose": _opt_str(row["purpose"]),
            }
        )
    return grouped


@lru_cache(maxsize=64)
def transactions_for(account_id: int) -> Tuple[Dict[str, Any], ...]:
    """All transactions for one account, newest first."""
    matches: List[Dict[str, Any]] = []
    for row in _rows("transactions.csv"):
        if int(row["account_id"]) != account_id:
            continue
        matches.append(
            {
                "transaction_id": int(row["transaction_id"]),
                "date": _date(row["date"]),
                "direction": row["direction"],
                "operation": row["operation"],
                "purpose": _opt_str(row["purpose"]),
                "amount": _float(row["amount"]),
                "signed_amount": _float(row["signed_amount"]),
                "balance": _float(row["balance"]),
                "partner_bank": _opt_str(row["partner_bank"]),
                "partner_account": _opt_str(row["partner_account"]),
            }
        )
    matches.sort(key=lambda item: (item["date"], item["transaction_id"]), reverse=True)
    return tuple(matches)


@lru_cache(maxsize=64)
def monthly_summary_for(account_id: int) -> Tuple[Dict[str, Any], ...]:
    matches: List[Dict[str, Any]] = []
    for row in _rows("monthly_summary.csv"):
        if int(row["account_id"]) != account_id:
            continue
        matches.append(
            {
                "account_id": int(row["account_id"]),
                "month": row["month"],
                "money_in": _float(row["money_in"]),
                "money_out": _float(row["money_out"]),
                "cash_deposits": _float(row["cash_deposits"]),
                "transfers_in": _float(row["transfers_in"]),
                "pension_in": _float(row["pension_in"]),
                "interest_in": _float(row["interest_in"]),
                "household_bills": _float(row["household_bills"]),
                "insurance": _float(row["insurance"]),
                "loan_payments": _float(row["loan_payments"]),
                "bank_fees": _float(row["bank_fees"]),
                "cash_withdrawals_genuine": _float(row["cash_withdrawals_genuine"]),
                "card_withdrawals": _float(row["card_withdrawals"]),
                "transfers_out_other": _float(row["transfers_out_other"]),
                "month_end_balance": _float(row["month_end_balance"]),
                "min_balance": _float(row["min_balance"]),
                "avg_daily_balance": _float(row["avg_daily_balance"]),
                "days_below_zero": int(float(row["days_below_zero"])),
            }
        )
    matches.sort(key=lambda item: item["month"])
    return tuple(matches)


def get_account_detail(
    account_id: int, transaction_limit: int, transaction_offset: int
) -> Optional[Dict[str, Any]]:
    """Assemble everything known about one account, or None if it does not exist."""
    account = accounts().get(account_id)
    if account is None:
        return None

    dispositions = dispositions_by_account().get(account_id, [])

    owners: List[Dict[str, Any]] = []
    for disposition in dispositions:
        client = clients().get(disposition["client_id"])
        if client is None:
            continue
        owners.append(
            {
                "disposition_id": disposition["disposition_id"],
                "client_id": client["client_id"],
                "type": disposition["type"],
                "gender": client["gender"],
                "birth_date": client["birth_date"],
                "district_id": client["district_id"],
            }
        )

    cards: List[Dict[str, Any]] = []
    for disposition in dispositions:
        cards.extend(cards_by_disposition().get(disposition["disposition_id"], []))
    cards.sort(key=lambda card: card["card_id"])

    transactions = transactions_for(account_id)
    transaction_page = transactions[
        transaction_offset : transaction_offset + transaction_limit
    ]

    return {
        "account": account,
        "district": districts().get(account["district_id"]),
        "owners": owners,
        "cards": cards,
        "loans": loans_by_account().get(account_id, []),
        "standing_orders": standing_orders_by_account().get(account_id, []),
        "monthly_summary": list(monthly_summary_for(account_id)),
        "transactions": list(transaction_page),
        "transaction_total": len(transactions),
    }
