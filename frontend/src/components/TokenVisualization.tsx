import TokenCard from "./TokenCard";
import type { CustomToken, Token } from "../types/api";

interface TokenVisualizationProps {
  tokens: (Token | CustomToken)[];
}

function tokenText(token: Token | CustomToken): string {
  return "decoded_text" in token ? token.decoded_text : token.token_text;
}

function tokenBytes(token: Token | CustomToken): number[] {
  return "token_bytes" in token ? token.token_bytes : [];
}

function tokenIsNew(token: Token | CustomToken): boolean | undefined {
  return "is_new" in token ? token.is_new : undefined;
}

function TokenVisualization({ tokens }: TokenVisualizationProps) {
  return (
    <div className="token-visualization">
      {tokens.map((token) => (
        <TokenCard
          key={token.index}
          index={token.index}
          tokenId={token.token_id}
          tokenText={tokenText(token)}
          tokenBytes={tokenBytes(token)}
          isNew={tokenIsNew(token)}
        />
      ))}
    </div>
  );
}

export default TokenVisualization;
