import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import ResetVocabularyButton from "./ResetVocabularyButton";

describe("ResetVocabularyButton", () => {
  it("shows a confirmation step before calling onConfirm", () => {
    const onConfirm = vi.fn();
    vi.spyOn(window, "confirm").mockReturnValue(false);

    render(<ResetVocabularyButton onConfirm={onConfirm} />);
    fireEvent.click(screen.getByText("Reset Vocabulary"));

    expect(window.confirm).toHaveBeenCalled();
    expect(onConfirm).not.toHaveBeenCalled();

    vi.restoreAllMocks();
  });

  it("calls onConfirm when the user confirms", () => {
    const onConfirm = vi.fn();
    vi.spyOn(window, "confirm").mockReturnValue(true);

    render(<ResetVocabularyButton onConfirm={onConfirm} />);
    fireEvent.click(screen.getByText("Reset Vocabulary"));

    expect(onConfirm).toHaveBeenCalledTimes(1);

    vi.restoreAllMocks();
  });
});
