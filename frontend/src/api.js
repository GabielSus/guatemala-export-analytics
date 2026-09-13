const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function request(path) {
  const response = await fetch(`${API_URL}${path}`);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `API error ${response.status}`);
  }
  return response.json();
}

export const analyticsApi = {
  summary: () => request("/analytics/summary"),
  yearly: () => request("/analytics/yearly"),
  growth: () => request("/analytics/growth"),
  years: () => request("/analytics/years"),
  topItems: (year, limit = 10) => request(`/analytics/top-items?year=${year}&limit=${limit}`),
  chapters: (year, limit = 10) => request(`/analytics/chapters?year=${year}&limit=${limit}`),
};
