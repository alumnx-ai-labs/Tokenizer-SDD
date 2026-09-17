import type { BpeTrainingStep } from "../types/api";

interface BpeTrainingLogProps {
  trainingLog: BpeTrainingStep[];
}

function BpeTrainingLog({ trainingLog }: BpeTrainingLogProps) {
  return (
    <table className="bpe-training-log">
      <thead>
        <tr>
          <th>Step</th>
          <th>Pair</th>
          <th>Frequency</th>
          <th>Merged Token</th>
        </tr>
      </thead>
      <tbody>
        {trainingLog.map((entry) => (
          <tr key={entry.step}>
            <td>{entry.step}</td>
            <td>
              {entry.pair[0]} + {entry.pair[1]}
            </td>
            <td>{entry.frequency}</td>
            <td>{entry.merged_token_text}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default BpeTrainingLog;
