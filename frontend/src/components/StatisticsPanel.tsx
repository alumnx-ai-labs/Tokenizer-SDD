import type { TokenStatistics } from "../types/api";

interface StatisticsPanelProps {
  stats: TokenStatistics;
  vocabularySize?: number;
  newTokenCount?: number;
}

function StatisticsPanel({ stats, vocabularySize, newTokenCount }: StatisticsPanelProps) {
  return (
    <div className="statistics-panel">
      <div>
        <span>Characters</span>
        <strong>{stats.character_count}</strong>
      </div>
      <div>
        <span>Words</span>
        <strong>{stats.word_count}</strong>
      </div>
      <div>
        <span>Tokens</span>
        <strong>{stats.token_count}</strong>
      </div>
      <div>
        <span>Tokens/Word</span>
        <strong>{stats.tokens_per_word.toFixed(2)}</strong>
      </div>
      <div>
        <span>Tokens/Char</span>
        <strong>{stats.tokens_per_character.toFixed(2)}</strong>
      </div>
      {vocabularySize !== undefined && (
        <div>
          <span>Vocabulary</span>
          <strong>{vocabularySize}</strong>
        </div>
      )}
      {newTokenCount !== undefined && (
        <div>
          <span>New Tokens</span>
          <strong>{newTokenCount}</strong>
        </div>
      )}
    </div>
  );
}

export default StatisticsPanel;
