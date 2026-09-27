// Copyright 2026 Xilbi Sistemas de Informacion SL
// SPDX-License-Identifier: Apache-2.0
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const proxy = {
  "/api": {
    target: process.env.COMMUNITY_API_TARGET || "http://127.0.0.1:9010",
  },
};
export default defineConfig({
  plugins: [react()],
  server: { proxy },
  preview: { proxy },
});
