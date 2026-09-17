# Feature Specification: React Frontend with Dual Tokenizer Modes and BPE Training

**Feature Branch**: `002-react-custom-tokenizer`

**Created**: 2026-09-16

**Last Updated**: 2026-09-17

**Status**: Draft

**Input**: User description: "Update the existing Tokenizer Application: replace the Streamlit frontend with a React + TypeScript frontend; add a tokenizer mode selector between the existing tiktoken-based tokenizer and a new, independent Custom Tokenizer with its own dynamically-growing, deterministic vocabulary; keep existing text/TXT/PDF input, validation, and error handling; no database, no auth."

**Update (2026-09-17)**: "Enhance the Custom Tokenizer with Byte Pair Encoding (BPE): keep Tiktokenizer and the existing (word-based) Custom Tokenizer unchanged; let a user enter training text, set a target vocabulary size, and start BPE training; after training, show the learned vocabulary, ordered merge rules, and per-step training details (pair selected and merged at each step); let the user then tokenize new text with the trained BPE tokenizer, showing tokens and token IDs in the existing tokenization result table; clearly separate the BPE training flow from the BPE tokenization flow with appropriate loading, empty, validation, success, and error states; BPE must learn merges only during training, never during tokenization; BPE vocabulary IDs must be deterministic."

## Clarifications

### Session 2026-09-16

- Q: Should the Custom Tokenizer treat two words that differ only in letter case (e.g., "Hello" vs "hello") as the same vocabulary token, or as two distinct tokens? → A: Case-insensitive — they map to the same vocabulary entry/ID, and frequency counts both.
- Q: As a session's custom vocabulary grows over a long-running conversation, should every tokenization response and the vocabulary view always include the complete vocabulary, or should there be a cap with pagination for very large vocabularies? → A: Always the full vocabulary, no cap — new tokens keep being added to the same complete list every time.
- Q: When a user switches between Tiktokenizer and Custom Tokenizer mode, should their already-entered text/file stay loaded, or should switching clear the input and results? → A: Keep the input loaded; clear only the previous mode's displayed results until "Tokenize" is pressed again.

### Session 2026-09-17

- Q: Should BPE training/tokenization count as a capability of the single "Custom Tokenizer" that the project's governing principles already permit as the one additional non-tiktoken tokenizer, or does it constitute a second, distinct tokenizer engine? → A: BPE is part of the single permitted Custom Tokenizer — it is an enhancement of that one tokenizer (word-based splitting and BPE are two selectable behaviors of the same tokenizer), not a separate third tokenizer engine.
- Q: Should BPE merges be allowed to combine characters across whitespace, or should training split on whitespace first and only merge within each resulting word? → A: Pre-split on whitespace; merge only within each word's characters. Whitespace runs are never merged into another token.
- Q: Should the system enforce an upper bound on training text length and/or target vocabulary size? → A: Yes — cap training text at the same 5 MB limit already used for uploads/typed text elsewhere in the app, and cap target vocabulary size at 50,000; reject requests exceeding either with a clear validation message before training starts.
- Q: Should BPE's base symbols be case-sensitive, or case-folded like the existing word-based Custom Tokenizer? → A: Case-sensitive — "A" and "a" are distinct base symbols from the start, unlike the existing word-based tokenizer's case-insensitive matching.
- Q: Should starting a new BPE training run require confirmation, since it discards the session's previous BPE model? → A: No confirmation — starting a new run immediately replaces the previous model, since results are deterministic and reproducible from the same inputs.

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

### User Story 5 - Train a BPE Tokenizer on Custom Text (Priority: P5)

Within Custom Tokenizer mode, a user enters training text, sets a target
vocabulary size, and starts BPE (Byte Pair Encoding) training — separate
from, and without affecting, the existing word-based Custom Tokenizer. Once
training finishes, the user sees the learned vocabulary, the ordered merge
rules, and a step-by-step training log showing which pair was selected and
merged at each step.

**Why this priority**: This is the headline enhancement of this update, but
it is additive: the application must remain fully usable via Tiktokenizer
and the existing Custom Tokenizer even if BPE training were never used,
which is why it is sequenced after those established flows.

**Independent Test**: Can be fully tested by opening the BPE Training flow,
entering training text and a target vocabulary size, starting training, and
confirming the resulting vocabulary, merge rules, and step-by-step log are
all displayed and internally consistent (each step's merge matches the
corresponding merge rule and produces the vocabulary shown) — without
touching the word-based Custom Tokenizer or Tiktokenizer.

**Acceptance Scenarios**:

1. **Given** the BPE Training flow with no training run yet this session,
   **When** the user first opens it, **Then** the system shows an empty
   state indicating no BPE model has been trained yet, with no vocabulary,
   merge rules, or training log displayed.
2. **Given** valid training text and a valid target vocabulary size,
   **When** the user starts training, **Then** the system shows a loading/
   in-progress state, and MUST NOT accept a second concurrent training
   request for the same session while it is running.
3. **Given** a training run completes successfully, **When** results are
   displayed, **Then** the system shows the final learned vocabulary (every
   entry's token ID and token text), the ordered list of merge rules in the
   exact sequence they were learned, and a training log listing, for every
   step, the pair selected, the frequency that made it the top pair at that
   step, and the resulting merged token.
4. **Given** the BPE Training flow, **When** the user submits empty/
   whitespace-only training text, a non-integer, zero, or negative target
   vocabulary size, **Then** the system rejects the request with a clear,
   field-specific validation message and does not start training.
5. **Given** a target vocabulary size that is at or below the number of
   distinct base symbols already present in the training text, **When** the
   user starts training, **Then** the system rejects the request with a
   validation message explaining the minimum valid vocabulary size for that
   training text.
6. **Given** a target vocabulary size larger than the training text can
   ever reach (no adjacent pair repeats), **When** training runs, **Then**
   it stops early once no further merge is possible, and the system clearly
   reports the final vocabulary size actually achieved rather than reporting
   an error.
7. **Given** a training request that fails on the backend, **When** the
   failure occurs, **Then** the system shows a distinct, clear error state
   and leaves any previously trained model for that session unchanged.
8. **Given** a session already has a trained BPE model, **When** the user
   runs training again with new training text or a new target vocabulary
   size, **Then** training starts immediately without a confirmation
   prompt, and the previous vocabulary, merge rules, and training log are
   entirely replaced by the new run's results.

---

### User Story 6 - Tokenize Text with the Trained BPE Tokenizer (Priority: P6)

After training a BPE model, a user enters new text and tokenizes it using
that trained model, seeing the resulting tokens and token IDs in the same
tokenization result table used by the other tokenizer flows.

**Why this priority**: This is what makes BPE training useful, but it is
only meaningful once User Story 5 has produced a trained model, so it is
sequenced immediately after it.

**Independent Test**: Can be fully tested by training a BPE model, then
entering new text (including text with characters not seen during
training) in the BPE Tokenization flow, tokenizing it, and confirming the
displayed tokens/IDs are correct, deterministic, and that neither the
vocabulary nor the merge rules changed as a result.

**Acceptance Scenarios**:

1. **Given** no BPE model has been trained yet for the session, **When**
   the user opens the BPE Tokenization flow, **Then** the system shows an
   empty/blocked state instructing the user to train a BPE model first, and
   does not allow a tokenization request to be submitted.
2. **Given** a trained BPE model exists, **When** the user enters text and
   tokenizes it, **Then** the system shows a loading state followed by the
   resulting ordered tokens and their token IDs in the existing tokenization
   result table, using only the merge rules learned during training.
3. **Given** a trained BPE model, **When** the user tokenizes the exact same
   text more than once, **Then** the resulting tokens and token IDs are
   identical every time, and the trained vocabulary and merge rules remain
   unchanged after each tokenization.
4. **Given** a trained BPE model, **When** the user tokenizes text
   containing characters that never appeared in the training text, **Then**
   the system still completes tokenization deterministically (without
   erroring) and without adding any new merge rule to the trained model.
5. **Given** the BPE Tokenization flow, **When** the user submits empty/
   whitespace-only text, **Then** the system rejects the request with a
   clear validation message and does not call the trained model.
6. **Given** a tokenization request that fails on the backend, **When** the
   failure occurs, **Then** the system shows a distinct, clear error state
   and the trained model is left unchanged.

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
- What happens when BPE training text has fewer distinct base symbols than
  the requested target vocabulary size can ever reach? → Training MUST stop
  once no further merge is possible and MUST report the smaller final
  vocabulary size actually achieved, not an error.
- What happens when the requested BPE target vocabulary size is invalid
  (non-integer, zero, negative, at/below the training text's base symbol
  count, or above 50,000)? → The system MUST reject the request with a
  clear, specific validation message and MUST NOT start training.
- What happens when the submitted BPE training text exceeds 5 MB? → The
  system MUST reject the request with a message stating the limit and
  MUST NOT start training, consistent with the same limit already enforced
  for other text input in this application.
- What happens when the user attempts BPE tokenization before any BPE
  training has completed for their session? → The system MUST block the
  attempt and clearly instruct the user to train a BPE model first.
- What happens when a second BPE training request arrives for a session
  while a prior training request is still running? → The system MUST
  reject the second request rather than running two trainings concurrently
  against the same session's model.
- What happens when BPE-tokenized text contains characters that never
  appeared in the training text? → The system MUST still tokenize it
  deterministically using the trained model's base symbols, without
  crashing and without learning a new merge rule.
- What happens if BPE training or tokenization fails, or a session's BPE
  model becomes invalid mid-request? → The system MUST report a distinct,
  clear error rather than crashing or returning a partial/corrupted result,
  and MUST leave any previously trained model unchanged.
- What happens when the most frequent adjacent pair in the training text
  would span a whitespace boundary (e.g., the end of one word and the
  start of the next)? → That pair MUST NOT be merged; only the most
  frequent pair that occurs within a single word is eligible at each step.

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
- **FR-019**: Within Custom Tokenizer mode, the system MUST provide a
  distinct BPE Training flow and a distinct BPE Tokenization flow, each
  separate from one another and from the existing word-based Custom
  Tokenizer flow, so a user always knows which one they are interacting
  with; no single, ambiguous control MUST trigger more than one of the
  three. BPE Training and BPE Tokenization are an enhancement of the one
  Custom Tokenizer this application already provides (a second selectable
  behavior alongside its existing word-based splitting), not a separate,
  independent third tokenizer engine.
- **FR-020**: The BPE Training flow MUST let the user supply training text
  and a target vocabulary size, and MUST validate both before starting:
  training text MUST NOT be empty or whitespace-only and MUST NOT exceed
  5 MB (the same maximum already enforced elsewhere in this application
  for typed/uploaded text), and the target vocabulary size MUST be a
  positive integer strictly greater than the number of distinct base
  symbols present in the training text and MUST NOT exceed 50,000; any
  violation MUST be rejected with a clear, field-specific message and MUST
  NOT start training.
- **FR-021**: While a BPE training run is in progress for a session, the
  system MUST show a loading/in-progress state and MUST reject any second
  training request for that same session submitted before the first
  completes, rather than queueing or running it concurrently.
- **FR-022**: The BPE algorithm MUST first split the training text into
  words using the same whitespace-boundary rule as the existing word-based
  Custom Tokenizer (a maximal run of whitespace is its own unmerged unit,
  never a candidate for merging), then repeatedly find the most frequent
  adjacent pair of symbols occurring within a single word (never spanning
  a whitespace boundary) and merge it into a new token, recording each
  merge as an ordered rule, until either the target vocabulary size is
  reached or no within-word adjacent pair occurs more than once —
  whichever happens first — and MUST clearly report the final vocabulary
  size actually achieved when it is smaller than the requested target.
- **FR-023**: Upon successful BPE training completion, the system MUST
  return and display: the complete learned vocabulary (every entry's token
  ID and token text), the ordered list of merge rules in the exact sequence
  learned, and a step-by-step training log identifying, for each step, the
  pair selected, the frequency that made it the top pair at that step, and
  the resulting merged token.
- **FR-024**: BPE vocabulary token IDs MUST be assigned deterministically —
  training on identical training text with an identical target vocabulary
  size MUST always produce the same vocabulary, the same merge rules in the
  same order, and the same token IDs, regardless of session, run count, or
  timing.
- **FR-025**: The BPE Tokenization flow MUST let the user enter new text
  and tokenize it using the most recently trained BPE model for their
  session; if no BPE model has been trained for that session, the system
  MUST block the attempt and clearly instruct the user to train one first,
  without sending a request that assumes a model exists.
- **FR-026**: BPE tokenization MUST apply only the merge rules learned
  during the most recent training for that session, in their learned
  order, and MUST NOT learn, add, remove, or reorder any merge rule, and
  MUST NOT alter the trained vocabulary, as part of tokenizing.
- **FR-027**: BPE tokenization of text containing symbols not present in
  the training text MUST still complete deterministically (falling back to
  base-symbol-level tokens for the unseen input) rather than failing or
  silently producing an incorrect result.
- **FR-028**: For every successful BPE tokenization request, the system
  MUST return the resulting ordered tokens and their token IDs, and MUST
  display them in the same tokenization result table used by the other
  tokenizer flows.
- **FR-029**: Starting a new BPE training run for a session MUST proceed
  immediately, without requiring a confirmation step, and MUST replace
  that session's previously trained BPE model (vocabulary, merge rules, and
  training log) in its entirety; subsequent BPE tokenization requests for
  that session MUST use only the newest trained model.
- **FR-030**: A session's BPE model (vocabulary, merge rules, and training
  log) MUST be isolated from other sessions' BPE models in the same manner
  as the existing Custom Tokenizer vocabulary, and MUST be retained only for
  as long as its owning session is active and the backend is running; no
  database or other persistent storage is used for it.
- **FR-031**: The system MUST detect and report, as distinct clear errors,
  BPE-specific failure conditions — invalid training input, a training
  failure, an internal BPE model becoming invalid, or a tokenization
  request made with no valid trained model — without crashing or returning
  a partial/corrupted result, and without altering any previously trained
  model when the failure occurs.
- **FR-032**: All BPE training and tokenization computation (selecting
  pairs, performing merges, assigning vocabulary IDs, and applying learned
  rules) MUST be performed by the server-side application logic; the
  client-side interface MUST be limited to collecting user input, calling
  the server, holding UI/loading/error state, and rendering the returned
  vocabulary, merge rules, training log, and tokenization results — it MUST
  NOT itself compute merges or assign vocabulary IDs.
- **FR-033**: Adding BPE Training and BPE Tokenization MUST NOT change the
  behavior, inputs, outputs, or vocabulary-growth rules of Tiktokenizer
  mode or the existing word-based Custom Tokenizer flow described in
  FR-001 through FR-018.

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
- **BPE Training Request**: A user's input to start BPE training —
  training text and a target vocabulary size.
- **BPE Merge Rule**: One learned rule pairing two symbols/tokens that are
  merged into a single new token, together with the step number at which
  it was learned; merge rules are ordered and applied in that order during
  tokenization.
- **BPE Training Step**: One iteration of the training log — the pair
  selected, the frequency that made it the most frequent adjacent pair at
  that step, and the resulting merged token.
- **BPE Vocabulary Entry**: One entry in a trained BPE model's
  vocabulary — token ID and token text — covering both base symbols and
  every symbol produced by a merge.
- **BPE Model**: The complete trained artifact for one session — its
  vocabulary, ordered merge rules, and training log — produced by the most
  recent BPE Training Request and used exclusively by that session's BPE
  Tokenization requests.
- **BPE Tokenization Result**: The outcome of tokenizing new text with a
  session's trained BPE Model — ordered tokens, token IDs, and statistics,
  shown in the existing tokenization result table.

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
- **SC-008**: A user can go from entering training text and a target
  vocabulary size to seeing the complete learned vocabulary, ordered merge
  rules, and step-by-step training details in a single "Train" action.
- **SC-009**: Tokenizing identical text with an unchanged trained BPE model
  produces identical tokens and token IDs, 100% of the time.
- **SC-010**: BPE tokenization never changes the vocabulary, merge rules,
  or training log produced by the most recent training, verified every
  time it is used.
- **SC-011**: Users can tell, without ambiguity, whether they are training
  a BPE model, tokenizing with an already-trained one, or using the
  existing word-based Custom Tokenizer, 100% of the time.
- **SC-012**: Attempting BPE tokenization before training completes is
  either prevented or clearly explained, with no silent failures or
  unexplained empty results, 100% of the time.
- **SC-013**: Training two BPE models from the same training text and the
  same target vocabulary size — on the same session or a different one —
  always yields the same vocabulary, merge rules, and token IDs.
- **SC-014**: Training text over 5 MB or a target vocabulary size over
  50,000 is rejected with a clear message before any training work starts,
  100% of the time.

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
- **BPE placement**: BPE Training and BPE Tokenization are two additional,
  clearly separated flows reachable from Custom Tokenizer mode, distinct
  from the existing word-based Custom Tokenizer flow. They share the mode's
  session scoping but not its vocabulary, merge rules, or growth behavior.
  Per the 2026-09-17 clarification, BPE is an enhancement of the single,
  already-permitted Custom Tokenizer (word-based splitting and BPE are two
  behaviors of that one tokenizer) — it is not a second, independent
  tokenizer engine, so it does not require expanding the number of
  non-tiktoken tokenizers the application supports.
- **BPE base symbols**: for the purposes of counting "distinct base
  symbols" and forming the starting point of a BPE model, a base symbol is
  one Unicode character of the training text (consistent with the
  character-oriented approach the existing Custom Tokenizer already takes),
  not a raw byte. This keeps the minimum-vocabulary-size validation rule
  (FR-020) and the training algorithm (FR-022) well-defined without
  dictating an internal representation.
- **BPE whitespace handling**: per the 2026-09-17 clarification, training
  text is first split into words on whitespace boundaries (the same rule
  the existing word-based Custom Tokenizer uses), and merges only ever
  combine symbols within a single word; a run of whitespace is counted
  among the training text's base symbols but is never itself merged into
  another token, and no merge ever spans across a whitespace boundary.
- **BPE case sensitivity**: per the 2026-09-17 clarification, BPE base
  symbols are case-sensitive — "A" and "a" are distinct symbols from the
  start of training and may end up in different merges/tokens — unlike the
  existing word-based Custom Tokenizer's case-insensitive word matching
  (FR-008). This is an intentional difference between the two behaviors of
  the one Custom Tokenizer, not an inconsistency to reconcile.
- **BPE size limits**: per the 2026-09-17 clarification, training text is
  capped at 5 MB (the same limit already enforced for other text input in
  this application) and target vocabulary size is capped at 50,000;
  requests exceeding either limit are rejected before training starts.
- **Backend/frontend split**: per explicit instruction, all BPE training
  and tokenization computation (pair selection, merging, vocabulary ID
  assignment, and applying learned rules) is implemented by the backend
  service; the frontend is limited to input collection, API calls, UI
  state, and rendering results. This is a given directive from the
  request, not a choice made while writing this specification, and is
  reflected in FR-032 in behavior-level ("server-side" / "client-side")
  terms rather than by naming a specific technology.
- **Unseen-symbol fallback**: when BPE-tokenizing text containing a
  character never seen during training, the trained model still produces a
  token for it deterministically (e.g., as its own base-symbol token)
  rather than erroring, since rejecting ordinary novel input would make the
  BPE Tokenization flow impractical for real use.
- **Re-training behavior**: each new BPE training run fully replaces the
  session's previous BPE model; this specification does not require
  retaining a history of prior trained models. Per the 2026-09-17
  clarification, no confirmation prompt is required before starting a new
  run, since a BPE model is fully deterministic and reproducible from the
  same training text and target vocabulary size (unlike Reset Vocabulary
  in US4, which discards non-reproducible frequency history and does
  require confirmation).
- **Concurrent training**: a second BPE training request for a session
  while one is already running is rejected (rather than queued), consistent
  with how the rest of this application surfaces one clear state at a time
  instead of silently queuing background work.
