import { useEffect, useState } from "react";
import VocabularySearch from "./VocabularySearch";
import ResetVocabularyButton from "./ResetVocabularyButton";
import { getVocabulary, resetVocabulary } from "../api/client";
import type { VocabularyEntry } from "../types/api";

interface VocabularyPanelProps {
  sessionId: string;
  refreshKey: number;
}

function VocabularyPanel({ sessionId, refreshKey }: VocabularyPanelProps) {
  const [vocabulary, setVocabulary] = useState<VocabularyEntry[]>([]);

  useEffect(() => {
    getVocabulary(sessionId)
      .then((response) => setVocabulary(response.vocabulary))
      .catch(() => {
        // Vocabulary display failures are non-fatal; the main tokenize
        // flow already surfaces backend errors via ErrorMessage.
      });
  }, [sessionId, refreshKey]);

  async function handleReset() {
    const response = await resetVocabulary(sessionId);
    setVocabulary(response.vocabulary);
  }

  return (
    <div className="vocabulary-panel">
      <h2>Vocabulary</h2>
      <ResetVocabularyButton onConfirm={handleReset} />
      <VocabularySearch vocabulary={vocabulary} />
    </div>
  );
}

export default VocabularyPanel;
