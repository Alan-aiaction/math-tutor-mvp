import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import Account from "./Account";
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

function renderAccount(props = {}) {
  return render(
    <LanguageProvider>
      <Account accessToken="t" {...props} />
    </LanguageProvider>
  );
}

describe("Account", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("defaults to Dutch selected", () => {
    apiFetch.mockImplementation(() => new Promise(() => {})); // never resolves - not under test here
    renderAccount();
    expect(screen.getByRole("button", { name: "Nederlands" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: "English" })).toHaveAttribute("aria-pressed", "false");
    expect(screen.getByText("Taal")).toBeInTheDocument();
  });

  it("clicking English switches the visible language across the app", () => {
    apiFetch.mockImplementation(() => new Promise(() => {}));
    renderAccount();
    fireEvent.click(screen.getByRole("button", { name: "English" }));
    expect(screen.getByRole("button", { name: "English" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: "Nederlands" })).toHaveAttribute("aria-pressed", "false");
    expect(screen.getByText("Language")).toBeInTheDocument();
  });

  it("switching back to Nederlands restores Dutch", () => {
    apiFetch.mockImplementation(() => new Promise(() => {}));
    renderAccount();
    fireEvent.click(screen.getByRole("button", { name: "English" }));
    fireEvent.click(screen.getByRole("button", { name: "Nederlands" }));
    expect(screen.getByRole("button", { name: "Nederlands" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByText("Taal")).toBeInTheDocument();
  });

  it("shows the family code and children-used count once loaded", async () => {
    apiFetch.mockResolvedValue({ family_code: "AB12CD", max_children: 3, children_count: 2 });
    renderAccount();
    expect(await screen.findByText("AB12CD")).toBeInTheDocument();
    expect(screen.getByText("2 van 3 kinderen")).toBeInTheDocument();
  });

  it("shows an error state instead of crashing when the family-code fetch fails", async () => {
    apiFetch.mockRejectedValue(new ApiError("Kon de gezinscode niet laden"));
    renderAccount();
    expect(await screen.findByText("Kon de gezinscode niet laden")).toBeInTheDocument();
  });

  it("copying the family code shows a brief confirmation", async () => {
    apiFetch.mockResolvedValue({ family_code: "AB12CD", max_children: 3, children_count: 2 });
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.assign(navigator, { clipboard: { writeText } });
    renderAccount();
    const copyButton = await screen.findByRole("button", { name: "Kopiëren" });
    fireEvent.click(copyButton);
    expect(writeText).toHaveBeenCalledWith("AB12CD");
    expect(await screen.findByRole("button", { name: "Gekopieerd!" })).toBeInTheDocument();
  });

  it("links to the privacy policy", () => {
    apiFetch.mockImplementation(() => new Promise(() => {}));
    renderAccount();
    expect(screen.getByRole("link", { name: "Privacybeleid" })).toHaveAttribute("href", "/privacy");
  });
});
