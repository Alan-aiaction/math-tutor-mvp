import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import AppShell from "./AppShell";
import { LanguageProvider } from "../lib/LanguageContext";

function renderShell({ view = "dashboard", onNavigate = vi.fn(), onSignOut = vi.fn() } = {}) {
  return render(
    <LanguageProvider>
      <AppShell view={view} onNavigate={onNavigate} onSignOut={onSignOut}>
        <p>content</p>
      </AppShell>
    </LanguageProvider>
  );
}

describe("AppShell", () => {
  it("Dashboard, Mijn kinderen, and Account are always shown", () => {
    renderShell();
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Mijn kinderen")).toBeInTheDocument();
    expect(screen.getByText("Account")).toBeInTheDocument();
  });

  it("clicking a nav item calls onNavigate with that view", () => {
    const onNavigate = vi.fn();
    renderShell({ onNavigate });
    fireEvent.click(screen.getByText("Mijn kinderen"));
    expect(onNavigate).toHaveBeenCalledWith("kinderen");
  });

  it("marks the current view's nav item as the current page", () => {
    renderShell({ view: "kinderen" });
    expect(screen.getByText("Mijn kinderen").closest("button")).toHaveAttribute("aria-current", "page");
    expect(screen.getByText("Dashboard").closest("button")).toHaveAttribute("aria-current", "false");
  });

  it("sign-out button calls onSignOut", () => {
    const onSignOut = vi.fn();
    renderShell({ onSignOut });
    fireEvent.click(screen.getByText("Uitloggen"));
    expect(onSignOut).toHaveBeenCalledTimes(1);
  });

  it("renders the passed-in content", () => {
    renderShell();
    expect(screen.getByText("content")).toBeInTheDocument();
  });
});
