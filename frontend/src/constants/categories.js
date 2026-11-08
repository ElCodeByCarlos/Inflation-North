export const MODES = {
  CURRENT: "current",
  PLAN: "plan",
};

// Visual metadata per category; figures come from the API.
export const CATEGORY_META = {
  income: { icon: "↗", accent: "var(--income)" },
  savings: { icon: "◎", accent: "var(--savings)" },
  expenses: { icon: "↘", accent: "var(--expenses)" },
  investments: { icon: "▲", accent: "var(--investments)" },
};

// Plan mode "what if" scenarios; values match backend/app/schemas/plan.py `Scenario`.
export const SCENARIOS = [
  { value: "accident", label: "Accident" },
  { value: "luxury", label: "Luxury" },
  { value: "no_income", label: "No income" },
];

// Used when the backend is not running, so the UI still renders.
export const FALLBACK_CATEGORIES = [
  { key: "income", title: "Income", amount: 0, change: 0 },
  { key: "savings", title: "Savings", amount: 0, change: 0 },
  { key: "expenses", title: "Expenses", amount: 0, change: 0 },
  { key: "investments", title: "Investments", amount: 0, change: 0 },
];
