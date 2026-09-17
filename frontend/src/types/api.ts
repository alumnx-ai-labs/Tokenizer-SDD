export type SupportedEncoding = "cl100k_base" | "o200k_base" | "p50k_base" | "r50k_base";

export type SourceType = "text" | "txt_file" | "pdf_file";

export interface Token {
  index: number;
  token_id: number;
  decoded_text: string;
  token_bytes: number[];
}

export interface TokenStatistics {
  character_count: number;
  word_count: number;
  token_count: number;
  tokens_per_word: number;
  tokens_per_character: number;
}

export interface TokenizationResult {
  text: string;
  encoding: SupportedEncoding;
  source_type: SourceType;
  tokens: Token[];
  statistics: TokenStatistics;
}

export interface EncodingsResponse {
  encodings: SupportedEncoding[];
}

export interface ApiErrorResponse {
  error_code: string;
  detail: string;
}

export interface BpeVocabularyEntry {
  token_id: number;
  token_text: string;
}

export interface BpeMergeRule {
  step: number;
  pair: string[];
  merged_token_text: string;
}

export interface BpeTrainingStep {
  step: number;
  pair: string[];
  frequency: number;
  merged_token_text: string;
}

export interface BpeTrainResponse {
  vocabulary: BpeVocabularyEntry[];
  merge_rules: BpeMergeRule[];
  training_log: BpeTrainingStep[];
  vocabulary_size: number;
}

export interface BpeToken {
  index: number;
  token_id: number;
  token_text: string;
}

export interface BpeTokenizeResult {
  text: string;
  tokens: BpeToken[];
  token_count: number;
  character_count: number;
  word_count: number;
  tokens_per_word: number;
  tokens_per_character: number;
}
