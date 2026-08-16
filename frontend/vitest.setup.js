import { afterEach } from "vitest";
import { cleanup } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";

// RTL's own auto-cleanup relies on detecting a global afterEach (Jest-style globals) -
// this repo's test files import afterEach/etc explicitly from "vitest" rather than
// enabling test.globals, so cleanup is wired up here instead: one registration, applies
// to every test file, not something each one needs to remember.
afterEach(() => {
  cleanup();
});
