---

description: "Task list for React Frontend with Dual Tokenizer Modes"
---

# Tasks: React Frontend with Dual Tokenizer Modes

**Input**: Design documents from `/specs/002-react-custom-tokenizer/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

**Tests**: Included — constitution Principles VIII/IX require backend unit/API tests, and the spec's own Testing section (§20) explicitly requests frontend component tests and additional backend test coverage for the custom tokenizer.

**Organization**: Tasks are grouped by user story (from spec.md) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- File paths are exact and relative to the repository root

## Path Conventions

Per plan.md's "Structure Decision":
- Backend: `backend/app/...`, `backend/tests/...` (extends the existing feature-001 layout)
- Frontend: `frontend/...` (fully replaces the Streamlit app from feature 001)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Remove the old Streamlit frontend and scaffold the new React + TypeScript project

- [X] T001 Delete the Streamlit frontend: remove `frontend/app.py`, `frontend/api_client.py`, `frontend/requirements.txt`
- [X] T002 Scaffold the new React + TypeScript + Vite project in `frontend/`: `package.json` (react, react-dom, typescript, vite, @vitejs/plugin-react as dependencies), `tsconfig.json`, `vite.config.ts`, `index.html`, empty `frontend/src/main.tsx` and `frontend/src/App.tsx` placeholders
- [X] T003 [P] Add frontend test tooling to `frontend/package.json` and `frontend/vite.config.ts`: `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `jsdom`, plus a `frontend/src/setupTests.ts` importing `@testing-library/jest-dom`
- [X] T004 [P] Create `frontend/.env.local.example` documenting `VITE_TOKENIZER_API_URL=http://localhost:8000`

**Checkpoint**: Old Streamlit app removed; new frontend project builds and runs empty.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared backend types/infrastructure and frontend app shell that every user story depends on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 [P] Create `backend/app/schemas/custom_tokenizer.py` with Pydantic models: `VocabularyEntry` (token_id, token_text, frequency, status), `CustomToken` (index, token_id, token_text, is_new), `CustomTokenizeRequest` (text), `CustomTokenizationResult` (text, tokens, token_count, character_count, word_count, tokens_per_word, tokens_per_character, vocabulary_size, new_token_count, vocabulary), `VocabularyResponse` (vocabulary, vocabulary_size), `ResetResponse` (vocabulary, vocabulary_size) — per data-model.md
- [X] T006 Add domain exceptions to `backend/app/core/errors.py`: `MissingSessionIdError` (400, `missing_session_id`), `InvalidTokenizerStateError` (400, `invalid_tokenizer_state`), `VocabularyInitError` (500, `vocabulary_init_error`), `MalformedTokenDataError` (400, `malformed_token_data`) — following the existing `TokenizerError` subclass pattern so they're automatically handled by `register_exception_handlers`
- [X] T007 Create `backend/app/core/session_store.py` with a `SessionVocabularyStore` class: an in-memory `dict[str, list[VocabularyEntry]]` (plus per-entry frequency state) guarded by one `threading.Lock`, exposing `get_or_create(session_id) -> vocabulary`, `update(session_id, vocabulary)`, and `reset(session_id) -> vocabulary` (restores the seed vocabulary); define the fixed seed vocabulary here (e.g. `<UNK>`=0, `hello`=1, `world`=2, each starting at frequency 0)
- [X] T008 [P] Create `frontend/src/types/api.ts` with TypeScript interfaces mirroring every backend schema: `Token` (incl. `token_bytes: number[]`), `TokenStatistics`, `TokenizationResult`, `SupportedEncoding`, `SourceType`, `VocabularyEntry`, `CustomToken`, `CustomTokenizationResult`, `VocabularyResponse`, `ResetResponse`, `ApiErrorResponse`
- [X] T009 [P] Create `frontend/src/api/client.ts` with a base `fetch` helper (reads `import.meta.env.VITE_TOKENIZER_API_URL`, parses `ApiErrorResponse` on non-OK responses) and a `getEncodings()` call to `GET /api/v1/encodings`
- [X] T010 [P] Create `frontend/src/hooks/useSessionId.ts`: on first use, reads a session id from `localStorage`, or generates one with `crypto.randomUUID()` and persists it; returns the stable id for the component tree's lifetime
- [X] T011 [P] Create `frontend/src/components/Header.tsx` (renders the "TokenLab" title and "Explore how text becomes tokens" tagline)
- [X] T012 [P] Create `frontend/src/components/ErrorMessage.tsx` (renders an `error_code`/`detail` pair as a styled inline error banner)
- [X] T013 [P] Create `frontend/src/components/LoadingState.tsx` (renders a simple loading indicator, shown while a tokenize/reset request is in flight)
- [X] T014 Create `frontend/src/App.tsx` skeleton wiring `useSessionId`, rendering `Header`, and holding top-level state placeholders for tokenizer mode, input mode, and results (no tokenizer-specific UI yet); update `frontend/src/main.tsx` to mount it

**Checkpoint**: Foundation ready — user story implementation can now begin.

---

## Phase 3: User Story 1 - Tiktokenizer on the New Interface (Priority: P1) 🎯 MVP

**Goal**: A user can tokenize pasted text or an uploaded `.txt`/`.pdf` file with a tiktoken encoding through the new React interface, with full parity (plus a new `token_bytes` field) to the previous Streamlit behavior.

**Independent Test**: Open the app (Tiktokenizer is the default mode), tokenize pasted text and a file upload, and confirm results match the previous application's behavior with the added byte representation.

### Tests for User Story 1 ⚠️

- [X] T015 [P] [US1] Extend `backend/tests/unit/test_tokenizer_service.py`: assert each returned `Token` includes a `token_bytes` list of ints whose decoded bytes match `decoded_text`'s UTF-8 encoding
- [X] T016 [P] [US1] Extend `backend/tests/api/test_tokenize_routes.py`: assert `POST /api/v1/tokenize/text` and `.../tokenize/file` responses include `token_bytes` on every token
- [X] T017 [P] [US1] Create `frontend/src/components/TokenCard.test.tsx`: renders a token's index/ID/decoded text/bytes correctly
- [X] T018 [P] [US1] Create `frontend/src/components/TokenVisualization.test.tsx`: renders one `TokenCard` per token with no cap, given a list of tokens
- [X] T019 [P] [US1] Create `frontend/src/components/StatisticsPanel.test.tsx`: renders character/word/token counts and the two ratios correctly

### Implementation for User Story 1

- [X] T020 [US1] Add `token_bytes: list[int]` to the `Token` model in `backend/app/schemas/tokenize.py`
- [X] T021 [US1] Update `backend/app/services/tokenizer_service.py` to populate `token_bytes=list(enc.decode_single_token_bytes(token_id))` for every token
- [X] T022 [P] [US1] Create `frontend/src/components/TokenizerModeSelector.tsx` (segmented control: "Tiktokenizer" / "Custom Tokenizer"; calls a parent-provided `onChange`)
- [X] T023 [P] [US1] Create `frontend/src/components/InputModeSelector.tsx` (tabs: "Text" / "TXT" / "PDF"; calls a parent-provided `onChange`)
- [X] T024 [P] [US1] Create `frontend/src/components/TextInput.tsx` (large multiline, editable textarea bound to a controlled value)
- [X] T025 [P] [US1] Create `frontend/src/components/FileUploader.tsx` (file input restricted via an `accept` prop, e.g. `.txt` or `.pdf`)
- [X] T026 [P] [US1] Create `frontend/src/components/EncodingSelector.tsx` (dropdown populated by `getEncodings()`, only rendered by the parent in Tiktokenizer mode)
- [X] T027 [P] [US1] Create `frontend/src/components/TokenizeButton.tsx` (button; disabled while a `loading` prop is true)
- [X] T028 [US1] Add `tokenizeText(text, encoding)` and `tokenizeFile(fileBytes, filename, encoding)` to `frontend/src/api/client.ts`, calling `POST /api/v1/tokenize/text` and `POST /api/v1/tokenize/file`
- [X] T029 [P] [US1] Create `frontend/src/components/StatisticsPanel.tsx` (renders character/word/token counts and tokens-per-word/tokens-per-character tiles from a stats object)
- [X] T030 [P] [US1] Create `frontend/src/components/TokenCard.tsx` (renders one token's index, ID, decoded text, and byte array)
- [X] T031 [US1] Create `frontend/src/components/TokenVisualization.tsx` (renders one `TokenCard` per token in `tokens`, no cap or truncation)
- [X] T032 [US1] Wire the Tiktokenizer flow end-to-end in `frontend/src/App.tsx`: mode/input-mode state, `EncodingSelector` shown only in Tiktokenizer mode, `TokenizeButton` calling `tokenizeText`/`tokenizeFile`, rendering `LoadingState`/`ErrorMessage`/`StatisticsPanel`/`TokenVisualization` based on request state. Structure the `results` state so that changing the tokenizer-mode state clears it (see T042/T065 for where the second mode makes this observable) while the `text`/`file` input state is a separate piece of state untouched by mode changes (FR-002)

**Checkpoint**: User Story 1 is fully functional and independently testable — Tiktokenizer works end-to-end on the new interface.

---

## Phase 4: User Story 2 - Tokenize with the Custom Tokenizer (Priority: P2)

**Goal**: A user can switch to Custom Tokenizer mode and tokenize text, seeing each token correctly marked as new or existing, with deterministic, case-insensitive, session-isolated vocabulary growth.

**Independent Test**: Switch to Custom Tokenizer mode, tokenize text with known and brand-new words, and confirm new/existing labeling, ID stability across repeats, and that a different session id doesn't see this session's new tokens.

### Tests for User Story 2 ⚠️

- [X] T033 [P] [US2] Create `backend/tests/unit/test_custom_tokenizer_service.py`: seed vocabulary contents and IDs; known-token lookup reuses its ID and increments frequency; an unseen token is assigned the next sequential ID, added with frequency 1, and marked new; repeating the same input a second time yields zero new tokens and the same IDs; case-insensitive matching (`"Hello"` and `"hello"` resolve to one entry, stored text is first-seen casing); the split rule on `"Hello, world! 123"` produces the documented word/punctuation/whitespace/number units; splitting on Unicode text (e.g. accented or non-Latin letters) groups letters correctly; vocabulary reset restores the exact seed state
- [X] T034 [P] [US2] Create `backend/tests/api/test_custom_tokenizer_routes.py`: `POST /api/v1/custom-tokenizer/tokenize/text` returns 200 with correct `is_new` flags and `new_token_count`; missing `X-Session-Id` header returns 400 `missing_session_id`; empty text returns 400 `empty_input`; two different `X-Session-Id` values produce independent vocabularies (session isolation)
- [X] T035 [P] [US2] Create `frontend/src/components/TokenCard.test.tsx` additions (or a dedicated variant test) verifying a token rendered with `isNew=true` is visually distinguished (e.g., a distinct class/badge) from `isNew=false`

### Implementation for User Story 2

- [X] T036 [US2] Create `backend/app/services/custom_tokenizer_service.py` with a `CustomTokenizerService`: `split(text) -> list[str]` (the deterministic character-scan algorithm from research.md — maximal runs of `isspace()`/`isalpha()`/`isdigit()` characters, every other character as its own token), and `tokenize(session_id, text) -> CustomTokenizationResult` (uses `SessionVocabularyStore.get_or_create`, does a case-insensitive lookup for word tokens, creates new entries with the next sequential ID and frequency 1, increments frequency and marks `is_new=False` for existing entries, builds and returns the full result including the vocabulary snapshot)
- [X] T037 [US2] Create `backend/app/api/custom_tokenizer_routes.py` with a router requiring an `X-Session-Id` header (raise `MissingSessionIdError` if absent/empty) and `POST /tokenize/text` declared with `response_model=CustomTokenizationResult`: validate non-empty text and upload size via the existing `validation` module, then call `CustomTokenizerService.tokenize` (constitution Principle VII)
- [X] T038 [US2] Register the custom-tokenizer router in `backend/app/main.py`
- [X] T039 [US2] Add `customTokenizeText(text, sessionId)` to `frontend/src/api/client.ts`, posting JSON to `POST /api/v1/custom-tokenizer/tokenize/text` with an `X-Session-Id` header
- [X] T040 [US2] Update `frontend/src/components/TokenCard.tsx` to accept an optional `isNew` prop and render a visually distinct "NEW" badge/style when true
- [X] T041 [US2] Update `frontend/src/components/TokenVisualization.tsx` to pass each `CustomToken`'s `is_new` flag through to `TokenCard` when rendering Custom Tokenizer results
- [X] T042 [US2] Update `frontend/src/App.tsx`: in Custom Tokenizer mode, hide `EncodingSelector`, call `customTokenizeText` (and, once available, the file variant) instead of the tiktoken calls, and pass `is_new` info into `TokenVisualization`. Add the `onChange` handler passed to `TokenizerModeSelector` (T022) so that selecting a different mode clears the `results` state from T032 while leaving the current text/file input value in place (FR-002, clarified 2026-09-16)
- [X] T043 [US2] Update `frontend/src/components/StatisticsPanel.tsx` to additionally render "Vocabulary" (size) and "New Tokens" tiles when given Custom Tokenizer statistics

**Checkpoint**: User Stories 1 and 2 both work independently — Custom Tokenizer core tokenize-and-distinguish behavior is live.

---

## Phase 5: User Story 3 - View and Search the Live Vocabulary (Priority: P3)

**Goal**: While in Custom Tokenizer mode, a user can see the full current vocabulary (updating live) and search it by token text; file-upload input also works for the Custom Tokenizer.

**Independent Test**: Tokenize in Custom Tokenizer mode and confirm the vocabulary panel lists every entry and refreshes immediately after each tokenization; confirm searching filters the list.

### Tests for User Story 3 ⚠️

- [X] T044 [P] [US3] Extend `backend/tests/api/test_custom_tokenizer_routes.py`: `GET /api/v1/custom-tokenizer/vocabulary` auto-creates and returns the seed vocabulary for a never-seen `X-Session-Id`, and reflects prior tokenizations for a known one; `POST /api/v1/custom-tokenizer/tokenize/file` with a `.txt` upload tokenizes the extracted text with the Custom Tokenizer; **and**, per FR-016 ("all existing error cases... regardless of which tokenizer mode is active"), also test that this same endpoint returns 400 `unsupported_file_type` for a non-`.txt`/`.pdf` file, 400 `invalid_pdf` for a corrupted PDF, 400 `no_extractable_text` for a text-less PDF, and 413 `upload_too_large` for an oversized file — mirroring `test_tokenize_routes.py`'s existing coverage of `POST /api/v1/tokenize/file`
- [X] T045 [P] [US3] Create `frontend/src/components/VocabularyTable.test.tsx`: renders ID/Token/Frequency/Status columns for a given vocabulary list
- [X] T046 [P] [US3] Create `frontend/src/components/VocabularySearch.test.tsx`: filters a vocabulary list by a case-insensitive text match on token text

### Implementation for User Story 3

- [X] T047 [US3] Add `GET /vocabulary` to `backend/app/api/custom_tokenizer_routes.py`, declared with `response_model=VocabularyResponse` (constitution Principle VII), returning it via `SessionVocabularyStore.get_or_create`
- [X] T048 [US3] Add `POST /tokenize/file` to `backend/app/api/custom_tokenizer_routes.py`, declared with `response_model=CustomTokenizationResult` (constitution Principle VII): accept a multipart file, reuse `validation.validate_upload_size`/`validate_file_extension`/`decode_text_file_content`/`pdf_service.extract_text` (same pattern as the Tiktokenizer file endpoint) to obtain text, then call `CustomTokenizerService.tokenize`
- [X] T049 [US3] Add `customTokenizeFile(fileBytes, filename, sessionId)` and `getVocabulary(sessionId)` to `frontend/src/api/client.ts`
- [X] T050 [P] [US3] Create `frontend/src/components/VocabularyTable.tsx` (renders ID/Token/Frequency/Status rows for a given, already-filtered vocabulary array)
- [X] T051 [P] [US3] Create `frontend/src/components/VocabularySearch.tsx` (a text input that filters a vocabulary array by token text, case-insensitive, and renders `VocabularyTable` with the filtered result)
- [X] T052 [US3] Create `frontend/src/components/VocabularyPanel.tsx` (container: holds/fetches the vocabulary via `getVocabulary`, renders `VocabularySearch` + `VocabularyTable`; exposes a method/prop to refresh after a tokenization)
- [X] T053 [US3] Wire `VocabularyPanel` into `frontend/src/App.tsx`: rendered only in Custom Tokenizer mode, fetched on first switch to that mode, and refreshed after every successful custom tokenization

**Checkpoint**: User Stories 1–3 all work independently — vocabulary is visible, searchable, and always current.

---

## Phase 6: User Story 4 - Reset the Custom Vocabulary (Priority: P4)

**Goal**: A user can reset their session's custom vocabulary back to exactly its initial state, with a confirmation step.

**Independent Test**: Grow the vocabulary via a few tokenizations, reset it, and confirm it returns to exactly the initial entries/frequencies/size.

### Tests for User Story 4 ⚠️

- [X] T054 [P] [US4] Extend `backend/tests/api/test_custom_tokenizer_routes.py`: for a session with a grown vocabulary, `POST /api/v1/custom-tokenizer/reset` returns the exact seed vocabulary and size, and a subsequent `GET /vocabulary` confirms the reset persisted
- [X] T055 [P] [US4] Create `frontend/src/components/ResetVocabularyButton.test.tsx`: clicking shows a confirmation step; canceling triggers no reset call; confirming calls the provided reset handler

### Implementation for User Story 4

- [X] T056 [US4] Add `reset(session_id)` to `backend/app/services/custom_tokenizer_service.py` (delegates to `SessionVocabularyStore.reset`)
- [X] T057 [US4] Add `POST /reset` to `backend/app/api/custom_tokenizer_routes.py`, declared with `response_model=ResetResponse` (constitution Principle VII)
- [X] T058 [US4] Add `resetVocabulary(sessionId)` to `frontend/src/api/client.ts`, calling `POST /api/v1/custom-tokenizer/reset`
- [X] T059 [US4] Create `frontend/src/components/ResetVocabularyButton.tsx` (renders a button that shows an inline/native confirmation before calling a parent-provided `onConfirm`)
- [X] T060 [US4] Wire `ResetVocabularyButton` into `frontend/src/components/VocabularyPanel.tsx`, calling `resetVocabulary` and refreshing the displayed vocabulary on confirm

### Additional coverage for User Story 2 (added post-`/speckit-analyze`)

- [X] T065 [US2] Create `frontend/src/App.test.tsx` covering FR-002's mode-switch behavior: render `App`, tokenize in Tiktokenizer mode to produce a result, switch to Custom Tokenizer mode, and assert the previously entered text is still present in `TextInput` while the previous result is no longer rendered
- [X] T066 [US2] Give FR-017's three error conditions real triggers: in `backend/app/core/session_store.py`, wrap the seed-vocabulary construction in `get_or_create` in a try/except that raises `VocabularyInitError` on failure; in `backend/app/services/custom_tokenizer_service.py`, add a `_check_vocabulary_integrity(vocabulary)` guard — called at the start of `tokenize()` and `reset()` — that raises `InvalidTokenizerStateError` if the vocabulary contains duplicate `token_id` values or a non-monotonic next-ID, and raises `MalformedTokenDataError` if any entry's `token_id`/`token_text`/`frequency` has the wrong type or a `token_text` that is empty
- [X] T067 [P] [US2] Add unit tests to `backend/tests/unit/test_custom_tokenizer_service.py` for the three T066 guards: construct a vocabulary with a duplicate `token_id` and assert `tokenize()` raises `InvalidTokenizerStateError`; construct a vocabulary entry with a malformed field (e.g. `token_id` as a string) and assert `MalformedTokenDataError`; monkeypatch the seed-vocabulary constructor to raise, and assert `SessionVocabularyStore.get_or_create` raises `VocabularyInitError`
- [X] T068 [P] [US2] Add an API test to `backend/tests/api/test_custom_tokenizer_routes.py` asserting that when `CustomTokenizerService.tokenize` raises `InvalidTokenizerStateError`, `POST /api/v1/custom-tokenizer/tokenize/text` returns 400 with `error_code: "invalid_tokenizer_state"` (inject the failure the same way T067 does, via a corrupted vocabulary for a test session id)

**Checkpoint**: All four user stories are independently functional, and FR-002/FR-016/FR-017's previously-undertested behaviors now have explicit coverage.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that span multiple user stories

- [X] T061 [P] Extend `backend/tests/integration/test_user_stories.py` with a Custom Tokenizer end-to-end flow (tokenize introducing a new word → vocabulary reflects it → reset restores the seed state) and a session-isolation check using two different `X-Session-Id` values
- [X] T062 [P] Rewrite the root `README.md`'s frontend section to describe running the new React app (`cd frontend && npm install && npm run dev`) in place of the removed `streamlit run` instructions
- [X] T063 Manually run every scenario in [quickstart.md](./quickstart.md) (curl commands and the React UI) and confirm actual behavior matches expected results
- [X] T064 [P] Review every new `error_code`/`detail` message (`missing_session_id`, `invalid_tokenizer_state`, `vocabulary_init_error`, `malformed_token_data`) across `backend/app/core/errors.py` and `backend/app/api/custom_tokenizer_routes.py` for clarity and consistency (FR-017)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately.
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories.
- **User Story 1 (Phase 3)**: Depends only on Foundational.
- **User Story 2 (Phase 4)**: Depends on Foundational; reuses US1's input/mode-selector components and `App.tsx` scaffolding, so implement after US1.
- **User Story 3 (Phase 5)**: Depends on Foundational and US2 (extends the same custom-tokenizer router/service and needs `is_new`/vocabulary concepts already in place).
- **User Story 4 (Phase 6)**: Depends on Foundational and US2/US3 (resets the vocabulary US2 grows and US3 displays).
- **Polish (Phase 7)**: Depends on all four user stories being complete.

### Within Each User Story

- Tests are written first and should fail before their corresponding implementation tasks.
- Backend schema/service/error work before backend routes; backend routes before frontend API-client wiring; frontend leaf components before the `App.tsx` wiring that composes them.

### Parallel Opportunities

- T003, T004 (Setup).
- T005, T008, T009, T010, T011, T012, T013 (Foundational) — different files, no interdependencies.
- T015–T019 (US1 tests) — different files.
- T022–T027, T029, T030 (US1 leaf components) — different files.
- T033–T035 (US2 tests); T044–T046 (US3 tests); T054–T055 (US4 tests); T067, T068 (US2 error-path tests, once T066 lands).
- T050, T051 (US3 leaf components).

---

## Parallel Example: User Story 2

```bash
# Tests for User Story 2 together:
Task: "Unit tests for CustomTokenizerService in backend/tests/unit/test_custom_tokenizer_service.py"
Task: "API tests for custom-tokenizer routes in backend/tests/api/test_custom_tokenizer_routes.py"
Task: "TokenCard new/existing rendering test in frontend/src/components/TokenCard.test.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (remove Streamlit, scaffold React app)
2. Complete Phase 2: Foundational (blocks everything else)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: run T015–T019, then manually exercise the Tiktokenizer flow per quickstart.md
5. This is a demonstrable MVP: the application works end-to-end on the new React frontend, with full Tiktokenizer parity plus token bytes.

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. Add User Story 1 → validate independently → demo (MVP: React frontend + Tiktokenizer)
3. Add User Story 2 → validate independently → demo (Custom Tokenizer core behavior)
4. Add User Story 3 → validate independently → demo (vocabulary view/search)
5. Add User Story 4 → validate independently → demo (reset)
6. Phase 7 polish once all four stories are in place

## Notes

- [P] tasks touch different files and have no unmet dependencies.
- Tests are included per constitution Principles VIII/IX and the spec's explicit Testing section (§20) — write them before their implementation task and confirm they fail first.
- Every task lists an exact file path so it is directly actionable.
- Recall the constitution conflicts flagged in plan.md (Streamlit removal, tiktoken-exclusivity) — running `/speckit-constitution` to ratify v2.0.0 is a recommended parallel action, not itself a task here.

---

## Phase 8: Convergence

- [X] T069 CRITICAL: Add `CORSMiddleware` to `backend/app/main.py` allowing the frontend's dev origin (e.g. `http://localhost:5173`, ideally read from an environment variable with that as the default) for methods `GET`/`POST` and headers including `Content-Type` and `X-Session-Id`; add an API test asserting an `OPTIONS` preflight to a custom-tokenizer endpoint from that origin returns the correct `Access-Control-Allow-Origin`/`-Methods`/`-Headers` response instead of today's 405, per plan.md's REST/HTTP frontend-backend communication architecture (missing)
- [X] T070 Fix the concurrency race in `CustomTokenizerService.tokenize()` (`backend/app/services/custom_tokenizer_service.py`): the read-modify-write cycle on a session's vocabulary (`SessionVocabularyStore.get_or_create` → mutate the returned list → `SessionVocabularyStore.update`) currently runs outside the store's lock, so concurrent requests for the same session can race. Add a lock-protected mutation path on `SessionVocabularyStore` (e.g. a `mutate(session_id, fn)` method or context manager that holds the lock for the whole cycle) and use it in `tokenize()`; add a test that fires concurrent `tokenize()` calls for the same new word in the same session and asserts exactly one resulting vocabulary entry with no duplicate IDs, per spec.md Edge Cases (contradicts)
