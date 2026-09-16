import type { VocabularyEntry } from "../types/api";

interface VocabularyTableProps {
  vocabulary: VocabularyEntry[];
}

function VocabularyTable({ vocabulary }: VocabularyTableProps) {
  return (
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Token</th>
          <th>Frequency</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {vocabulary.map((entry) => (
          <tr key={entry.token_id}>
            <td>{entry.token_id}</td>
            <td>{entry.token_text}</td>
            <td>{entry.frequency}</td>
            <td>{entry.status}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default VocabularyTable;
