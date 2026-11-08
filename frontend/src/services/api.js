const BASE_URL = "/api";

async function getJson(path) {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export function fetchDashboard(mode, accountId) {
  const query = accountId != null ? `?account_id=${accountId}` : "";
  return getJson(`/dashboard/${mode}${query}`);
}

export function fetchAccounts() {
  return getJson("/accounts");
}

export function fetchAccount(accountId) {
  return getJson(`/accounts/${accountId}`);
}

export function fetchTransactions(accountId, { limit = 50, offset = 0 } = {}) {
  return getJson(`/accounts/${accountId}/transactions?limit=${limit}&offset=${offset}`);
}

export async function fetchInsights(mode, question) {
  const res = await fetch(`${BASE_URL}/insights/${mode}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(question ? { question } : {}),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `Request failed: ${res.status}`);
  return data;
}
