import type { BpeVocabularyEntry } from "../types/api";

interface BpeVocabularyTableProps {
  vocabulary: BpeVocabularyEntry[];
}

function BpeVocabularyTable({ vocabulary }: BpeVocabularyTableProps) {
  return (
    <table className="bpe-vocabulary-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Token</th>
        </tr>
      </thead>
      <tbody>
        {vocabulary.map((entry) => (
          <tr key={entry.token_id}>
            <td>{entry.token_id}</td>
            <td>{entry.token_text}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default BpeVocabularyTable;
