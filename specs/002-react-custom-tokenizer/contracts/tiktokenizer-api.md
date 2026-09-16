# API Contract: Tiktokenizer Endpoints (updated)

**Feature**: [../spec.md](../spec.md) | **Data model**: [../data-model.md](../data-model.md)

Base path: `/api/v1`. These two endpoints already exist (feature
001-tokenizer-app) and keep their paths, request shapes, and error
behavior. The only change is one added field per token.

## GET /api/v1/encodings

Unchanged.

## POST /api/v1/tokenize/text

Unchanged request. **Response 200** (`TokenizationResult`): each entry in
`tokens` now additionally includes `token_bytes: number[]` (FR-004).

```json
{
  "text": "Hi!",
  "encoding": "cl100k_base",
  "source_type": "text",
  "tokens": [
    {"index": 0, "token_id": 13347, "decoded_text": "Hi", "token_bytes": [72, 105]},
    {"index": 1, "token_id": 0, "decoded_text": "!", "token_bytes": [33]}
  ],
  "statistics": { "character_count": 3, "word_count": 1, "token_count": 2, "tokens_per_word": 2.0, "tokens_per_character": 0.666 }
}
```

Error responses: unchanged from feature 001 (`empty_input`,
`upload_too_large`, `unsupported_encoding`, `internal_error`).

## POST /api/v1/tokenize/file

Unchanged request/error behavior. Same `token_bytes` addition to the
response's `tokens` entries as above.
