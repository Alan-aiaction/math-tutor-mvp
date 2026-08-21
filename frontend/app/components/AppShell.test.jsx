import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import AppShell from "./AppShell";
import { LanguageProvider } from "../lib/LanguageContext";

const PARENT_NAV_ITEMS = [
  { key: "dashboard", label: "Dashboard" },
  { key: "kinderen", label: "Mijn kinderen" },
];

function renderShell({
  view = "dashboard",
  onNavigate = vi.fn(),
  onSignOut = vi.fn(),
  navItems = PARENT_NAV_ITEMS,
  showAccountLink,
  identityLabel,
} = {}) {
  return render(
    <LanguageProvider>
      <AppShell
        view={view}
        onNavigate={onNavigate}
        onSignOut={onSignOut}
        navItems={navItems}
        showAccountLink={showAccountLink}
        identityLabel={identityLabel}
      >
        <p>content</p>
      </AppShell>
    </LanguageProvider>
  );
}

describe("AppShell", () => {
  it("renders the given nav items, plus Account, by default", () => {
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

  it("renders a narrower, caller-supplied set of nav items - e.g. child mode's Practice/Dashboard only", () => {
    renderShell({
      view: "oefenen",
      navItems: [
        { key: "oefenen", label: "Oefenen" },
        { key: "dashboard", label: "Dashboard" },
      ],
    });
    expect(screen.getByText("Oefenen")).toBeInTheDocument();
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.queryByText("Mijn kinderen")).not.toBeInTheDocument();
  });

  it("hides the Account link when showAccountLink is false - child mode has no account management", () => {
    renderShell({ showAccountLink: false });
    expect(screen.queryByText("Account")).not.toBeInTheDocument();
    // Uitloggen still there regardless - signing out always stays reachable.
    expect(screen.getByText("Uitloggen")).toBeInTheDocument();
  });

  it("shows identityLabel in the topbar when provided", () => {
    renderShell({ identityLabel: "Ian" });
    expect(screen.getByText("Ian")).toBeInTheDocument();
  });

  it("shows no identity pill at all when identityLabel is not provided - unchanged parent chrome", () => {
    const { container } = renderShell();
    // The topbar's identity pill has this exact class combination - absent entirely
    // when there's no identityLabel, not just empty.
    expect(container.querySelector(".rounded-full.border.border-border.bg-surface")).not.toBeInTheDocument();
  });
});
