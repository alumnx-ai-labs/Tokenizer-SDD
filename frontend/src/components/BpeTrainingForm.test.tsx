import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import BpeTrainingForm from "./BpeTrainingForm";

describe("BpeTrainingForm", () => {
  it("renders a training-text textarea and a vocabulary-size input", () => {
    render(<BpeTrainingForm loading={false} onSubmit={vi.fn()} />);
    expect(screen.getByLabelText("BPE training text")).toBeInTheDocument();
    expect(screen.getByLabelText("Target vocabulary size")).toBeInTheDocument();
  });

  it("disables the Train button while loading", () => {
    render(<BpeTrainingForm loading={true} onSubmit={vi.fn()} />);
    expect(screen.getByText("Train")).toBeDisabled();
  });

  it("renders a passed-in validation error message", () => {
    render(
      <BpeTrainingForm loading={false} validationError="Text is required." onSubmit={vi.fn()} />
    );
    expect(screen.getByRole("alert")).toHaveTextContent("Text is required.");
  });

  it("calls onSubmit with the entered training text and vocab size", () => {
    const onSubmit = vi.fn();
    render(<BpeTrainingForm loading={false} onSubmit={onSubmit} />);
    fireEvent.change(screen.getByLabelText("BPE training text"), {
      target: { value: "ab ab ab" },
    });
    fireEvent.change(screen.getByLabelText("Target vocabulary size"), {
      target: { value: "10" },
    });
    fireEvent.click(screen.getByText("Train"));
    expect(onSubmit).toHaveBeenCalledWith("ab ab ab", 10);
  });
});
