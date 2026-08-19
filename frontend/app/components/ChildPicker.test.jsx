import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ChildPicker from "./ChildPicker";
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

function renderPicker(props = {}) {
  return render(
    <LanguageProvider>
      <ChildPicker accessToken="t" {...props} />
    </LanguageProvider>
  );
}

describe("ChildPicker", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows the empty state when the parent has no children yet", async () => {
    apiFetch.mockResolvedValue([]);
    renderPicker();
    expect(await screen.findByText(/nog geen kinderen/i)).toBeInTheDocument();
  });

  it("renders a tile per child once loaded", async () => {
    apiFetch.mockResolvedValue([
      { id: 1, nickname: "Sam", parent_id: "p", created_at: "x" },
      { id: 2, nickname: "Robin", parent_id: "p", created_at: "x" },
    ]);
    renderPicker();
    expect(await screen.findByText("Sam")).toBeInTheDocument();
    expect(screen.getByText("Robin")).toBeInTheDocument();
  });

  it("shows a distinct error when loading children fails", async () => {
    apiFetch.mockRejectedValue(new ApiError("Could not load your children"));
    renderPicker();
    expect(await screen.findByText("Could not load your children")).toBeInTheDocument();
    expect(screen.queryByText(/nog geen kinderen/i)).not.toBeInTheDocument();
  });

  it("add-child flow: submitting the form calls apiFetch and returns to the list", async () => {
    apiFetch
      .mockResolvedValueOnce([]) // initial load
      .mockResolvedValueOnce({ id: 1, nickname: "Sam" }) // POST /children
      .mockResolvedValueOnce([{ id: 1, nickname: "Sam", parent_id: "p", created_at: "x" }]); // reload
    renderPicker();
    fireEvent.click(await screen.findByText("+ Kind toevoegen"));
    fireEvent.change(screen.getByPlaceholderText("Bijnaam"), { target: { value: "Sam" } });
    fireEvent.change(screen.getByPlaceholderText("Wachtwoord"), { target: { value: "sesame" } });
    fireEvent.click(screen.getByRole("button", { name: "Kind toevoegen" }));
    await waitFor(() => expect(screen.getByText("Sam")).toBeInTheDocument());
    expect(apiFetch).toHaveBeenCalledWith(
      expect.stringContaining("/children"),
      expect.objectContaining({ method: "POST" })
    );
  });

  it("password gate: wrong password shows an error and stays on the gate, not the whole picker", async () => {
    apiFetch
      .mockResolvedValueOnce([{ id: 1, nickname: "Sam", parent_id: "p", created_at: "x" }])
      .mockRejectedValueOnce(new ApiError("Incorrect child password"));
    renderPicker();
    fireEvent.click(await screen.findByText("Sam"));
    expect(screen.getByText(/sam.*wachtwoord/i)).toBeInTheDocument();
    fireEvent.change(screen.getByPlaceholderText("Wachtwoord"), { target: { value: "wrong" } });
    fireEvent.click(screen.getByRole("button", { name: "Ga" }));
    expect(await screen.findByText("Incorrect child password")).toBeInTheDocument();
    // Still on the gate, not bounced back to the tile list.
    expect(screen.getByRole("button", { name: "Ga" })).toBeInTheDocument();
  });

  it("password gate: correct password calls onChildSelected", async () => {
    const loggedInChild = { id: 1, nickname: "Sam", parent_id: "p", created_at: "x" };
    apiFetch.mockResolvedValueOnce([loggedInChild]).mockResolvedValueOnce(loggedInChild);
    const onChildSelected = vi.fn();
    renderPicker({ onChildSelected });
    fireEvent.click(await screen.findByText("Sam"));
    fireEvent.change(screen.getByPlaceholderText("Wachtwoord"), { target: { value: "sesame" } });
    fireEvent.click(screen.getByRole("button", { name: "Ga" }));
    await waitFor(() => expect(onChildSelected).toHaveBeenCalledWith(loggedInChild));
  });

  it("remove-child flow: confirming calls DELETE and reloads the list without that child", async () => {
    apiFetch
      .mockResolvedValueOnce([{ id: 1, nickname: "Sam", parent_id: "p", created_at: "x" }]) // initial load
      .mockResolvedValueOnce({ deleted: true }) // DELETE /children/1
      .mockResolvedValueOnce([]); // reload
    renderPicker();
    fireEvent.click(await screen.findByLabelText("Sam verwijderen"));
    fireEvent.click(screen.getByRole("button", { name: "Ja, verwijderen" }));
    await waitFor(() => expect(screen.getByText(/nog geen kinderen/i)).toBeInTheDocument());
    expect(apiFetch).toHaveBeenCalledWith(
      expect.stringContaining("/children/1"),
      expect.objectContaining({ method: "DELETE" })
    );
  });

  it("remove-child flow: cancel leaves the child in place untouched", async () => {
    apiFetch.mockResolvedValueOnce([{ id: 1, nickname: "Sam", parent_id: "p", created_at: "x" }]);
    renderPicker();
    fireEvent.click(await screen.findByLabelText("Sam verwijderen"));
    fireEvent.click(screen.getByRole("button", { name: "Annuleren" }));
    expect(screen.getByText("Sam")).toBeInTheDocument();
    expect(apiFetch).toHaveBeenCalledTimes(1); // only the initial load - no DELETE call
  });

  it("remove-child flow: a failed delete shows an error and keeps the child", async () => {
    apiFetch
      .mockResolvedValueOnce([{ id: 1, nickname: "Sam", parent_id: "p", created_at: "x" }])
      .mockRejectedValueOnce(new ApiError("Could not remove this child"));
    renderPicker();
    fireEvent.click(await screen.findByLabelText("Sam verwijderen"));
    fireEvent.click(screen.getByRole("button", { name: "Ja, verwijderen" }));
    expect(await screen.findByText("Could not remove this child")).toBeInTheDocument();
    // Still in the confirm state, not silently reset - the child wasn't removed.
    expect(screen.getByText(/sam verwijderen\?/i)).toBeInTheDocument();
  });
});
