import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
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

  it("preserves entered text but clears the previous result when switching away and back", async () => {
    render(<App />);

    await waitFor(() => expect(apiClient.getEncodings).toHaveBeenCalled());

    const textarea = screen.getByLabelText("Text to tokenize");
    fireEvent.change(textarea, { target: { value: "hello" } });

    fireEvent.click(screen.getByText("Tokenize"));
    await waitFor(() => expect(screen.getByText("Tokenized Output")).toBeInTheDocument());

    fireEvent.click(screen.getByLabelText("BPE Custom Tokenizer"));

    expect(screen.queryByText("Tokenized Output")).not.toBeInTheDocument();
    expect(screen.queryByLabelText("Text to tokenize")).not.toBeInTheDocument();

    fireEvent.click(screen.getByLabelText("Tiktokenizer"));

    expect(screen.queryByText("Tokenized Output")).not.toBeInTheDocument();
    expect(screen.getByLabelText("Text to tokenize")).toHaveValue("hello");
  });
});

describe("App BPE sub-flows (US5/US6)", () => {
  beforeEach(() => {
    vi.spyOn(apiClient, "getEncodings").mockResolvedValue(["cl100k_base"]);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("shows the blocked empty state before training and does not call the tokenize API", async () => {
    const tokenizeSpy = vi.spyOn(apiClient, "bpeTokenizeText");
    render(<App />);
    await waitFor(() => expect(apiClient.getEncodings).toHaveBeenCalled());

    fireEvent.click(screen.getByLabelText("BPE Custom Tokenizer"));
    fireEvent.click(screen.getByLabelText("Tokenize with BPE"));

    expect(screen.getByText(/train a bpe model first/i)).toBeInTheDocument();
    expect(tokenizeSpy).not.toHaveBeenCalled();
  });

  it("trains a BPE model then tokenizes with it, rendering results in the shared result table", async () => {
    vi.spyOn(apiClient, "trainBpe").mockResolvedValue({
      vocabulary: [
        { token_id: 0, token_text: "a" },
        { token_id: 1, token_text: "b" },
        { token_id: 2, token_text: " " },
        { token_id: 3, token_text: "ab" },
      ],
      merge_rules: [{ step: 1, pair: ["a", "b"], merged_token_text: "ab" }],
      training_log: [{ step: 1, pair: ["a", "b"], frequency: 3, merged_token_text: "ab" }],
      vocabulary_size: 4,
    });
    vi.spyOn(apiClient, "bpeTokenizeText").mockResolvedValue({
      text: "ab",
      tokens: [{ index: 0, token_id: 3, token_text: "ab" }],
      token_count: 1,
      character_count: 2,
      word_count: 1,
      tokens_per_word: 1,
      tokens_per_character: 0.5,
    });

    render(<App />);
    await waitFor(() => expect(apiClient.getEncodings).toHaveBeenCalled());

    fireEvent.click(screen.getByLabelText("BPE Custom Tokenizer"));
    fireEvent.click(screen.getByLabelText("Train BPE"));

    fireEvent.change(screen.getByLabelText("BPE training text"), {
      target: { value: "ab ab ab" },
    });
    fireEvent.change(screen.getByLabelText("Target vocabulary size"), {
      target: { value: "10" },
    });
    fireEvent.click(screen.getByText("Train"));

    await waitFor(() => expect(screen.getByText("Vocabulary (4)")).toBeInTheDocument());

    fireEvent.click(screen.getByLabelText("Tokenize with BPE"));
    expect(screen.getByLabelText("BPE tokenize text")).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("BPE tokenize text"), { target: { value: "ab" } });
    fireEvent.click(screen.getByRole("button", { name: "Tokenize with BPE" }));

    await waitFor(() => expect(screen.getByText("Tokenized Output")).toBeInTheDocument());
    const tokenCard = document.querySelector(".token-card");
    expect(tokenCard).not.toBeNull();
    expect(within(tokenCard as HTMLElement).getByText("ab")).toBeInTheDocument();
  });
});
