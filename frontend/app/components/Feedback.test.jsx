import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import Feedback from "./Feedback";
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

function renderFeedback(props = {}) {
  return render(
    <LanguageProvider>
      <Feedback role="parent" authToken="test-token" {...props} />
    </LanguageProvider>
  );
}

const rateStars = (n) => {
  fireEvent.click(screen.getByLabelText(`${n} van de 5 sterren`));
};

describe("Feedback", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders 5 star buttons", () => {
    renderFeedback();
    for (let i = 1; i <= 5; i++) {
      expect(screen.getByLabelText(`${i} van de 5 sterren`)).toBeInTheDocument();
    }
  });

  it("clicking a star sets the rating (later stars fill too)", () => {
    renderFeedback();
    rateStars(3);
    expect(screen.getByLabelText("3 van de 5 sterren")).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByLabelText("5 van de 5 sterren")).toHaveAttribute("aria-pressed", "false");
  });

  describe("parent role", () => {
    it("shows a category picker and a required message field", () => {
      renderFeedback({ role: "parent" });
      expect(screen.getByText("Bug")).toBeInTheDocument();
      expect(screen.getByText("Idee")).toBeInTheDocument();
      expect(screen.getByText("Iets anders")).toBeInTheDocument();
      expect(screen.getByPlaceholderText("Wat wil je ons laten weten? Hoe meer details, hoe beter.")).toBeInTheDocument();
    });

    it("submit is disabled until both a rating and a message are given", () => {
      renderFeedback({ role: "parent" });
      const submit = screen.getByRole("button", { name: "Versturen" });
      expect(submit).toBeDisabled();

      rateStars(4);
      expect(submit).toBeDisabled(); // rating alone isn't enough for a parent

      fireEvent.change(screen.getByPlaceholderText("Wat wil je ons laten weten? Hoe meer details, hoe beter."), {
        target: { value: "Great app!" },
      });
      expect(submit).not.toBeDisabled();
    });

    it("posts rating, category, and message to /feedback", async () => {
      apiFetch.mockResolvedValue({ id: 1 });
      renderFeedback({ role: "parent", authToken: "parent-token" });
      rateStars(4);
      fireEvent.click(screen.getByText("Bug"));
      fireEvent.change(screen.getByPlaceholderText("Wat wil je ons laten weten? Hoe meer details, hoe beter."), {
        target: { value: "The check button was slow." },
      });
      fireEvent.click(screen.getByRole("button", { name: "Versturen" }));

      expect(apiFetch).toHaveBeenCalledWith(
        expect.stringContaining("/feedback"),
        expect.objectContaining({
          method: "POST",
          headers: expect.objectContaining({ Authorization: "Bearer parent-token" }),
          body: JSON.stringify({ rating: 4, category: "Bug", message: "The check button was slow." }),
        })
      );
    });
  });

  describe("child role", () => {
    it("shows no category picker, and an optional message field", () => {
      renderFeedback({ role: "child" });
      expect(screen.queryByText("Bug")).not.toBeInTheDocument();
      expect(screen.getByPlaceholderText("Wil je nog iets vertellen? (optioneel)")).toBeInTheDocument();
    });

    it("submit is disabled until a rating is given, but no message is required", () => {
      renderFeedback({ role: "child" });
      const submit = screen.getByRole("button", { name: "Versturen" });
      expect(submit).toBeDisabled();
      rateStars(5);
      expect(submit).not.toBeDisabled();
    });

    it("posts rating with no category and an empty message when none was typed", async () => {
      apiFetch.mockResolvedValue({ id: 2 });
      renderFeedback({ role: "child", authToken: "child-token" });
      rateStars(5);
      fireEvent.click(screen.getByRole("button", { name: "Versturen" }));

      expect(apiFetch).toHaveBeenCalledWith(
        expect.stringContaining("/feedback"),
        expect.objectContaining({
          headers: expect.objectContaining({ Authorization: "Bearer child-token" }),
          body: JSON.stringify({ rating: 5, category: null, message: null }),
        })
      );
    });
  });

  it("shows a thank-you message and resets the form on success", async () => {
    apiFetch.mockResolvedValue({ id: 1 });
    renderFeedback({ role: "child" });
    rateStars(5);
    fireEvent.click(screen.getByRole("button", { name: "Versturen" }));

    expect(await screen.findByText("Bedankt voor je feedback!")).toBeInTheDocument();
    expect(screen.getByLabelText("5 van de 5 sterren")).toHaveAttribute("aria-pressed", "false");
  });

  it("shows an error message on failure, keeps the form filled in", async () => {
    apiFetch.mockRejectedValue(new ApiError("Kon feedback niet versturen. Probeer het opnieuw."));
    renderFeedback({ role: "child" });
    rateStars(5);
    fireEvent.click(screen.getByRole("button", { name: "Versturen" }));

    expect(await screen.findByText("Kon feedback niet versturen. Probeer het opnieuw.")).toBeInTheDocument();
    expect(screen.getByLabelText("5 van de 5 sterren")).toHaveAttribute("aria-pressed", "true");
  });
});
