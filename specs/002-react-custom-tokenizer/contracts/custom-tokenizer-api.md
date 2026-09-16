# API Contract: Custom Tokenizer Endpoints (new)

**Feature**: [../spec.md](../spec.md) | **Data model**: [../data-model.md](../data-model.md)

Base path: `/api/v1/custom-tokenizer`. All four endpoints below **require**
an `X-Session-Id` header (any non-empty string, generated and persisted by
the frontend). A missing/empty header returns:

```json
{ "error_code": "missing_session_id", "detail": "An X-Session-Id header is required for Custom Tokenizer requests." }
```
with HTTP 400.

## POST /api/v1/custom-tokenizer/tokenize/text

Tokenizes directly provided text with the requesting session's custom
vocabulary (FR-001, FR-005–FR-009).

**Request body**:
```json
{ "text": "string, required" }
```

**Response 200** (`CustomTokenizationResult`, see data-model.md):
```json
{
  "text": "hello developer",
  "tokens": [
    {"index": 0, "token_id": 1, "token_text": "hello", "is_new": false},
    {"index": 1, "token_id": 5, "token_text": " ", "is_new": false},
    {"index": 2, "token_id": 6, "token_text": "developer", "is_new": true}
  ],
  "token_count": 3,
  "character_count": 16,
  "word_count": 2,
  "tokens_per_word": 1.5,
  "tokens_per_character": 0.1875,
  "vocabulary_size": 7,
  "new_token_count": 1,
  "vocabulary": [ /* full VocabularyEntry[] snapshot, no cap */ ]
}
```

**Error responses**:
| Status | error_code | Condition |
|---|---|---|
| 400 | `missing_session_id` | `X-Session-Id` header absent/empty |
| 400 | `empty_input` | `text` empty or whitespace-only (FR-016) |
| 400 | `invalid_tokenizer_state` | The session's tokenizer state is corrupted (FR-017) |
| 500 | `internal_error` | Unexpected failure |

## POST /api/v1/custom-tokenizer/tokenize/file

Same behavior as the text endpoint, but for an uploaded `.txt`/`.pdf` file
(FR-001). Request/error shape mirrors `POST /api/v1/tokenize/file` from the
Tiktokenizer contract (multipart `file` field; no `encoding` field is
needed here since the Custom Tokenizer has no encoding concept).

**Additional error responses** (beyond the text endpoint's):
| Status | error_code | Condition |
|---|---|---|
| 400 | `unsupported_file_type` | Extension not `.txt`/`.pdf` (FR-016) |
| 400 | `invalid_pdf` | PDF cannot be parsed (FR-016) |
| 400 | `no_extractable_text` | PDF has no extractable text (FR-016) |
| 413 | `upload_too_large` | File exceeds 5 MB (FR-016) |

## GET /api/v1/custom-tokenizer/vocabulary

Returns the requesting session's current vocabulary without performing any
tokenization (used to populate the Vocabulary panel on mode switch or page
load, per FR-012).

**Response 200** (`VocabularyResponse`):
```json
{
  "vocabulary": [
    {"token_id": 0, "token_text": "<UNK>", "frequency": 0, "status": "initial"},
    {"token_id": 1, "token_text": "hello", "frequency": 4, "status": "existing"}
  ],
  "vocabulary_size": 2
}
```

If the session id has never been seen before, the backend auto-creates a
fresh seeded vocabulary for it and returns that (never a 404).

## POST /api/v1/custom-tokenizer/reset

Restores the requesting session's vocabulary to its initial seed state,
discarding every dynamically added token and resetting all frequencies
(FR-015). Takes no request body.

**Response 200** (`ResetResponse`):
```json
{
  "vocabulary": [
    {"token_id": 0, "token_text": "<UNK>", "frequency": 0, "status": "initial"},
    {"token_id": 1, "token_text": "hello", "frequency": 0, "status": "initial"},
    {"token_id": 2, "token_text": "world", "frequency": 0, "status": "initial"}
  ],
  "vocabulary_size": 3
}
```

## Notes for the frontend

- The Custom Tokenizer never touches tiktoken; the frontend MUST NOT
  imply otherwise anywhere in its UI copy (spec's "Important
  Distinction").
- Switching tokenizer mode keeps the currently entered input but clears
  any displayed result until the user tokenizes again (FR-002, clarified
  2026-09-16) — this is frontend-only state management, not a backend
  concern.
- The vocabulary table and search (FR-012, FR-013) operate on the full
  `vocabulary` array returned by whichever call was most recent
  (tokenize, the vocabulary GET, or reset) — no additional pagination
  endpoint exists.
