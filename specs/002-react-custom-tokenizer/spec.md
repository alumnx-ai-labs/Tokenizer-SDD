# Feature Specification: React Frontend with Dual Tokenizer Modes

**Feature Branch**: `002-react-custom-tokenizer`

**Created**: 2026-09-16

**Status**: Draft

**Input**: User description: "Update the existing Tokenizer Application: replace the Streamlit frontend with a React + TypeScript frontend; add a tokenizer mode selector between the existing tiktoken-based tokenizer and a new, independent Custom Tokenizer with its own dynamically-growing, deterministic vocabulary; keep existing text/TXT/PDF input, validation, and error handling; no database, no auth."

## Clarifications

### Session 2026-09-16

- Q: Should the Custom Tokenizer treat two words that differ only in letter case (e.g., "Hello" vs "hello") as the same vocabulary token, or as two distinct tokens? → A: Case-insensitive — they map to the same vocabulary entry/ID, and frequency counts both.
- Q: As a session's custom vocabulary grows over a long-running conversation, should every tokenization response and the vocabulary view always include the complete vocabulary, or should there be a cap with pagination for very large vocabularies? → A: Always the full vocabulary, no cap — new tokens keep being added to the same complete list every time.
- Q: When a user switches between Tiktokenizer and Custom Tokenizer mode, should their already-entered text/file stay loaded, or should switching clear the input and results? → A: Keep the input loaded; clear only the previous mode's displayed results until "Tokenize" is pressed again.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Tokenize with Tiktokenizer on the New Interface (Priority: P1)

A user opens the redesigned application, provides text (typed, or via a
`.txt`/`.pdf` upload), selects a tiktoken encoding, and tokenizes it —
getting the same kind of detailed token breakdown and statistics the
application has always provided, now through a modern web interface instead
of the previous one.

**Why this priority**: This is the application's existing core value.
Nothing else in this update matters if this baseline capability breaks
during the interface rebuild — it must work exactly as before.

**Independent Test**: Can be fully tested by opening the app, leaving
Tiktokenizer selected (the default), tokenizing pasted text and a `.txt`/
`.pdf` upload, and confirming the results match what the previous interface
produced.

**Acceptance Scenarios**:

1. **Given** the app is open with Tiktokenizer mode selected by default,
   **When** the user pastes text, picks an encoding, and tokenizes,
   **Then** the system shows the total token count, every token (index, ID,
   decoded text, and byte representation), and character/word statistics.
2. **Given** Tiktokenizer mode, **When** the user uploads a valid `.txt` or
   text-based `.pdf` file instead of typing, **Then** the system extracts
   the text, displays it, and returns the same kind of token breakdown.
3. **Given** a result is displayed, **When** the user switches to a
   different encoding and re-tokenizes the same input, **Then** the results
   update to reflect the newly selected encoding.

---

### User Story 2 - Tokenize with the Custom Tokenizer (Priority: P2)

A user switches to Custom Tokenizer mode and tokenizes text, seeing which
resulting tokens were already known to the application's own vocabulary and
which ones are being seen — and added to that vocabulary — for the first
time.

**Why this priority**: This is the headline new capability of this update:
an independent, self-growing tokenizer that behaves differently from
Tiktokenizer and needs to be visibly distinct and correct to deliver its
educational purpose.

**Independent Test**: Can be fully tested by switching to Custom Tokenizer
mode, tokenizing text containing both previously-seeded and brand-new words,
and confirming each resulting token is correctly labeled new or existing and
that token IDs are stable across repeated runs.

**Acceptance Scenarios**:

1. **Given** Custom Tokenizer mode is selected, **When** the user tokenizes
   text containing only words already in the vocabulary, **Then** every
   resulting token is labeled "existing", no new tokens are reported, and
   each token's ID matches its known vocabulary ID.
2. **Given** Custom Tokenizer mode, **When** the user tokenizes text
   containing a word never seen before, **Then** that token is labeled
   "new", is assigned the next available token ID, and is added to the
   vocabulary with a starting frequency.
3. **Given** a token was just added as "new", **When** the user tokenizes
   the exact same text again, **Then** that token is now labeled "existing"
   with the same ID and an incremented frequency, and no new tokens are
   reported.
4. **Given** Custom Tokenizer mode, **When** the user tokenizes text made up
   of punctuation, numbers, and whitespace in addition to words, **Then**
   each of those units is split into its own token following the same
   documented, deterministic rule every time.
5. **Given** the user has been tokenizing in Custom Tokenizer mode,
   **When** the user switches to Tiktokenizer mode and back, **Then** the
   custom vocabulary built up so far is unchanged and still available, the
   previously entered input is still there, the prior results are cleared
   until re-tokenized, and at no point does anything suggest the tiktoken
   encoding itself changed.

---

### User Story 3 - View and Search the Live Vocabulary (Priority: P3)

While using Custom Tokenizer mode, a user views the full current vocabulary
— including tokens just added — and searches it to find a specific token.

**Why this priority**: Seeing the vocabulary grow is central to the
educational goal of the Custom Tokenizer; without a visible, searchable
vocabulary view, User Story 2's new/existing distinction has no persistent
place to be understood.

**Independent Test**: Can be fully tested by tokenizing text in Custom
Tokenizer mode and confirming the vocabulary view lists every token (ID,
text, frequency, status) and updates immediately after tokenizing again,
and that searching filters the list to matching tokens.

**Acceptance Scenarios**:

1. **Given** Custom Tokenizer mode is active, **When** the user views the
   vocabulary panel, **Then** it lists every vocabulary entry with its ID,
   token text, frequency, and status (initial, existing, or new-this-run).
2. **Given** a tokenization just added new tokens, **When** the vocabulary
   panel is viewed immediately afterward, **Then** the new tokens appear in
   the list without any manual refresh action.
3. **Given** the vocabulary contains many entries, **When** the user types
   into the vocabulary search field, **Then** only matching tokens remain
   visible.

---

### User Story 4 - Reset the Custom Vocabulary (Priority: P4)

A user who has grown the custom vocabulary during exploration wants to
start over, so they reset it back to its original, predefined state.

**Why this priority**: Useful for repeated experimentation, but the
application is fully usable without it, making it the lowest-priority
increment of this update.

**Independent Test**: Can be fully tested by growing the vocabulary with a
few tokenizations, resetting it, and confirming the vocabulary returns to
exactly its original entries, frequencies, and size.

**Acceptance Scenarios**:

1. **Given** the vocabulary has grown beyond its initial state, **When**
   the user activates "Reset Vocabulary" and confirms the action, **Then**
   the vocabulary returns to exactly its initial entries and frequencies,
   and the vocabulary size statistic matches the initial count.
2. **Given** the user activates "Reset Vocabulary", **When** the
   confirmation prompt appears, **Then** the user can cancel without any
   change to the vocabulary.

---

### Edge Cases

- What happens when the user requests tokenization without selecting a
  tiktoken encoding, or selects one outside the four supported options?
  → The system MUST reject the request and identify the valid options
  (unchanged from prior behavior).
- What happens when text (typed or extracted) is empty or whitespace-only,
  in either tokenizer mode? → The system MUST reject the request and state
  that text is required.
- What happens when an uploaded file has an unsupported extension, or its
  content doesn't actually match a supported type (e.g., binary content
  named `.txt`)? → The system MUST reject it with a clear error, regardless
  of which tokenizer mode is selected.
- What happens with a corrupted PDF, or a scanned/image-only PDF with no
  extractable text? → The system MUST reject each with its own distinct,
  clear error (unchanged from prior behavior).
- What happens when an upload exceeds the maximum allowed size? → The
  system MUST reject it with a message stating the limit, regardless of
  tokenizer mode.
- What happens if the custom vocabulary fails to initialize, or the custom
  tokenizer's internal state becomes invalid mid-request? → The system MUST
  report a distinct, clear error rather than crashing or returning a
  corrupted result.
- What happens when custom-tokenizer input contains only punctuation,
  numbers, whitespace, or non-Latin/Unicode characters? → Each such unit is
  still split and tokenized deterministically following the same
  documented rule, and can still become a new vocabulary entry.
- What happens if two tokenization requests for the same new word arrive
  for the same session at effectively the same time? → The vocabulary MUST
  end up with exactly one entry for that word (no duplicate IDs, no lost
  updates).
- What happens if the user resets the vocabulary while a tokenization
  request is still in flight? → The system MUST leave the vocabulary in a
  consistent state — either the reset or the tokenization's update applies
  cleanly, never a mix that produces duplicate or missing entries.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST let a user provide input as typed/pasted
  text, an uploaded `.txt` file, or an uploaded `.pdf` file, in either
  tokenizer mode (continuity of existing capability).
- **FR-002**: The system MUST let the user select exactly one tokenizer
  mode at a time — Tiktokenizer or Custom Tokenizer — and MUST make the
  currently active mode visually unambiguous at all times. Switching modes
  MUST preserve the currently entered text or uploaded file, but MUST
  clear any previously displayed tokenization results until the user
  tokenizes again in the newly selected mode.
- **FR-003**: In Tiktokenizer mode, the system MUST let the user choose one
  of exactly four supported encodings (`cl100k_base`, `o200k_base`,
  `p50k_base`, `r50k_base`) and MUST reject any other value with a message
  listing the valid options.
- **FR-004**: In Tiktokenizer mode, for every successful tokenization the
  system MUST return: the original/extracted text, total token count, each
  token's index/ID/decoded text/byte representation, character count, word
  count, tokens-per-word, tokens-per-character, the encoding used, and the
  input source type.
- **FR-005**: In Custom Tokenizer mode, the system MUST tokenize using an
  independent, application-owned vocabulary that is never read from or
  written to any tiktoken encoding — selecting or using Custom Tokenizer
  MUST NOT alter tiktoken behavior in any way.
- **FR-006**: The Custom Tokenizer's vocabulary MUST start from a small,
  fixed, predefined set of entries, each with a token string, a token ID,
  and a frequency; token IDs MUST be assigned deterministically (the same
  input history always produces the same IDs).
- **FR-007**: The Custom Tokenizer MUST split input into token units using
  one fixed, documented, deterministic rule: a maximal run of letter
  characters is one "word" token; a maximal run of decimal digit characters
  is one "number" token; a maximal run of whitespace characters is one
  "whitespace" token; every other character (punctuation or symbol) is its
  own single-character token.
- **FR-008**: For each resulting token unit, the Custom Tokenizer MUST look
  it up in the vocabulary using a case-insensitive match for word tokens
  (e.g., "Hello" and "hello" resolve to the same entry) — if found, it MUST
  reuse that entry's existing ID and increase its frequency by one; if not
  found, it MUST assign the next sequential ID, add it to the vocabulary
  with a starting frequency of one, and mark it as newly added for that
  request only. The vocabulary's stored token text for a word entry MUST be
  its first-seen casing.
- **FR-009**: For every successful Custom Tokenizer request, the system
  MUST return: the original/extracted text, total token count, each
  token's ID/text/index/new-or-existing flag, character count, word count,
  tokens-per-word, tokens-per-character, the current vocabulary size, the
  count of tokens newly added by this request, and a snapshot of the full
  current vocabulary with no cap or pagination, regardless of how large
  the vocabulary has grown within the session.
- **FR-010**: The system MUST keep each user's custom vocabulary isolated
  from other users' vocabularies — tokenizing in one session MUST NOT
  change what another session's vocabulary contains.
- **FR-011**: The Custom Tokenizer's vocabulary MUST be retained only for
  as long as its owning session is active and the backend is running; no
  database or other persistent storage is used for it.
- **FR-012**: The system MUST display the full current custom vocabulary
  (ID, token text, frequency, status) whenever Custom Tokenizer mode is
  active, with no cap or pagination regardless of vocabulary size, and
  MUST refresh that display after every successful custom tokenization
  without requiring a manual reload.
- **FR-013**: The system MUST let the user search/filter the displayed
  vocabulary by token text.
- **FR-014**: The system MUST visually distinguish, in the tokenized
  output, which tokens were newly added during the current tokenization
  versus tokens that already existed in the vocabulary.
- **FR-015**: The system MUST provide a "Reset Vocabulary" action, available
  only in Custom Tokenizer mode, that asks for confirmation before
  proceeding; once confirmed, it MUST restore the vocabulary, all
  frequencies, and all vocabulary statistics to exactly their initial
  state, discarding every dynamically added token for that session.
- **FR-016**: The system MUST continue to enforce every previously
  supported validation and error case — empty text, empty file, unsupported
  file extension or mismatched content, invalid/corrupted PDF, PDF with no
  extractable text, unsupported tiktoken encoding, and oversized upload —
  regardless of which tokenizer mode is active.
- **FR-017**: The system MUST detect and report, as distinct clear errors,
  Custom-Tokenizer-specific failure conditions: the vocabulary failing to
  initialize, the tokenizer's internal state being invalid, or malformed
  token data — without crashing or returning a partial/corrupted result.
- **FR-018**: The system MUST NOT introduce authentication, user accounts,
  or any database/persistent storage technology for this feature.

### Key Entities

- **Tokenizer Mode**: Which of the two independent tokenization paths is
  currently active for a request — Tiktokenizer or Custom Tokenizer.
- **Tiktoken Result**: The outcome of a Tiktokenizer request — text,
  encoding used, source type, ordered tokens (index, ID, decoded text,
  bytes), and statistics. Unchanged in shape from the existing application.
- **Custom Vocabulary Entry**: One entry in a Custom Tokenizer's
  vocabulary — token ID, token text, and frequency (how many times it has
  been produced in that session).
- **Custom Tokenization Result**: The outcome of a Custom Tokenizer
  request — text, ordered tokens (ID, text, index, new-or-existing flag),
  statistics, vocabulary size, count of tokens newly added by this
  request, and the full current vocabulary snapshot.
- **Tokenizer Session**: The scope within which one user's Custom
  Tokenizer vocabulary persists and grows, isolated from other sessions'
  vocabularies.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can tokenize identical input in both Tiktokenizer and
  Custom Tokenizer mode, within the same visit, without a page reload, and
  get mode-appropriate results every time.
- **SC-002**: Every token that did not previously exist in a session's
  custom vocabulary is visibly flagged as new immediately after the
  tokenization that introduced it, and appears in the vocabulary view
  without any manual refresh, 100% of the time.
- **SC-003**: Re-tokenizing the exact same text a second time in the same
  session reports zero newly added tokens, 100% of the time.
- **SC-004**: Resetting the vocabulary restores it to precisely its initial
  entries, frequencies, and size, verified every time it is used.
- **SC-005**: All previously supported error scenarios continue to produce
  clear, distinct, correctly-worded error messages after this update, with
  no regression from the application's prior behavior.
- **SC-006**: Two concurrent sessions tokenizing different text each see
  only their own vocabulary change — neither sees the other's tokens
  appear, 100% of the time.
- **SC-007**: A user can go from choosing an input method (text, TXT, or
  PDF) to seeing full tokenized results in a single "Tokenize" action, for
  either tokenizer mode.

## Assumptions

- Per explicit instruction, the frontend is rebuilt as a React + TypeScript
  single-page application replacing Streamlit; this is a given directive
  from the request, not a choice made while writing this specification.
  The backend continues to be reachable over REST/HTTP as before.
- **Session scoping**: each browser session is identified by an identifier
  the frontend generates and retains for that browser (no login), sent with
  every Custom Tokenizer request; the backend keeps one in-memory
  vocabulary per identifier and seeds a fresh one automatically the first
  time an identifier is seen. This satisfies the request's preference for
  session-isolated vocabulary without introducing accounts or a database.
- **Token status categories** shown for each vocabulary entry: "Initial"
  (part of the predefined seed vocabulary, not yet produced by any
  tokenization this session), "Existing" (has been produced before,
  frequency greater than zero), "New" (first produced by the current
  request).
- **Token bytes** (Tiktokenizer mode) means the array of raw byte values
  (0–255) making up that token's decoded byte sequence, consistent with
  how the token would be represented before being decoded to text.
- The Custom Tokenizer's initial predefined vocabulary is a small, fixed
  set of common example entries (on the order of a handful of tokens);
  its exact contents are illustrative and not user-configurable in this
  version.
- "Word" characters for the Custom Tokenizer's splitting rule are Unicode
  letters (not limited to ASCII), so non-English text is split the same
  deterministic way rather than being rejected or treated as unsupported.
- Concurrent requests within one session are handled so the vocabulary
  never ends up with duplicate IDs for the same token or a lost update;
  the exact mechanism is a technical decision for planning, not this spec.
- No automated tests, UI polish level, or specific component boundaries are
  dictated by this spec beyond what's needed to satisfy the requirements
  above; those are technical/planning concerns.
