import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import * as apiClient from "./api/client";

describe("App mode switching (FR-002)", () => {
  beforeEach(() => {
    vi.spyOn(apiClient, "getEncodings").mockResolvedValue(["cl100k_base"]);
    vi.spyOn(apiClient, "tokenizeText").mockResolvedValue({
      text: "hello",
      encoding: "cl100k_base",
      source_type: "text",
      tokens: [{ index: 0, token_id: 1, decoded_text: "hello", token_bytes: [104] }],
      statistics: {
        character_count: 5,
        word_count: 1,
        token_count: 1,
        tokens_per_word: 1,
        tokens_per_character: 0.2,
      },
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("preserves entered text but clears the previous result when switching modes", async () => {
    render(<App />);

    await waitFor(() => expect(apiClient.getEncodings).toHaveBeenCalled());

    const textarea = screen.getByLabelText("Text to tokenize");
    fireEvent.change(textarea, { target: { value: "hello" } });

    fireEvent.click(screen.getByText("Tokenize"));
    await waitFor(() => expect(screen.getByText("Tokenized Output")).toBeInTheDocument());

    fireEvent.click(screen.getByLabelText("Custom Tokenizer"));

    expect(screen.queryByText("Tokenized Output")).not.toBeInTheDocument();
    expect(screen.getByLabelText("Text to tokenize")).toHaveValue("hello");
  });
});
