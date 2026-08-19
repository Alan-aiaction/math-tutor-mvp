import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import AppShell from "./AppShell";
import { LanguageProvider } from "../lib/LanguageContext";

function renderShell({ activeChild = null, view = "dashboard", onNavigate = vi.fn(), onSignOut = vi.fn() } = {}) {
  return render(
    <LanguageProvider>
      <AppShell activeChild={activeChild} view={view} onNavigate={onNavigate} onSignOut={onSignOut}>
        <p>content</p>
      </AppShell>
    </LanguageProvider>
  );
}

describe("AppShell", () => {
  it("hides Oefenen when there is no active child", () => {
    renderShell({ activeChild: null });
    expect(screen.queryByText("Oefenen")).not.toBeInTheDocument();
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
  });

  it("shows Oefenen once a child is active", () => {
    renderShell({ activeChild: { id: 1, nickname: "Sam" } });
    expect(screen.getByText("Oefenen")).toBeInTheDocument();
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
  });

  it("Mijn kinderen and Account are always shown regardless of active child", () => {
    renderShell({ activeChild: null });
    expect(screen.getByText("Mijn kinderen")).toBeInTheDocument();
    expect(screen.getByText("Account")).toBeInTheDocument();
  });

  it("clicking a nav item calls onNavigate with that view", () => {
    const onNavigate = vi.fn();
    renderShell({ activeChild: { id: 1, nickname: "Sam" }, onNavigate });
    fireEvent.click(screen.getByText("Mijn kinderen"));
    expect(onNavigate).toHaveBeenCalledWith("kinderen");
  });

  it("marks the current view's nav item as the current page", () => {
    renderShell({ activeChild: { id: 1, nickname: "Sam" }, view: "oefenen" });
    expect(screen.getByText("Oefenen").closest("button")).toHaveAttribute("aria-current", "page");
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
