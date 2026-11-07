"""Pydantic models for account-level data read from the CSV dataset."""

from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class Account(BaseModel):
    account_id: int
    district_id: int
    frequency: str
    account_opened: date


class District(BaseModel):
    district_id: int
    district_name: str
    region: str
    inhabitants: int
    municipalities_under_500: int
    municipalities_500_1999: int
    municipalities_2000_9999: int
    municipalities_over_10000: int
    num_cities: int
    urban_ratio_pct: float
    average_salary: float
    unemployment_rate_2022: Optional[float] = None
    unemployment_rate_2023: float
    entrepreneurs_per_1000: float
    crimes_2022: Optional[int] = None
    crimes_2023: int


class Owner(BaseModel):
    disposition_id: int
    client_id: int
    type: str
    gender: str
    birth_date: date
    district_id: int


class Card(BaseModel):
    card_id: int
    card_type: str
    issued: date


class Loan(BaseModel):
    loan_id: int
    loan_start: date
    amount: float
    duration_months: int
    monthly_payment: float
    status: str
    status_meaning: str
    defaulted: bool


class StandingOrder(BaseModel):
    order_id: int
    to_bank: str
    to_account: str
    amount: float
    purpose: Optional[str] = None


class Transaction(BaseModel):
    transaction_id: int
    date: date
    direction: str
    operation: str
    purpose: Optional[str] = None
    amount: float
    signed_amount: float
    balance: float
    partner_bank: Optional[str] = None
    partner_account: Optional[str] = None


class MonthlySummary(BaseModel):
    account_id: int
    month: str
    money_in: float
    money_out: float
    cash_deposits: float
    transfers_in: float
    pension_in: float
    interest_in: float
    household_bills: float
    insurance: float
    loan_payments: float
    bank_fees: float
    cash_withdrawals_genuine: float
    card_withdrawals: float
    transfers_out_other: float
    month_end_balance: float
    min_balance: float
    avg_daily_balance: float
    days_below_zero: int


class AccountDetail(BaseModel):
    account: Account
    district: Optional[District] = None
    owners: List[Owner]
    cards: List[Card]
    loans: List[Loan]
    standing_orders: List[StandingOrder]
    monthly_summary: List[MonthlySummary]
    transactions: List[Transaction]
    transaction_total: int
