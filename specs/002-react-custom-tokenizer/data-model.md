# Data Model: React Frontend with Dual Tokenizer Modes

**Feature**: [spec.md](./spec.md) | **Date**: 2026-09-16

## Carried Over from Feature 001 (unchanged unless noted)

- `SupportedEncoding`, `SourceType`, `TokenStatistics`, `ErrorResponse` —
  unchanged.
- `Token` — **extended** with a new field:

  | Field | Type | Notes |
  |---|---|---|
  | index | `int` | unchanged |
  | token_id | `int` | unchanged |
  | decoded_text | `str` | unchanged |
  | token_bytes | `list[int]` | **new** — raw byte values (0–255) of the token's decoded byte sequence (FR-004) |

- `TokenizationResult`, `TextTokenizeRequest`, `EncodingsResponse` —
  unchanged in shape (still describe Tiktokenizer results only).

## New: Custom Tokenizer Entities

### VocabularyEntry

One row in a session's custom vocabulary (transient, in-memory only).

| Field | Type | Notes |
|---|---|---|
| token_id | `int` | Deterministic, assigned in creation order starting from the seed vocabulary's next free ID (FR-006) |
| token_text | `str` | Display text, stored using the casing it was first seen with; lookup for word tokens is case-insensitive (FR-008, clarified 2026-09-16) |
| frequency | `int` | Number of times this token has been produced in this session; seed entries start at `0` |
| status | `str` (enum: `initial`, `existing`, `new`) | Computed per response, not stored: `initial` = seed entry never yet produced, `existing` = produced before this request, `new` = first produced by this request |

### CustomToken

One token in a single tokenization result's ordered output.

| Field | Type | Notes |
|---|---|---|
| index | `int` | Position in the sequence (0-based) |
| token_id | `int` | The vocabulary entry's ID this token resolved to |
| token_text | `str` | The exact substring this token represents (original casing as it appeared in the input) |
| is_new | `bool` | `true` only if this exact request caused the vocabulary entry to be created |

### CustomTokenizeRequest

| Field | Type | Notes |
|---|---|---|
| text | `str` | Raw or extracted text to tokenize (FR-001) |
| (session id) | header `X-Session-Id` | Not a body field — carried as an HTTP header on every custom-tokenizer request (see research.md) |

**Validation rules**: identical to the Tiktokenizer text/file validation —
non-empty after whitespace-stripping, upload size ≤ 5 MB, supported file
extension (FR-016). The `X-Session-Id` header is required; a missing or
empty header is a validation error (FR-017).

### CustomTokenizationResult

| Field | Type | Notes |
|---|---|---|
| text | `str` | Original/extracted text tokenized (FR-009) |
| tokens | `list[CustomToken]` | Every resulting token, in order, no cap (consistent with the no-truncation philosophy already established for Tiktokenizer) |
| token_count | `int` | `len(tokens)` |
| character_count | `int` | `len(text)` |
| word_count | `int` | Whitespace-split word count, consistent with Tiktokenizer's definition |
| tokens_per_word | `float` | Guarded against division by zero |
| tokens_per_character | `float` | Guarded against division by zero |
| vocabulary_size | `int` | Total vocabulary entries *after* this request's updates |
| new_token_count | `int` | Count of entries created by this exact request (`0` on a pure repeat, FR-009) |
| vocabulary | `list[VocabularyEntry]` | Full current vocabulary snapshot, no cap (clarified 2026-09-16) |

### VocabularyResponse

Returned by `GET /api/v1/custom-tokenizer/vocabulary` (no tokenization
performed — just a read of current state).

| Field | Type | Notes |
|---|---|---|
| vocabulary | `list[VocabularyEntry]` | Full current vocabulary for the requesting session |
| vocabulary_size | `int` | `len(vocabulary)` |

### ResetResponse

Returned by `POST /api/v1/custom-tokenizer/reset`.

| Field | Type | Notes |
|---|---|---|
| vocabulary | `list[VocabularyEntry]` | The restored initial vocabulary (FR-015) |
| vocabulary_size | `int` | Equal to the seed vocabulary's size |

## Tokenizer Session (conceptual, not a request/response schema)

- **Identity**: an opaque string (`X-Session-Id` header value) the
  frontend generates and persists in `localStorage`; the backend does not
  validate its format beyond non-empty.
- **Lifetime**: exists in the backend process's memory only, for as long
  as the process runs and the frontend keeps using the same id; lost on
  backend restart (FR-011). Never written to disk or any database.
- **Isolation**: one `{seed vocabulary} → mutated vocabulary` mapping per
  session id, held in a single process-wide dictionary guarded by one
  lock (FR-010).

## Entity Relationships

```
CustomTokenizeRequest --(X-Session-Id routes to a)--> Tokenizer Session
Tokenizer Session --owns--> VocabularyEntry (0..*)
CustomTokenizationResult *---- 1..* ----* CustomToken
CustomTokenizationResult ---- includes a snapshot of ----> VocabularyEntry (0..*)
```

No entity here persists beyond the backend process's in-memory lifetime,
and none is shared across session ids — consistent with FR-010/FR-011 and
constitution Principle XI (no database).
