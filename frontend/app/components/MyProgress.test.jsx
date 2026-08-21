import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import MyProgress from "./MyProgress";
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

const samKpis = {
  accuracy_trend: [{ date: "2026-08-18", accuracy: 0.5 }],
  practice_frequency_days: 3,
  average_retries: 1.6,
  total_attempts: 12,
  weak_spots_by_topic: [{ topic: "fractions", accuracy: 0.5 }],
};

function renderMyProgress(props = {}) {
  return render(
    <LanguageProvider>
      <MyProgress child={sam} token="child-token" {...props} />
    </LanguageProvider>
  );
}

describe("MyProgress", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("fetches only this child's own kpis - no /children list call, own token as Bearer", async () => {
    apiFetch.mockResolvedValue(samKpis);
    renderMyProgress();
    await screen.findByText("12"); // total_attempts figure, proves the fetch resolved
    expect(apiFetch).toHaveBeenCalledTimes(1);
    expect(apiFetch).toHaveBeenCalledWith(
      expect.stringContaining("/children/1/kpis"),
      expect.objectContaining({ headers: expect.objectContaining({ Authorization: "Bearer child-token" }) })
    );
  });

  it("renders the same progress summary a parent would see for this child", async () => {
    apiFetch.mockResolvedValue(samKpis);
    renderMyProgress();
    expect(await screen.findByText("12")).toBeInTheDocument(); // total_attempts
    expect(screen.getByText("3")).toBeInTheDocument(); // practice_frequency_days
    expect(screen.getByTestId("weakspot-topic")).toHaveTextContent("fractions");
  });

  it("never shows a comparison table - a child must never see siblings' data", async () => {
    apiFetch.mockResolvedValue(samKpis);
    renderMyProgress();
    await screen.findByText("12");
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });

  it("shows an error state instead of crashing when the fetch fails", async () => {
    apiFetch.mockRejectedValue(new ApiError("Could not load progress"));
    renderMyProgress();
    expect(await screen.findByText("Could not load progress")).toBeInTheDocument();
  });
});
