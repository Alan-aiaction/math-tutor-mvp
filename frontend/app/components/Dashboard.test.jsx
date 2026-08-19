import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import Dashboard from "./Dashboard";
import { apiFetch, ApiError } from "../lib/apiFetch";
import { LanguageProvider } from "../lib/LanguageContext";

vi.mock("../lib/apiFetch", () => ({
  apiFetch: vi.fn(),
  ApiError: class ApiError extends Error {
    constructor(message, opts = {}) {
      super(message);
      Object.assign(this, opts);
    }
  },
}));

const sam = { id: 1, nickname: "Sam", parent_id: "p", created_at: "x" };
const noor = { id: 2, nickname: "Noor", parent_id: "p", created_at: "x" };

const samKpis = {
  accuracy_trend: [{ date: "2026-08-18", accuracy: 0.5 }],
  practice_frequency_days: 3,
  average_retries: 1.6,
  total_attempts: 12,
  weak_spots_by_topic: [
    { topic: "fractions", accuracy: 0.5 },
    { topic: "percentages", accuracy: 0.9 },
  ],
};

const noorKpis = {
  accuracy_trend: [],
  practice_frequency_days: 5,
  average_retries: 1.1,
  total_attempts: 18,
  weak_spots_by_topic: [],
};

function renderDashboard(props = {}) {
  return render(
    <LanguageProvider>
      <Dashboard accessToken="t" activeChild={sam} {...props} />
    </LanguageProvider>
  );
}

describe("Dashboard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the hero and KPI cards using the active child's real data", async () => {
    apiFetch.mockImplementation((url) => {
      if (url.endsWith("/children")) return Promise.resolve([sam]);
      if (url.endsWith("/children/1/kpis")) return Promise.resolve(samKpis);
      throw new Error(`unexpected fetch: ${url}`);
    });
    renderDashboard();
    expect(await screen.findByText("12")).toBeInTheDocument(); // total_attempts figure
    expect(screen.getByText("3")).toBeInTheDocument(); // practice_frequency_days figure
  });

  it("weak-spot list renders in the order the backend already sorted (weakest first)", async () => {
    apiFetch.mockImplementation((url) => {
      if (url.endsWith("/children")) return Promise.resolve([sam]);
      if (url.endsWith("/children/1/kpis")) return Promise.resolve(samKpis);
      throw new Error(`unexpected fetch: ${url}`);
    });
    renderDashboard();
    const topics = await screen.findAllByTestId("weakspot-topic");
    expect(topics.map((el) => el.textContent)).toEqual(["fractions", "percentages"]);
  });

  it("does not show a comparison table with only one child", async () => {
    apiFetch.mockImplementation((url) => {
      if (url.endsWith("/children")) return Promise.resolve([sam]);
      if (url.endsWith("/children/1/kpis")) return Promise.resolve(samKpis);
      throw new Error(`unexpected fetch: ${url}`);
    });
    renderDashboard();
    await screen.findByText("12");
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });

  it("shows a comparison table row per child when there is more than one", async () => {
    apiFetch.mockImplementation((url) => {
      if (url.endsWith("/children")) return Promise.resolve([sam, noor]);
      if (url.endsWith("/children/1/kpis")) return Promise.resolve(samKpis);
      if (url.endsWith("/children/2/kpis")) return Promise.resolve(noorKpis);
      throw new Error(`unexpected fetch: ${url}`);
    });
    renderDashboard();
    const table = await screen.findByRole("table");
    expect(table).toBeInTheDocument();
    expect(screen.getAllByText("Sam").length).toBeGreaterThan(0);
    expect(screen.getByText("Noor")).toBeInTheDocument();
  });

  it("shows an error state instead of crashing when the fetch fails", async () => {
    apiFetch.mockRejectedValue(new ApiError("Could not load progress"));
    renderDashboard();
    expect(await screen.findByText("Could not load progress")).toBeInTheDocument();
  });
});
