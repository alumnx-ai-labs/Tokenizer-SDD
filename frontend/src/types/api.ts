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

export type VocabularyStatus = "initial" | "existing" | "new";

export interface VocabularyEntry {
  token_id: number;
  token_text: string;
  frequency: number;
  status: VocabularyStatus;
}

export interface CustomToken {
  index: number;
  token_id: number;
  token_text: string;
  is_new: boolean;
}

export interface CustomTokenizationResult {
  text: string;
  tokens: CustomToken[];
  token_count: number;
  character_count: number;
  word_count: number;
  tokens_per_word: number;
  tokens_per_character: number;
  vocabulary_size: number;
  new_token_count: number;
  vocabulary: VocabularyEntry[];
}

export interface VocabularyResponse {
  vocabulary: VocabularyEntry[];
  vocabulary_size: number;
}

export interface ResetResponse {
  vocabulary: VocabularyEntry[];
  vocabulary_size: number;
}

export interface ApiErrorResponse {
  error_code: string;
  detail: string;
}
