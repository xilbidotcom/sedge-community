// Copyright 2026 Xilbi Sistemas de Informacion SL
// SPDX-License-Identifier: Apache-2.0
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { fundingDisclaimer } from "../src/legal.js";

test("full funding disclaimer matches canonical public documents", () => {
  for (const name of ["FUNDING.md", "NOTICE", "README.md"]) {
    const text = readFileSync(
      new URL(`../../${name}`, import.meta.url),
      "utf8",
    );
    assert.ok(text.replace(/\s+/g, " ").includes(fundingDisclaimer));
  }
  assert.ok(
    fundingDisclaimer.includes(
      "Neither the European Union nor the granting authority",
    ),
  );
});

test("every application legal link has a bundled offline document", () => {
  const app = readFileSync(new URL("../src/main.jsx", import.meta.url), "utf8");
  for (const match of app.matchAll(/href="\/legal\/([^\"]+)"/g)) {
    assert.ok(
      existsSync(new URL(`../public/legal/${match[1]}`, import.meta.url)),
    );
  }
  assert.equal((app.match(/\{fundingDisclaimer\}/g) || []).length, 2);
});
