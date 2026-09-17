export type CustomTokenizerSubMode = "train-bpe" | "tokenize-bpe";

interface CustomTokenizerSubModeSelectorProps {
  mode: CustomTokenizerSubMode;
  onChange: (mode: CustomTokenizerSubMode) => void;
}

function CustomTokenizerSubModeSelector({ mode, onChange }: CustomTokenizerSubModeSelectorProps) {
  return (
    <fieldset className="custom-tokenizer-sub-mode-selector">
      <legend>Custom Tokenizer Flow</legend>
      <label>
        <input
          type="radio"
          name="custom-tokenizer-sub-mode"
          value="train-bpe"
          checked={mode === "train-bpe"}
          onChange={() => onChange("train-bpe")}
        />
        Train BPE
      </label>
      <label>
        <input
          type="radio"
          name="custom-tokenizer-sub-mode"
          value="tokenize-bpe"
          checked={mode === "tokenize-bpe"}
          onChange={() => onChange("tokenize-bpe")}
        />
        Tokenize with BPE
      </label>
    </fieldset>
  );
}

export default CustomTokenizerSubModeSelector;
