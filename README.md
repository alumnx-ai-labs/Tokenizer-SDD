# Tokenizer Application

A small, stateless web tool that tokenizes text — pasted directly, or
extracted from an uploaded `.txt`/`.pdf` file — using either `tiktoken`
(Tiktokenizer mode) or an independent, educational Custom Tokenizer with
its own dynamically-growing vocabulary.

See [specs/002-react-custom-tokenizer/quickstart.md](specs/002-react-custom-tokenizer/quickstart.md)
for full validation scenarios. Quick version:

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

cd frontend
npm install
```

## Run the backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

## Run the frontend

In a second terminal:

```bash
cd frontend
npm run dev
```

Open the URL Vite prints (default `http://localhost:5173`). The frontend
reads the backend URL from `VITE_TOKENIZER_API_URL` (default
`http://localhost:8000`); set it in `frontend/.env.local` if needed (see
`frontend/.env.local.example`).

## Frontend Overview

The React app (`frontend/src/`) lets users tokenize text with either of two
independent tokenizer engines and inspect the result.

### Tokenizer mode

- **Tiktokenizer** (default) — uses the `tiktoken` library. Supported
  encodings (defined in `backend/app/core/config.py`):
  - `cl100k_base` — used by GPT-3.5-turbo and GPT-4 (~100k vocab). General-purpose, good for English and code.
  - `o200k_base` — used by GPT-4o (~200k vocab). Larger vocabulary, more efficient for non-English text and special characters.
  - `p50k_base` — used by earlier GPT-3 models and Codex (~50k vocab). Well-tuned for code.
  - `r50k_base` — the original GPT-2/GPT-3 encoding (~50k vocab). Kept for legacy comparison.
- **Custom Tokenizer** — a separate, deterministic tokenizer with its own
  small seed vocabulary that grows as unseen words/punctuation/numbers are
  encountered. It never reads or writes tiktoken's encodings. Each browser
  gets its own isolated, in-memory vocabulary (via a generated session ID),
  which can be reset back to its initial state at any time.

### Inputs

- **Input mode (tabs)** — "Text", "TXT", or "PDF".
  - Text mode shows a large text area to type/paste directly into.
  - Upload modes show a file uploader restricted to `.txt` or `.pdf`.
- **Encoding dropdown** *(Tiktokenizer mode only)* — choose which `tiktoken`
  encoding to tokenize with. Picking a different encoding changes the
  "vocabulary" used to split text, so the same input can produce a
  different number of tokens depending on which one is selected.
- **Tokenize button** — sends the text/file to the backend for processing
  with whichever tokenizer is currently selected.

### Output

- **Statistics** — 5 metric tiles for both modes (Custom Tokenizer mode adds
  two more: Vocabulary and New Tokens):

  | Tile | Meaning | Computation |
  |---|---|---|
  | Characters | Total character count | `len(text)` (includes spaces/newlines) |
  | Words | Total word count | `len(text.split())` (splits on whitespace) |
  | Tokens | Number of tokens produced | `len(tokens)` |
  | Tokens/Word | Average tokens per word | `token_count / word_count` (0.0 if no words) |
  | Tokens/Character | Average tokens per character | `token_count / character_count` (0.0 if empty) |
  | Vocabulary *(Custom Tokenizer only)* | Current vocabulary size for this session | count of vocabulary entries after this request |
  | New Tokens *(Custom Tokenizer only)* | Tokens/punctuation/numbers not seen before in this session | count of units from this request not already in the vocabulary |

  Ratios are displayed rounded to 2 decimal places in the UI; the backend
  returns unrounded floats.

- **Tokenized Output** — a card per token produced, showing:
  - `#index` — its position in the sequence
  - **text** — the token's text (decoded text for Tiktokenizer mode, the raw
    unit for Custom Tokenizer mode)
  - **ID** — its numeric token ID
  - **Bytes** — the token's raw UTF-8 byte values

  In Tiktokenizer mode, tokenization uses Byte-Pair Encoding (BPE), so token
  boundaries are not fixed-length — common words/substrings seen often during
  training tend to become single tokens, while rarer words get split into
  smaller pieces. In Custom Tokenizer mode, newly created tokens are visibly
  marked "NEW".

- **Vocabulary** *(Custom Tokenizer mode only)* — a live, searchable table
  of every vocabulary entry (ID, token, frequency, status), plus a "Reset
  Vocabulary" button (with a confirmation step) that restores the seed
  vocabulary.

## Run tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```
