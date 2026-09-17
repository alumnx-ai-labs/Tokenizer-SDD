import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import BpeTokenizePanel from "./BpeTokenizePanel";

describe("BpeTokenizePanel", () => {
  it("renders a blocked state instructing the user to train first when no model exists", () => {
    render(<BpeTokenizePanel hasTrainedModel={false} loading={false} onSubmit={vi.fn()} />);
    expect(screen.getByText(/train a bpe model first/i)).toBeInTheDocument();
    expect(screen.queryByLabelText("BPE tokenize text")).not.toBeInTheDocument();
  });

  it("renders a text input and Tokenize button when a trained model exists", () => {
    render(<BpeTokenizePanel hasTrainedModel={true} loading={false} onSubmit={vi.fn()} />);
    expect(screen.getByLabelText("BPE tokenize text")).toBeInTheDocument();
    expect(screen.getByText("Tokenize with BPE")).toBeInTheDocument();
  });

  it("calls the parent tokenize handler on submit", () => {
    const onSubmit = vi.fn();
    render(<BpeTokenizePanel hasTrainedModel={true} loading={false} onSubmit={onSubmit} />);
    fireEvent.change(screen.getByLabelText("BPE tokenize text"), { target: { value: "ab" } });
    fireEvent.click(screen.getByText("Tokenize with BPE"));
    expect(onSubmit).toHaveBeenCalledWith("ab");
  });
});
