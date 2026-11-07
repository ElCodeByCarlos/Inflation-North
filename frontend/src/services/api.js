const BASE_URL = "/api";

export async function fetchDashboard(mode) {
  const res = await fetch(`${BASE_URL}/dashboard/${mode}`);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
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
