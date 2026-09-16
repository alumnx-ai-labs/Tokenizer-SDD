import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import StatisticsPanel from "./StatisticsPanel";

describe("StatisticsPanel", () => {
  it("renders character/word/token counts and ratios", () => {
    render(
      <StatisticsPanel
        stats={{
          character_count: 23,
          word_count: 3,
          token_count: 5,
          tokens_per_word: 1.67,
          tokens_per_character: 0.22,
        }}
      />
    );

    expect(screen.getByText("23")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByText("1.67")).toBeInTheDocument();
    expect(screen.getByText("0.22")).toBeInTheDocument();
  });

  it("renders vocabulary and new-token tiles when custom stats are given", () => {
    render(
      <StatisticsPanel
        stats={{
          character_count: 10,
          word_count: 2,
          token_count: 3,
          tokens_per_word: 1.5,
          tokens_per_character: 0.3,
        }}
        vocabularySize={7}
        newTokenCount={1}
      />
    );

    expect(screen.getByText("7")).toBeInTheDocument();
    expect(screen.getByText("1")).toBeInTheDocument();
  });
});
