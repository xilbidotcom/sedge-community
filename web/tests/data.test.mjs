// Copyright 2026 Xilbi Sistemas de Informacion SL
// SPDX-License-Identifier: Apache-2.0
import test from "node:test";
import assert from "node:assert/strict";
import {
  chartData,
  csvText,
  defaults,
  estimateRows,
  errorMessage,
} from "../src/data.js";

test("default scope and population estimates", () => {
  assert.equal(estimateRows(defaults), 672);
  assert.equal(estimateRows({ ...defaults, buildings: 3 }), 2016);
});
test("chart sums buildings but CSV retains them", () => {
  const rows = [1, 2].map((n) => ({
    timestamp: "2026-06-01T00:00:00+00:00",
    building_id: `building-${n}`,
    load_kw: n,
    pv_kw: 0,
    grid_kw: n,
    temperature_c: 15,
  }));
  assert.equal(chartData(rows)[0].load_kw, 3);
  assert.equal(chartData(rows).length, 1);
  assert.equal(csvText(rows).trim().split("\n").length, 3);
  assert.equal(rows.length, 2);
});
test("validation errors preserve the exact field", () => {
  assert.match(
    errorMessage({
      detail: [{ loc: ["body", "days"], msg: "Must be at most 31" }],
    }),
    /days: Must be at most 31/,
  );
});
