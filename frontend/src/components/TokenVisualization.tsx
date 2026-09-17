import TokenCard from "./TokenCard";
import type { BpeToken, Token } from "../types/api";

type AnyToken = Token | BpeToken;

interface TokenVisualizationProps {
  tokens: AnyToken[];
}

function tokenText(token: AnyToken): string {
  return "decoded_text" in token ? token.decoded_text : token.token_text;
}

function tokenBytes(token: AnyToken): number[] {
  return "token_bytes" in token ? token.token_bytes : [];
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
        />
      ))}
    </div>
  );
}

export default TokenVisualization;
