interface TokenizeButtonProps {
  onClick: () => void;
  loading: boolean;
}

function TokenizeButton({ onClick, loading }: TokenizeButtonProps) {
  return (
    <button type="button" onClick={onClick} disabled={loading}>
      Tokenize
    </button>
  );
}

export default TokenizeButton;
