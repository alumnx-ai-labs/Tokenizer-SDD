import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import VocabularyTable from "./VocabularyTable";
import type { VocabularyEntry } from "../types/api";

describe("VocabularyTable", () => {
  it("renders ID/Token/Frequency/Status columns for each entry", () => {
    const vocabulary: VocabularyEntry[] = [
      { token_id: 0, token_text: "<UNK>", frequency: 0, status: "initial" },
      { token_id: 1, token_text: "hello", frequency: 4, status: "existing" },
      { token_id: 3, token_text: "developer", frequency: 1, status: "new" },
    ];

    render(<VocabularyTable vocabulary={vocabulary} />);

    expect(screen.getByText("hello")).toBeInTheDocument();
    expect(screen.getByText("developer")).toBeInTheDocument();
    expect(screen.getByText("existing")).toBeInTheDocument();
    expect(screen.getByText("new")).toBeInTheDocument();
    expect(screen.getByText("4")).toBeInTheDocument();
  });
});
