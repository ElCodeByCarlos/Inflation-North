const BASE_URL = "/api";

export async function fetchDashboard(mode) {
  const res = await fetch(`${BASE_URL}/dashboard/${mode}`);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}
