import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

// First frontend test framework this repo has ever had (previously zero infrastructure,
// see .claude/plans/test-pyramid-design.md) - Vitest chosen for the 3rd MVP auth ticket.
// Pinned to Vitest 2 / Vite 5 rather than the latest Vitest 4 / Vite 8 (oxc-based
// transform by default): 2/5's esbuild-based pipeline handles this setup cleanly, and
// (per the .jsx extension convention below) no custom transform config ends up needed.
//
// New components under test in this ticket use .jsx (not this repo's usual .js for
// components, e.g. StepBox.js) - both Vite's client and SSR/import-analysis transforms
// require it for files containing JSX, confirmed by hitting both directly while wiring
// this up. Existing .js components are untouched; nothing about them needs to change
// since none of them have test coverage yet either.
export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./vitest.setup.js"],
  },
});
