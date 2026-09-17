export type TokenizerMode = "tiktokenizer" | "custom";

interface TokenizerModeSelectorProps {
  mode: TokenizerMode;
  onChange: (mode: TokenizerMode) => void;
}

function TokenizerModeSelector({ mode, onChange }: TokenizerModeSelectorProps) {
  return (
    <fieldset>
      <legend>Tokenizer</legend>
      <label>
        <input
          type="radio"
          name="tokenizer-mode"
          value="tiktokenizer"
          checked={mode === "tiktokenizer"}
          onChange={() => onChange("tiktokenizer")}
        />
        Tiktokenizer
      </label>
      <label>
        <input
          type="radio"
          name="tokenizer-mode"
          value="custom"
          checked={mode === "custom"}
          onChange={() => onChange("custom")}
        />
        BPE Custom Tokenizer
      </label>
    </fieldset>
  );
}

export default TokenizerModeSelector;
