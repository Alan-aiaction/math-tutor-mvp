import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import ActiveChildHeader from "./ActiveChildHeader";

describe("ActiveChildHeader", () => {
  it("shows the active child's nickname", () => {
    render(<ActiveChildHeader nickname="Sam" onSwitchChild={() => {}} />);
    expect(screen.getByText(/working as: sam/i)).toBeInTheDocument();
  });

  it("switch child calls onSwitchChild - doesn't touch the parent's session on its own", () => {
    const onSwitchChild = vi.fn();
    render(<ActiveChildHeader nickname="Sam" onSwitchChild={onSwitchChild} />);
    fireEvent.click(screen.getByText("Switch child"));
    expect(onSwitchChild).toHaveBeenCalledTimes(1);
  });
});
