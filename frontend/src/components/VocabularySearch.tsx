import { useState } from "react";
import VocabularyTable from "./VocabularyTable";
import type { VocabularyEntry } from "../types/api";

interface VocabularySearchProps {
  vocabulary: VocabularyEntry[];
}

function VocabularySearch({ vocabulary }: VocabularySearchProps) {
  const [query, setQuery] = useState("");

  const filtered = vocabulary.filter((entry) =>
    entry.token_text.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="vocabulary-search">
      <input
        type="text"
        placeholder="Search vocabulary..."
        value={query}
        onChange={(event) => setQuery(event.target.value)}
      />
      <div className="vocabulary-table-wrapper">
        <VocabularyTable vocabulary={filtered} />
      </div>
    </div>
  );
}

export default VocabularySearch;
