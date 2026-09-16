# Implementation Plan: React Frontend with Dual Tokenizer Modes

**Branch**: `002-react-custom-tokenizer` | **Date**: 2026-09-16 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-react-custom-tokenizer/spec.md`

## Summary

Replace the existing Streamlit frontend with a React + TypeScript single-page
app that talks to the same FastAPI backend over REST/HTTP, and add a second,
fully independent tokenizer engine — the Custom Tokenizer — alongside the
existing tiktoken-based one. The user picks exactly one tokenizer mode at a
time; Tiktokenizer behaves as before (plus a new `token_bytes` field per
token); Custom Tokenizer deterministically splits input into words/numbers/
whitespace/punctuation, looks each unit up in a per-session, in-memory,
case-insensitive-for-words vocabulary that grows as unseen tokens appear, and
exposes that vocabulary (with search) and a confirmed reset action. No
database, accounts, or authentication are introduced anywhere.

## Technical Context

**Language/Version**: Python 3.11+ (backend, unchanged); TypeScript 5.x +
Node.js 18+ (frontend, new)

**Primary Dependencies**:
- Backend (unchanged + one addition): FastAPI, uvicorn, Pydantic, tiktoken,
  PyMuPDF (`fitz`), python-multipart, pytest, httpx
- Frontend (replaces Streamlit): React 18, TypeScript, Vite, Vitest,
  React Testing Library

**Storage**: N/A for persistence (constitution Principle XI unchanged);
the Custom Tokenizer's vocabulary is process-memory-only, keyed by session
id (FR-011)

**Testing**: pytest (backend unit/API, extended for the custom tokenizer);
Vitest + React Testing Library (new, frontend component tests)

**Target Platform**: Local development machine / simple deployment — three
local processes: `uvicorn` (backend), `vite` dev server or its static build
output (frontend); no orchestration

**Project Type**: Web application (separate frontend + backend), with the
frontend's implementation technology changing from Streamlit to a React SPA

**Performance Goals**: None formally required (carried over from feature
001, still true — no new performance target introduced here)

**Constraints**: 5 MB max upload size unchanged and applies to both
tokenizer modes' file uploads; Custom Tokenizer vocabulary MUST NOT read or
write any tiktoken state; Custom Tokenizer split rule MUST be deterministic
and Unicode-aware; vocabulary/tokens returned MUST NOT be capped or
paginated (clarified 2026-09-16); custom vocabulary MUST be isolated per
session (FR-010)

**Scale/Scope**: Same single-tool scope as feature 001, now offering two
tokenizer engines and 6 backend endpoints total (2 existing + 4 new)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Update (2026-09-16, post-`/speckit-analyze`)**: the constitution has
been amended to v2.0.0 (Principles II and V rescoped; Technology Stack
updated) to formally ratify this feature's frontend-technology and
dual-tokenizer requirements. The conflicts originally flagged here are
resolved; the table below reflects the amended constitution. The original
conflict discussion is preserved in research.md's "Constitution Conflict"
entry for history.

| Principle | Check | Status |
|---|---|---|
| I. Simple, Modular Architecture | Still two services (frontend, backend) over REST/HTTP only; frontend's implementation technology changes, its role does not | PASS |
| II. Frontend Is Presentation-Only | React frontend keeps the same presentation-only role the constitution now names generically | PASS |
| III. FastAPI Owns Tokenization/Processing | Both tokenizer engines (tiktoken and the new Custom Tokenizer) live entirely in backend `services/`; frontend still never processes text | PASS |
| IV. No Duplicated Tokenization Logic | React frontend never re-implements tiktoken or the custom split/vocabulary logic; both come from the backend API | PASS |
| V. tiktoken Is Single Source of Truth for Tiktokenizer Mode | Custom Tokenizer is the one explicitly-permitted second engine, fully independent, never touching tiktoken state | PASS |
| VI. Backend-Enforced Validation | All existing validation (size/type/encoding/empty) still enforced server-side for both modes; new `X-Session-Id` validation added the same way | PASS |
| VII. Explicit API Contracts via Pydantic | Every new/changed endpoint uses explicit Pydantic request/response models, including `response_model=` on every route (see contracts/) | PASS |
| VIII. Unit Tests for Tokenization/Extraction | New unit tests planned for `custom_tokenizer_service` alongside existing tiktoken/PDF tests | PASS |
| IX. API Tests for Endpoints | New API tests planned for all 4 custom-tokenizer endpoints alongside existing ones, including the shared file-validation error cases and the three custom-tokenizer-specific error cases | PASS |
| X. Graceful Handling of Bad Input | Custom Tokenizer failure modes (invalid state, vocabulary init failure, malformed token data, missing session id) each map to a distinct error, same pattern as existing errors | PASS |
| XI. No Unnecessary Persistence | Vocabulary is in-memory only, no database introduced; explicit FR-011/FR-018 | PASS |
| XII. Local Dev / Simple Deployment | Still no orchestration; one more local process (`npm run dev`) replaces `streamlit run`, not in addition to it | PASS |
| XIII. Readable Code Over Abstraction | Custom Tokenizer split uses a plain character-scan loop (no regex dependency); one lock, one dict — no premature abstraction | PASS |
| XIV. Scope Discipline | No auth/accounts/DB/OCR/LLM/tokenizer-training added; matches spec's explicit exclusions | PASS |

No violations remain. Complexity Tracking below is retained for history
(the amendment that resolved it) rather than as an open justification.

## Streamlit → React Responsibilities (updated from feature 001)

**React frontend (replaces Streamlit) owns**:
- Rendering the tokenizer-mode selector, input-mode selector, text area/
  file uploader, encoding selector (Tiktokenizer mode only), Tokenize
  button, statistics tiles, token visualization, and — in Custom
  Tokenizer mode — the vocabulary panel/table/search/reset button.
- Generating and persisting a per-browser session id and sending it as
  `X-Session-Id` on every Custom Tokenizer request.
- Calling the backend over HTTP (`fetch`) and rendering its responses/
  errors; preserving entered input but clearing displayed results when
  the tokenizer mode is switched (clarified 2026-09-16).
- Never computing tokens, splitting text, or touching any vocabulary
  itself — purely a rendering/HTTP client layer, exactly as Streamlit was.

**FastAPI backend owns** (unchanged responsibilities, extended scope):
- Everything it already owned for Tiktokenizer (now also returning
  `token_bytes`).
- The entire Custom Tokenizer engine: vocabulary initialization, the
  deterministic split algorithm, case-insensitive word lookup, ID
  assignment, frequency updates, new-token detection, per-session
  isolation, and reset — via a dedicated `CustomTokenizerService`
  (`backend/app/services/custom_tokenizer_service.py`), structurally
  parallel to and independent from the existing tiktoken logic in
  `backend/app/services/tokenizer_service.py` (not renamed — "Tiktoken
  service" here refers to that existing module by role, not a new name).

## Project Structure

### Documentation (this feature)

```text
specs/002-react-custom-tokenizer/
├── plan.md                        # This file
├── research.md                    # Phase 0 output
├── data-model.md                  # Phase 1 output
├── quickstart.md                  # Phase 1 output
└── contracts/
    ├── tiktokenizer-api.md        # Updated existing contract (token_bytes)
    └── custom-tokenizer-api.md    # New contract
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── main.py                          # unchanged, registers both routers
│   ├── api/
│   │   ├── tokenize_routes.py           # existing; Token schema gains token_bytes
│   │   └── custom_tokenizer_routes.py   # NEW: 4 endpoints
│   ├── schemas/
│   │   ├── tokenize.py                  # existing; Token += token_bytes
│   │   └── custom_tokenizer.py          # NEW: VocabularyEntry, CustomToken,
│   │                                    #      CustomTokenizeRequest,
│   │                                    #      CustomTokenizationResult,
│   │                                    #      VocabularyResponse, ResetResponse
│   ├── services/
│   │   ├── tokenizer_service.py         # existing (may be read as "TiktokenService");
│   │   │                                #   extended to emit token_bytes
│   │   ├── pdf_service.py               # unchanged, reused by both tokenizer modes
│   │   ├── validation.py                # unchanged, reused by both tokenizer modes
│   │   └── custom_tokenizer_service.py  # NEW: CustomTokenizerService
│   └── core/
│       ├── config.py                    # unchanged
│       ├── errors.py                    # + InvalidTokenizerStateError,
│       │                                #   VocabularyInitError, MissingSessionIdError
│       └── session_store.py             # NEW: SessionVocabularyStore (dict + lock)
└── tests/
    ├── unit/
    │   ├── test_tokenizer_service.py         # extended for token_bytes
    │   ├── test_pdf_service.py               # unchanged
    │   └── test_custom_tokenizer_service.py  # NEW
    ├── api/
    │   ├── test_tokenize_routes.py            # extended for token_bytes
    │   └── test_custom_tokenizer_routes.py    # NEW
    └── integration/
        └── test_user_stories.py               # extended with Custom Tokenizer flows

frontend/                            # REPLACES the Streamlit app.py/api_client.py
├── package.json
├── tsconfig.json
├── vite.config.ts
├── index.html
├── .env.local.example
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── api/
    │   └── client.ts                # fetch wrappers for all 6 backend endpoints
    ├── types/
    │   └── api.ts                   # TS types mirroring the Pydantic schemas
    ├── hooks/
    │   ├── useSessionId.ts
    │   └── useTokenize.ts
    └── components/
        ├── Header.tsx
        ├── TokenizerModeSelector.tsx
        ├── InputModeSelector.tsx
        ├── TextInput.tsx
        ├── FileUploader.tsx
        ├── EncodingSelector.tsx
        ├── TokenizeButton.tsx
        ├── StatisticsPanel.tsx
        ├── TokenVisualization.tsx
        ├── TokenCard.tsx
        ├── VocabularyPanel.tsx
        ├── VocabularyTable.tsx
        ├── VocabularySearch.tsx
        ├── ResetVocabularyButton.tsx
        ├── ErrorMessage.tsx
        └── LoadingState.tsx
    (each component paired with a co-located `*.test.tsx`)
```

**Structure Decision**: Keep the existing `backend/` and `frontend/`
top-level split (constitution Principles I–III). Inside `backend/`, the
Custom Tokenizer gets its own service/schema/routes files parallel to the
existing tiktoken ones (constitution Principle XIII: no shared abstraction
forced between two genuinely different tokenizers). `frontend/` is
rebuilt from scratch as a small React app with one component per concern
listed in the spec (FR-driven, per the request's explicit component list)
— no `pages/` directory or router is introduced since this remains a
single-page tool.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| Principle II names "Streamlit" specifically, but this feature removes Streamlit | The user's explicit, clarified requirement is to replace Streamlit with a React + TypeScript SPA for a modern, component-based UI | Keeping Streamlit would directly contradict the feature's core, clarified ask; there is no simpler alternative that satisfies the request |
| Principle V forbids any tokenizer other than tiktoken without a constitution amendment | The user's explicit, clarified requirement is an independent, educational Custom Tokenizer alongside tiktoken, with its own vocabulary that never touches tiktoken | Implementing "Custom Tokenizer" as a thin wrapper around tiktoken (to technically avoid a second engine) would misrepresent the feature and violate the spec's explicit "Important Distinction" (FR-005) that the two must remain independent |

**Resolution path**: both rows above are pre-existing-principle conflicts
with a fully clarified, deliberate feature request, not accidental scope
creep. They are recorded here per the constitution's Governance clause and
should be closed out by running `/speckit-constitution` right after this
plan to amend Principle II (frontend technology → React/TypeScript) and
Principle V (scope tiktoken's "single source of truth" claim to
Tiktokenizer mode specifically, while still forbidding a *third* tokenizer
without further amendment).
