# Research: React Frontend with Dual Tokenizer Modes

**Feature**: [spec.md](./spec.md) | **Date**: 2026-09-16

## Constitution Conflict (must be resolved via amendment, not silently ignored)

- **Finding**: The current constitution (v1.0.0) fixes the frontend as
  Streamlit (Principle II, Technology Stack) and declares tiktoken the
  single source of truth with "No alternative or custom tokenizers MUST be
  introduced without amending this constitution" (Principle V). This
  feature's explicit, clarified intent is to replace Streamlit with React
  and add an independent Custom Tokenizer.
- **Decision**: Proceed with this plan against the feature's clarified
  intent, but flag both conflicts explicitly in the Constitution Check
  below and in Complexity Tracking, and recommend running
  `/speckit-constitution` immediately after this plan to ratify a v2.0.0
  amendment (frontend → React/TypeScript, Principle V scoped to "tiktoken
  is the sole engine for Tiktokenizer mode" rather than the only tokenizer
  in the application). This plan does not itself edit the constitution —
  that is out of scope for `/speckit-plan`.
- **Rationale**: The spec went through full `/speckit-clarify`; the
  request is unambiguous and deliberate, not an accidental scope creep.
  Blocking planning on the amendment first would just delay the same work;
  documenting the conflict transparently and completing the amendment
  right after keeps governance honest without stalling delivery.
- **Alternatives considered**: Silently treating the constitution as
  already amended (rejected — hides a real governance gap); refusing to
  plan until the constitution is amended first (rejected — the amendment's
  content is fully determined by this already-clarified spec, so
  sequencing it first adds a round-trip with no new information).

## Frontend Framework & Tooling

- **Decision**: React 18 + TypeScript, built with Vite; component-level
  tests with Vitest + React Testing Library.
- **Rationale**: Vite gives a fast dev server and simple `npm run build`
  for a static SPA with no server-side rendering needs — matching the
  "simple local dev, simple deployment" goal that previously applied to
  Streamlit. React + TypeScript is what the request explicitly mandates.
- **Alternatives considered**: Next.js (rejected — SSR/routing/server
  features are unneeded for a single-page tool with one backend); Create
  React App (rejected — unmaintained/deprecated tooling); plain
  React without TypeScript (rejected — TypeScript is explicitly mandated
  and catches API-shape mismatches with the Pydantic contracts at compile
  time).

## Frontend State Management

- **Decision**: Plain React state (`useState`/`useEffect`) plus a few small
  custom hooks (`useSessionId`, `useTokenize`); no external state library.
- **Rationale**: The app has a handful of interdependent pieces of state
  (mode, input, results, vocabulary) confined to one page — introducing
  Redux/Zustand/Context-heavy architecture would be complexity the app
  doesn't need (mirrors constitution Principle XIII's intent, applied to
  the new frontend).
- **Alternatives considered**: Redux Toolkit, Zustand (rejected — over-
  engineered for a single-page tool with no cross-page shared state).

## Session Identification for the Custom Tokenizer

- **Decision**: The frontend generates a UUID with `crypto.randomUUID()`
  the first time it loads, persists it in `localStorage`, and sends it as
  an `X-Session-Id` header on every Custom Tokenizer request. The backend
  keeps one in-memory vocabulary per session id in a process-wide
  dictionary guarded by a single `threading.Lock`, auto-creating a fresh
  seeded vocabulary the first time an id is seen.
- **Rationale**: Satisfies the spec's session-isolation requirement
  (FR-010) without cookies, accounts, or a database. A single lock is
  sufficient given this app's expected concurrency (a handful of local
  users at most) and keeps the implementation readable (Principle XIII).
- **Alternatives considered**: Server-set cookies (rejected — adds
  cross-origin cookie complexity when frontend/backend run on different
  ports in local dev, for no added benefit over a header); per-session
  locks keyed by id (rejected as premature optimization — a single lock
  guarding brief in-memory dict operations is not a bottleneck at this
  scale).

## Custom Tokenizer Split Algorithm

- **Decision**: Deterministic, single left-to-right scan over the input
  string. At each position, classify the character using Python's
  Unicode-aware `str.isspace()` / `str.isalpha()` / `str.isdigit()`:
  - A maximal run of `isspace()` characters → one "whitespace" token.
  - A maximal run of `isalpha()` characters → one "word" token.
  - A maximal run of `isdigit()` characters → one "number" token.
  - Any other character (punctuation/symbol) → its own single-character
    token (never grouped with adjacent punctuation).
  Word-token vocabulary lookups are case-insensitive (lowercased key);
  the vocabulary stores each entry's first-seen casing as its display
  text.
- **Rationale**: Implements FR-007/FR-008 exactly, using only the standard
  library (no regex dependency needed), is trivially deterministic, and is
  Unicode-aware by virtue of Python's built-in string methods, satisfying
  the spec's Unicode assumption without extra dependencies.
- **Alternatives considered**: A regex-based splitter (rejected — the
  `\p{L}` Unicode-letter class needs the third-party `regex` package since
  stdlib `re` doesn't support it; the character-scan approach needs no
  extra dependency and is equally deterministic).

## Custom Tokenizer API Shape

- **Decision**: Mirror the existing Tiktokenizer endpoint split for
  consistency: `POST /api/v1/custom-tokenizer/tokenize/text` and
  `POST /api/v1/custom-tokenizer/tokenize/file`, plus
  `GET /api/v1/custom-tokenizer/vocabulary` and
  `POST /api/v1/custom-tokenizer/reset`. All four require the
  `X-Session-Id` header.
- **Rationale**: The request's suggested single `POST .../tokenize`
  endpoint would need to multiplex JSON-body and multipart-file requests
  on one route, which FastAPI does not do cleanly; splitting by input type
  (as the existing Tiktokenizer endpoints already do) keeps the two
  tokenizer APIs symmetric and equally simple. The request explicitly
  allows the final API structure to be decided during planning.
- **Alternatives considered**: A single combined endpoint accepting either
  JSON or multipart (rejected — awkward FastAPI request-parsing, and
  breaks symmetry with the existing tiktoken endpoints).

## Extending the Tiktokenizer Result with Token Bytes

- **Decision**: Add a `token_bytes: list[int]` field to the existing
  `Token` schema, populated via
  `list(enc.decode_single_token_bytes(token_id))` (iterating a `bytes`
  object yields its integer byte values directly — no extra decoding
  step needed).
- **Rationale**: Directly satisfies FR-004's "token bytes where
  appropriate" with no new dependency and a one-line change to the
  existing `tokenizer_service.tokenize()` function.
- **Alternatives considered**: Base64/hex string encoding of the bytes
  (rejected — a plain integer array is simpler for the frontend to render
  and needs no encode/decode step on the TypeScript aside).

## Testing Approach (frontend)

- **Decision**: Vitest + React Testing Library for component/unit tests,
  mocking the backend API client module. No end-to-end browser test
  framework is introduced in this iteration.
- **Rationale**: Matches the backend's existing pattern of fast,
  dependency-light unit/API tests; a full e2e framework (Playwright/
  Cypress) would be new infrastructure not required by the spec's testing
  section, which asks for rendering/interaction/error/loading-state tests
  achievable at the component level.
- **Alternatives considered**: Playwright/Cypress e2e (rejected as
  out-of-proportion to this feature's scope; can be added later if
  needed, without amending this plan).
