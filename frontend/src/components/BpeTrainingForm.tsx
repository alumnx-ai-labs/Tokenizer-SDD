import { useState } from "react";

interface BpeTrainingFormProps {
  loading: boolean;
  validationError?: string;
  onSubmit: (trainingText: string, vocabSize: number) => void;
}

function BpeTrainingForm({ loading, validationError, onSubmit }: BpeTrainingFormProps) {
  const [trainingText, setTrainingText] = useState("");
  const [vocabSize, setVocabSize] = useState(300);

  function handleSubmit() {
    onSubmit(trainingText, vocabSize);
  }

  return (
    <div className="bpe-training-form">
      <textarea
        aria-label="BPE training text"
        value={trainingText}
        onChange={(event) => setTrainingText(event.target.value)}
        rows={8}
        style={{ width: "100%" }}
      />
      <label>
        Target vocabulary size
        <input
          type="number"
          aria-label="Target vocabulary size"
          value={vocabSize}
          onChange={(event) => setVocabSize(Number(event.target.value))}
        />
      </label>
      <button type="button" onClick={handleSubmit} disabled={loading}>
        Train
      </button>
      {validationError && <div role="alert">{validationError}</div>}
    </div>
  );
}

export default BpeTrainingForm;
