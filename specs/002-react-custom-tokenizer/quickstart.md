# Quickstart: React Frontend with Dual Tokenizer Modes

**Feature**: [spec.md](./spec.md) | **Contracts**: [contracts/](./contracts/)

## Prerequisites

- Python 3.11+ (backend, unchanged)
- Node.js 18+ and npm (new, for the React frontend)

## Setup

```bash
# Backend (unchanged)
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# Frontend (new React app replaces the old Streamlit app)
cd frontend
npm install
```

## Run the backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

## Run the frontend

```bash
cd frontend
npm run dev
```

Open the URL Vite prints (default `http://localhost:5173`). The frontend
reads the backend URL from `VITE_TOKENIZER_API_URL` (default
`http://localhost:8000`); set it in `frontend/.env.local` if needed.

## Validate User Story 1 — Tiktokenizer parity on the new interface

1. Open the app; Tiktokenizer mode is selected by default.
2. Paste `"Hello, tokenizer world!"`, pick `cl100k_base`, click Tokenize.
3. **Expected**: statistics tiles populate, every token shows index/ID/
   decoded text/bytes, matching what the old Streamlit app produced for
   the same input (see [../001-tokenizer-app/quickstart.md](../001-tokenizer-app/quickstart.md)
   for the reference values).
4. Repeat with a `.txt` upload and a text-based `.pdf` upload.

## Validate User Story 2 — Custom Tokenizer new-vs-existing tokens

```bash
curl -s -X POST http://localhost:8000/api/v1/custom-tokenizer/tokenize/text \
  -H "Content-Type: application/json" \
  -H "X-Session-Id: quickstart-session" \
  -d '{"text": "hello developer"}' | python3 -m json.tool
```

**Expected**: `hello` resolves to an existing seed vocabulary entry
(`is_new: false`); `developer` is `is_new: true` and `new_token_count` is
`1`. Re-run the exact same command — `new_token_count` is now `0` and
`developer`'s `is_new` is `false`.

In the UI: switch to Custom Tokenizer mode, type the same text, tokenize,
and confirm the tokenized output visually marks "developer" as new, and
the Vocabulary panel below immediately shows it.

## Validate User Story 3 — Vocabulary view and search

1. In Custom Tokenizer mode, tokenize a few different sentences.
2. Confirm the Vocabulary panel lists every entry (ID, token, frequency,
   status) and updates after each tokenization with no manual refresh.
3. Type part of a known token into the search box and confirm the list
   filters to matches.

## Validate User Story 4 — Reset vocabulary

```bash
curl -s -X POST http://localhost:8000/api/v1/custom-tokenizer/reset \
  -H "X-Session-Id: quickstart-session"
```

**Expected**: `vocabulary_size` returns to the seed count, and every entry
has its initial frequency (`0`) and no dynamically added tokens remain.

In the UI: click "Reset Vocabulary", confirm the prompt, and confirm the
vocabulary panel shrinks back to the initial entries.

## Validate session isolation (SC-006)

```bash
curl -s -X POST http://localhost:8000/api/v1/custom-tokenizer/tokenize/text \
  -H "X-Session-Id: session-a" -d '{"text": "alpha"}'
curl -s http://localhost:8000/api/v1/custom-tokenizer/vocabulary \
  -H "X-Session-Id: session-b"
```

**Expected**: `session-b`'s vocabulary does NOT contain "alpha" — each
session id gets its own independent vocabulary.

## Run automated tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

**Expected**: all backend unit/API tests pass (including the new custom
tokenizer service/route tests), and all frontend component tests pass.
