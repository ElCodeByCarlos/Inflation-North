from typing import List, Optional

from pydantic import BaseModel


class AccountSummary(BaseModel):
    account_id: int
    district_id: int
    district_name: Optional[str] = None
    frequency: str
    account_opened: str


class Account(BaseModel):
    account_id: int
    district_id: int
    frequency: str
    account_opened: str


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
    unemployment_rate_2023: Optional[float] = None
    entrepreneurs_per_1000: int
    crimes_2022: Optional[int] = None
    crimes_2023: Optional[int] = None


class Card(BaseModel):
    card_id: int
    disposition_id: int
    card_type: str
    issued: str


class Client(BaseModel):
    client_id: int
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    district_id: Optional[int] = None
    district_name: Optional[str] = None
    disposition_id: int
    role: str  # "owner" | "authorized user"
    cards: List[Card]


class Loan(BaseModel):
    loan_id: int
    account_id: int
    loan_start: str
    amount: float
    duration_months: int
    monthly_payment: float
    status: str
    status_meaning: str
    defaulted: int


class StandingOrder(BaseModel):
    order_id: int
    account_id: int
    to_bank: Optional[str] = None
    to_account: Optional[int] = None
    amount: float
    purpose: Optional[str] = None


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


class Transaction(BaseModel):
    transaction_id: int
    account_id: int
    date: str
    direction: str
    operation: Optional[str] = None
    purpose: Optional[str] = None
    amount: float
    signed_amount: float
    balance: float
    partner_bank: Optional[str] = None
    partner_account: Optional[int] = None  # CSV column has blanks, so pandas reads it as float


class TransactionPage(BaseModel):
    account_id: int
    total: int
    offset: int
    limit: int
    items: List[Transaction]


class AccountDetail(BaseModel):
    account: Account
    district: Optional[District] = None
    clients: List[Client]
    loans: List[Loan]
    standing_orders: List[StandingOrder]
    monthly_summary: List[MonthlySummary]
    transactions: TransactionPage
