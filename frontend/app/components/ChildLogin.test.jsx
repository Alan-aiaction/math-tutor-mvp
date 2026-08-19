import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ChildLogin from "./ChildLogin";
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

function renderChildLogin(props = {}) {
  return render(
    <LanguageProvider>
      <ChildLogin {...props} />
    </LanguageProvider>
  );
}

const fillAndSubmit = () => {
  fireEvent.change(screen.getByPlaceholderText("Gezinscode"), { target: { value: "AB12CD" } });
  fireEvent.change(screen.getByPlaceholderText("Bijnaam"), { target: { value: "Sam" } });
  fireEvent.change(screen.getByPlaceholderText("Wachtwoord"), { target: { value: "sesame" } });
  fireEvent.click(screen.getByRole("button", { name: "Inloggen" }));
};

describe("ChildLogin", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("posts family code, nickname, and password to /children/login", async () => {
    apiFetch.mockResolvedValue({ child: { id: 1, nickname: "Sam" }, token: "t" });
    renderChildLogin();
    fillAndSubmit();
    expect(apiFetch).toHaveBeenCalledWith(
      expect.stringContaining("/children/login"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ family_code: "AB12CD", nickname: "Sam", password: "sesame" }),
      })
    );
  });

  it("calls onLoggedIn with the child and token on success", async () => {
    const session = { child: { id: 1, nickname: "Sam" }, token: "real-token" };
    apiFetch.mockResolvedValue(session);
    const onLoggedIn = vi.fn();
    renderChildLogin({ onLoggedIn });
    fillAndSubmit();
    await vi.waitFor(() => expect(onLoggedIn).toHaveBeenCalledWith(session));
  });

  it("shows an error message when login fails, does not call onLoggedIn", async () => {
    apiFetch.mockRejectedValue(new ApiError("Onjuiste inloggegevens"));
    const onLoggedIn = vi.fn();
    renderChildLogin({ onLoggedIn });
    fillAndSubmit();
    expect(await screen.findByText("Onjuiste inloggegevens")).toBeInTheDocument();
    expect(onLoggedIn).not.toHaveBeenCalled();
  });

  it("calls onBack when the back link is clicked", () => {
    const onBack = vi.fn();
    renderChildLogin({ onBack });
    fireEvent.click(screen.getByText("Terug"));
    expect(onBack).toHaveBeenCalledTimes(1);
  });
});
