export function formatUsd(value) {
  const numeric = Number(value || 0);
  const absolute = Math.abs(numeric);

  if (absolute >= 1_000_000_000) {
    return `USD ${(numeric / 1_000_000_000).toFixed(2)}B`;
  }
  if (absolute >= 1_000_000) {
    return `USD ${(numeric / 1_000_000).toFixed(1)}M`;
  }
  if (absolute >= 1_000) {
    return `USD ${(numeric / 1_000).toFixed(1)}K`;
  }
  return `USD ${numeric.toFixed(0)}`;
}

export function formatUsdFull(value) {
  return new Intl.NumberFormat("es-GT", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value || 0);
}

export function formatNumber(value) {
  return new Intl.NumberFormat("es-GT").format(value || 0);
}

export function formatPct(value) {
  if (value === null || value === undefined) return "—";
  const prefix = value > 0 ? "+" : "";
  return `${prefix}${Number(value).toFixed(2)}%`;
}
