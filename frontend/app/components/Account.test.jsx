import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Account from "./Account";
import { LanguageProvider } from "../lib/LanguageContext";

function renderAccount() {
  return render(
    <LanguageProvider>
      <Account />
    </LanguageProvider>
  );
}

describe("Account", () => {
  it("defaults to Dutch selected", () => {
    renderAccount();
    expect(screen.getByRole("button", { name: "Nederlands" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: "English" })).toHaveAttribute("aria-pressed", "false");
    expect(screen.getByText("Taal")).toBeInTheDocument();
  });

  it("clicking English switches the visible language across the app", () => {
    renderAccount();
    fireEvent.click(screen.getByRole("button", { name: "English" }));
    expect(screen.getByRole("button", { name: "English" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: "Nederlands" })).toHaveAttribute("aria-pressed", "false");
    expect(screen.getByText("Language")).toBeInTheDocument();
  });

  it("switching back to Nederlands restores Dutch", () => {
    renderAccount();
    fireEvent.click(screen.getByRole("button", { name: "English" }));
    fireEvent.click(screen.getByRole("button", { name: "Nederlands" }));
    expect(screen.getByRole("button", { name: "Nederlands" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByText("Taal")).toBeInTheDocument();
  });
});
