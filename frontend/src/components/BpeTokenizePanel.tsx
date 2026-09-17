import { useState } from "react";

interface BpeTokenizePanelProps {
  hasTrainedModel: boolean;
  loading: boolean;
  onSubmit: (text: string) => void;
}

function BpeTokenizePanel({ hasTrainedModel, loading, onSubmit }: BpeTokenizePanelProps) {
  const [text, setText] = useState("");

  if (!hasTrainedModel) {
    return (
      <div className="bpe-tokenize-blocked">
        Train a BPE model first before tokenizing with it.
      </div>
    );
  }

  return (
    <div className="bpe-tokenize-panel">
      <textarea
        aria-label="BPE tokenize text"
        value={text}
        onChange={(event) => setText(event.target.value)}
        rows={6}
        style={{ width: "100%" }}
      />
      <button type="button" onClick={() => onSubmit(text)} disabled={loading}>
        Tokenize with BPE
      </button>
    </div>
  );
}

export default BpeTokenizePanel;
