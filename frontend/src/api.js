const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function request(path) {
  const response = await fetch(`${API_URL}${path}`);

  if (!response.ok) {
    let message = `Request failed (${response.status})`;

    try {
      const body = await response.json();
      message = body.detail || message;
    } catch {
      // Keep generic error.
    }

    throw new Error(message);
  }

  return response.json();
}

export const analyticsApi = {
  summary: () => request("/analytics/summary"),
  yearly: (startYear, endYear) => {
    const params = new URLSearchParams();
    if (startYear) params.set("start_year", startYear);
    if (endYear) params.set("end_year", endYear);
    const suffix = params.toString() ? `?${params}` : "";
    return request(`/analytics/yearly${suffix}`);
  },
  growth: (startYear, endYear) => {
    const params = new URLSearchParams();
    if (startYear) params.set("start_year", startYear);
    if (endYear) params.set("end_year", endYear);
    const suffix = params.toString() ? `?${params}` : "";
    return request(`/analytics/growth${suffix}`);
  },
  topItems: (year, limit = 10, chapter = null) => {
    const params = new URLSearchParams({
      year,
      limit,
    });
    if (chapter) params.set("chapter", chapter);
    return request(`/analytics/top-items?${params}`);
  },
  chapters: (year, limit = 10) =>
    request(`/analytics/chapters?year=${year}&limit=${limit}`),
  itemDetail: (code) => request(`/analytics/items/${code}`),
  years: () => request("/analytics/years"),
  forecast: (horizon = 3) => request(`/forecast?horizon=${horizon}`),
};
