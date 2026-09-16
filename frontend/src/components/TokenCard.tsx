interface TokenCardProps {
  index: number;
  tokenId: number;
  tokenText: string;
  tokenBytes: number[];
  isNew?: boolean;
}

function TokenCard({ index, tokenId, tokenText, tokenBytes, isNew }: TokenCardProps) {
  return (
    <div className={isNew ? "token-card token-card--new" : "token-card"}>
      <span>#{index}</span>
      <strong>{tokenText}</strong>
      <span>ID: {tokenId}</span>
      <span>Bytes: [{tokenBytes.join(", ")}]</span>
      {isNew && <span className="token-card__badge">NEW</span>}
    </div>
  );
}

export default TokenCard;
