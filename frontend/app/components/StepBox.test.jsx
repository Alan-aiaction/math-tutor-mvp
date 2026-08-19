import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import StepBox from "./StepBox";

describe("StepBox", () => {
  it("shows Draw/Edit when incorrect and still the current (last) step", () => {
    render(<StepBox index={0} result={{ valid: false }} isLast={true} />);
    expect(screen.getByText("Draw")).toBeInTheDocument();
    expect(screen.getByText("Edit")).toBeInTheDocument();
  });

  it("hides Draw/Edit when incorrect but a later step already exists", () => {
    render(<StepBox index={0} result={{ valid: false }} isLast={false} />);
    expect(screen.queryByText("Draw")).not.toBeInTheDocument();
    expect(screen.queryByText("Edit")).not.toBeInTheDocument();
  });

  it("hides Draw/Edit when correct, regardless of isLast", () => {
    render(<StepBox index={0} result={{ valid: true }} isLast={false} />);
    expect(screen.queryByText("Draw")).not.toBeInTheDocument();
    expect(screen.queryByText("Edit")).not.toBeInTheDocument();
  });

  it("shows Draw/Edit when unanswered and still the current (last) step", () => {
    render(<StepBox index={0} isLast={true} />);
    expect(screen.getByText("Draw")).toBeInTheDocument();
    expect(screen.getByText("Edit")).toBeInTheDocument();
  });
});
