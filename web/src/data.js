// Copyright 2026 Xilbi Sistemas de Informacion SL
// SPDX-License-Identifier: Apache-2.0
export const defaults = {
  scenario_id: "solar-home",
  start_date: "2026-06-01",
  days: 7,
  resolution_minutes: 15,
  buildings: 1,
  daily_load_kwh: 12,
  pv_capacity_kw: 4,
  variability: 0.15,
  seed: 42,
};
export const columns = [
  "timestamp",
  "building_id",
  "load_kw",
  "pv_kw",
  "grid_kw",
  "temperature_c",
];

export function estimateRows(config) {
  return ((config.days * 1440) / config.resolution_minutes) * config.buildings;
}

export function csvText(rows) {
  const escape = (value) => `"${String(value).replaceAll('"', '""')}"`;
  return `${columns.join(",")}\n${rows.map((row) => columns.map((k) => escape(row[k])).join(",")).join("\n")}\n`;
}

/** Aggregate building power by timestamp, then sample the chart only; exports stay complete. */
export function chartData(rows, limit = 900) {
  const byTime = new Map();
  for (const r of rows) {
    const point = byTime.get(r.timestamp) || {
      timestamp: r.timestamp,
      load_kw: 0,
      pv_kw: 0,
      grid_kw: 0,
    };
    for (const k of ["load_kw", "pv_kw", "grid_kw"]) point[k] += r[k];
    byTime.set(r.timestamp, point);
  }
  const values = Array.from(byTime.values());
  const step = Math.max(1, Math.ceil(values.length / limit));
  return values.filter((_, i) => i % step === 0 || i === values.length - 1);
}

export function errorMessage(error) {
  if (Array.isArray(error.detail))
    return error.detail
      .map(
        (e) =>
          `${e.loc.filter((x) => x !== "body").join(".") || "Configuration"}: ${e.msg}`,
      )
      .join("; ");
  return typeof error.detail === "string"
    ? error.detail
    : "Generation failed. Check the API service and try again.";
}
