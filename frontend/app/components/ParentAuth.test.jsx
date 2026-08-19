import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ParentAuth from "./ParentAuth";
import { supabase } from "../lib/supabaseClient";

vi.mock("../lib/supabaseClient", () => ({
  supabase: {
    auth: {
      signInWithPassword: vi.fn(),
      signUp: vi.fn(),
    },
  },
}));

const fillAndSubmit = async (email = "parent@example.com", password = "sesame123") => {
  fireEvent.change(screen.getByPlaceholderText("Email"), { target: { value: email } });
  fireEvent.change(screen.getByPlaceholderText("Password"), { target: { value: password } });
  // Anchored: "Sign in"/"Sign up" is also a substring of the toggle link's text
  // ("New here? Sign up" / "Already have an account? Sign in") - an unanchored match
  // would find both and fail with "multiple elements found."
  fireEvent.click(screen.getByRole("button", { name: /^sign (in|up)$/i }));
};

describe("ParentAuth", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("defaults to sign-in mode", () => {
    render(<ParentAuth />);
    expect(screen.getByRole("heading", { name: "Sign in" })).toBeInTheDocument();
  });

  it("calls signInWithPassword on submit in sign-in mode", async () => {
    supabase.auth.signInWithPassword.mockResolvedValue({ data: { session: { access_token: "t" } }, error: null });
    render(<ParentAuth />);
    await fillAndSubmit();
    expect(supabase.auth.signInWithPassword).toHaveBeenCalledWith({
      email: "parent@example.com",
      password: "sesame123",
    });
  });

  it("toggling to sign-up mode calls signUp instead", async () => {
    supabase.auth.signUp.mockResolvedValue({ data: { session: { access_token: "t" } }, error: null });
    render(<ParentAuth />);
    fireEvent.click(screen.getByText("New here? Sign up"));
    expect(screen.getByRole("heading", { name: "Create your account" })).toBeInTheDocument();
    await fillAndSubmit();
    expect(supabase.auth.signUp).toHaveBeenCalled();
    expect(supabase.auth.signInWithPassword).not.toHaveBeenCalled();
  });

  it("sign-up passes emailRedirectTo so the confirmation email doesn't link to localhost in production", async () => {
    // Bug #76: signUp() with no options falls back to Supabase's dashboard-configured
    // Site URL, which was left pointing at localhost. window.location.origin adapts to
    // whichever environment sign-up actually happened in (prod, preview, or local dev).
    supabase.auth.signUp.mockResolvedValue({ data: { session: { access_token: "t" } }, error: null });
    render(<ParentAuth />);
    fireEvent.click(screen.getByText("New here? Sign up"));
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
    render(<ParentAuth onAuthenticated={onAuthenticated} />);
    await fillAndSubmit();
    expect(await screen.findByText("Invalid login credentials")).toBeInTheDocument();
    expect(onAuthenticated).not.toHaveBeenCalled();
  });

  it("calls onAuthenticated with the session on success", async () => {
    const session = { access_token: "real-token" };
    supabase.auth.signInWithPassword.mockResolvedValue({ data: { session }, error: null });
    const onAuthenticated = vi.fn();
    render(<ParentAuth onAuthenticated={onAuthenticated} />);
    await fillAndSubmit();
    expect(onAuthenticated).toHaveBeenCalledWith(session);
  });
});
