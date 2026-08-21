import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ParentAuth from "./ParentAuth";
import { supabase } from "../lib/supabaseClient";
import { LanguageProvider } from "../lib/LanguageContext";

vi.mock("../lib/supabaseClient", () => ({
  supabase: {
    auth: {
      signInWithPassword: vi.fn(),
      signUp: vi.fn(),
    },
  },
}));

function renderAuth(props = {}) {
  return render(
    <LanguageProvider>
      <ParentAuth {...props} />
    </LanguageProvider>
  );
}

const fillAndSubmit = async (email = "parent@example.com", password = "sesame123") => {
  fireEvent.change(screen.getByPlaceholderText("E-mail"), { target: { value: email } });
  fireEvent.change(screen.getByPlaceholderText("Wachtwoord"), { target: { value: password } });
  // Ensures the privacy checkbox is checked regardless of mode's default, matching a
  // realistic form fill - checking an already-checked box (sign-in's default) is a
  // harmless no-op.
  const checkbox = screen.getByRole("checkbox");
  if (!checkbox.checked) fireEvent.click(checkbox);
  // Anchored: "Inloggen"/"Aanmelden" is also a substring of the toggle link's text
  // ("Nieuw hier? Meld je aan" / "Heb je al een account? Log in") - an unanchored match
  // would find both and fail with "multiple elements found."
  fireEvent.click(screen.getByRole("button", { name: /^(inloggen|aanmelden)$/i }));
};

describe("ParentAuth", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("defaults to sign-in mode", () => {
    renderAuth();
    expect(screen.getByRole("heading", { name: "Inloggen" })).toBeInTheDocument();
  });

  it("calls signInWithPassword on submit in sign-in mode", async () => {
    supabase.auth.signInWithPassword.mockResolvedValue({ data: { session: { access_token: "t" } }, error: null });
    renderAuth();
    await fillAndSubmit();
    expect(supabase.auth.signInWithPassword).toHaveBeenCalledWith({
      email: "parent@example.com",
      password: "sesame123",
    });
  });

  it("toggling to sign-up mode calls signUp instead", async () => {
    supabase.auth.signUp.mockResolvedValue({ data: { session: { access_token: "t" } }, error: null });
    renderAuth();
    fireEvent.click(screen.getByText("Nieuw hier? Meld je aan"));
    expect(screen.getByRole("heading", { name: "Account aanmaken" })).toBeInTheDocument();
    await fillAndSubmit();
    expect(supabase.auth.signUp).toHaveBeenCalled();
    expect(supabase.auth.signInWithPassword).not.toHaveBeenCalled();
  });

  it("sign-up passes emailRedirectTo so the confirmation email doesn't link to localhost in production", async () => {
    // Bug #76: signUp() with no options falls back to Supabase's dashboard-configured
    // Site URL, which was left pointing at localhost. window.location.origin adapts to
    // whichever environment sign-up actually happened in (prod, preview, or local dev).
    supabase.auth.signUp.mockResolvedValue({ data: { session: { access_token: "t" } }, error: null });
    renderAuth();
    fireEvent.click(screen.getByText("Nieuw hier? Meld je aan"));
    await fillAndSubmit();
    expect(supabase.auth.signUp).toHaveBeenCalledWith({
      email: "parent@example.com",
      password: "sesame123",
      options: { emailRedirectTo: window.location.origin },
    });
  });

  it("shows an error message when auth fails, doesn't call onAuthenticated", async () => {
    supabase.auth.signInWithPassword.mockResolvedValue({
      data: { session: null },
      error: { message: "Invalid login credentials" },
    });
    const onAuthenticated = vi.fn();
    renderAuth({ onAuthenticated });
    await fillAndSubmit();
    expect(await screen.findByText("Invalid login credentials")).toBeInTheDocument();
    expect(onAuthenticated).not.toHaveBeenCalled();
  });

  it("calls onAuthenticated with the session on success", async () => {
    const session = { access_token: "real-token" };
    supabase.auth.signInWithPassword.mockResolvedValue({ data: { session }, error: null });
    const onAuthenticated = vi.fn();
    renderAuth({ onAuthenticated });
    await fillAndSubmit();
    expect(onAuthenticated).toHaveBeenCalledWith(session);
  });

  it("shows a privacy policy checkbox with a link in both sign-in and sign-up mode", () => {
    renderAuth();
    expect(screen.getByRole("link", { name: "Privacybeleid" })).toHaveAttribute("href", "/privacy");
    fireEvent.click(screen.getByText("Nieuw hier? Meld je aan"));
    expect(screen.getByRole("link", { name: "Privacybeleid" })).toHaveAttribute("href", "/privacy");
  });

  it("privacy checkbox is checked by default in sign-in mode - returning users already agreed", () => {
    renderAuth();
    expect(screen.getByRole("checkbox")).toBeChecked();
  });

  it("privacy checkbox is unchecked by default in sign-up mode - a fresh consent moment", () => {
    renderAuth();
    fireEvent.click(screen.getByText("Nieuw hier? Meld je aan"));
    expect(screen.getByRole("checkbox")).not.toBeChecked();
  });

  it("toggling back to sign-in resets the checkbox to checked, even if it was left unchecked in sign-up", () => {
    renderAuth();
    fireEvent.click(screen.getByText("Nieuw hier? Meld je aan"));
    expect(screen.getByRole("checkbox")).not.toBeChecked();
    fireEvent.click(screen.getByText("Heb je al een account? Log in"));
    expect(screen.getByRole("checkbox")).toBeChecked();
  });

  it("submit button is disabled while the privacy checkbox is unchecked", () => {
    renderAuth();
    fireEvent.click(screen.getByText("Nieuw hier? Meld je aan"));
    expect(screen.getByRole("button", { name: "Aanmelden" })).toBeDisabled();
  });

  it("submit button re-enables once the privacy checkbox is checked", () => {
    renderAuth();
    fireEvent.click(screen.getByText("Nieuw hier? Meld je aan"));
    fireEvent.click(screen.getByRole("checkbox"));
    expect(screen.getByRole("button", { name: "Aanmelden" })).not.toBeDisabled();
  });
});
