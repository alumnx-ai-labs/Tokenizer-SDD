import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import TokenCard from "./TokenCard";

describe("TokenCard", () => {
  it("renders index, ID, decoded text, and bytes", () => {
    render(
      <TokenCard index={0} tokenId={9906} tokenText="Hello" tokenBytes={[72, 101, 108, 108, 111]} />
    );

    expect(screen.getByText("#0")).toBeInTheDocument();
    expect(screen.getByText(/9906/)).toBeInTheDocument();
    expect(screen.getByText("Hello")).toBeInTheDocument();
    expect(screen.getByText(/72, 101, 108, 108, 111/)).toBeInTheDocument();
  });

  it("renders a distinct visual state when isNew is true", () => {
    render(
      <TokenCard
        index={0}
        tokenId={6}
        tokenText="developer"
        tokenBytes={[100]}
        isNew
      />
    );

    expect(screen.getByText(/NEW/i)).toBeInTheDocument();
  });

  it("does not render a NEW badge when isNew is false", () => {
    render(
      <TokenCard index={0} tokenId={1} tokenText="hello" tokenBytes={[104]} isNew={false} />
    );

    expect(screen.queryByText(/NEW/i)).not.toBeInTheDocument();
  });
});
