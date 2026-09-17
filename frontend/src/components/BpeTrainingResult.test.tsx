import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import BpeTrainingResult from "./BpeTrainingResult";

describe("BpeTrainingResult", () => {
  it("renders an empty state when no training result exists", () => {
    render(<BpeTrainingResult result={null} />);
    expect(screen.getByText(/no bpe model has been trained yet/i)).toBeInTheDocument();
  });

  it("renders the vocabulary and training log for a result, without a merge rules section", () => {
    render(
      <BpeTrainingResult
        result={{
          vocabulary: [
            { token_id: 0, token_text: "a" },
            { token_id: 1, token_text: "b" },
            { token_id: 2, token_text: "ab" },
          ],
          merge_rules: [{ step: 1, pair: ["a", "b"], merged_token_text: "ab" }],
          training_log: [{ step: 1, pair: ["a", "b"], frequency: 3, merged_token_text: "ab" }],
          vocabulary_size: 3,
        }}
      />
    );
    expect(screen.getByText("Vocabulary (3)")).toBeInTheDocument();
    expect(screen.queryByText("Merge Rules")).not.toBeInTheDocument();
    expect(screen.getByText("Training Log")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
  });
});
