import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import VocabularySearch from "./VocabularySearch";
import type { VocabularyEntry } from "../types/api";

describe("VocabularySearch", () => {
  const vocabulary: VocabularyEntry[] = [
    { token_id: 0, token_text: "<UNK>", frequency: 0, status: "initial" },
    { token_id: 1, token_text: "hello", frequency: 4, status: "existing" },
    { token_id: 2, token_text: "world", frequency: 2, status: "existing" },
  ];

  it("filters the vocabulary table by a case-insensitive text match", () => {
    render(<VocabularySearch vocabulary={vocabulary} />);

    fireEvent.change(screen.getByPlaceholderText("Search vocabulary..."), {
      target: { value: "HELLO" },
    });

    expect(screen.getByText("hello")).toBeInTheDocument();
    expect(screen.queryByText("world")).not.toBeInTheDocument();
  });
});
