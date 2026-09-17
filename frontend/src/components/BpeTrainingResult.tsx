import BpeTrainingLog from "./BpeTrainingLog";
import BpeVocabularyTable from "./BpeVocabularyTable";
import type { BpeTrainResponse } from "../types/api";

interface BpeTrainingResultProps {
  result: BpeTrainResponse | null;
}

function BpeTrainingResult({ result }: BpeTrainingResultProps) {
  if (!result) {
    return (
      <div className="bpe-training-result-empty">No BPE model has been trained yet.</div>
    );
  }

  return (
    <div className="bpe-training-result">
      <h3>Vocabulary ({result.vocabulary_size})</h3>
      <BpeVocabularyTable vocabulary={result.vocabulary} />
      <h3>Training Log</h3>
      <BpeTrainingLog trainingLog={result.training_log} />
    </div>
  );
}

export default BpeTrainingResult;
