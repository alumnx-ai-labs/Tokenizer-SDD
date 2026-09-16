import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import TokenVisualization from "./TokenVisualization";
import type { Token } from "../types/api";

describe("TokenVisualization", () => {
  it("renders one TokenCard per token with no cap", () => {
    const tokens: Token[] = Array.from({ length: 50 }, (_, i) => ({
      index: i,
      token_id: i,
      decoded_text: `t${i}`,
      token_bytes: [i],
    }));

    render(<TokenVisualization tokens={tokens} />);

    expect(screen.getAllByText(/t\d+/)).toHaveLength(50);
  });
});
