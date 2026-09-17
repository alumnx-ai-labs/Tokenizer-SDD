import re

from app.core.bpe_session_store import BPEModel, SessionBPEModelStore, session_bpe_model_store
from app.core.errors import BPEModelNotTrainedError, InvalidVocabSizeError
from app.schemas.bpe import (
    BPEMergeRule,
    BPEToken,
    BPETokenizeResult,
    BPETrainingStep,
    BPETrainResponse,
    BPEVocabularyEntry,
)
from app.services import validation

MAX_VOCAB_SIZE = 50_000

_SEGMENT_PATTERN = re.compile(r"(\s+)")


def _split_into_segments(text: str) -> list[tuple[str, bool]]:
    """Splits text into alternating (segment, is_whitespace) pairs, in
    order. A "word" segment (is_whitespace=False) is a maximal run of
    non-whitespace characters; a whitespace segment is a maximal run of
    whitespace, kept intact as a single atomic unit that is never split
    into characters or merged (per the 2026-09-17 clarification)."""
    return [
        (segment, segment.isspace())
        for segment in _SEGMENT_PATTERN.split(text)
        if segment != ""
    ]


def _base_symbols(segments: list[tuple[str, bool]]) -> set[str]:
    symbols: set[str] = set()
    for segment, is_whitespace in segments:
        if is_whitespace:
            symbols.add(segment)
        else:
            symbols.update(segment)
    return symbols


def _validate_vocab_size(vocab_size: int, base_symbol_count: int) -> None:
    if vocab_size <= 0:
        raise InvalidVocabSizeError("Target vocabulary size must be a positive integer.")
    if vocab_size <= base_symbol_count:
        raise InvalidVocabSizeError(
            "Target vocabulary size must be greater than the training text's "
            f"{base_symbol_count} distinct base symbol(s)."
        )
    if vocab_size > MAX_VOCAB_SIZE:
        raise InvalidVocabSizeError(
            f"Target vocabulary size must not exceed {MAX_VOCAB_SIZE}."
        )


def _most_frequent_pair(
    word_symbols: list[list[str]],
) -> tuple[tuple[str, str] | None, int]:
    """Scans every word's current symbol sequence for adjacent pairs and
    returns the most frequent one, ties broken by first occurrence (dict
    insertion order), for fully deterministic merge selection (FR-024)."""
    counts: dict[tuple[str, str], int] = {}
    for symbols in word_symbols:
        for left, right in zip(symbols, symbols[1:]):
            pair = (left, right)
            counts[pair] = counts.get(pair, 0) + 1
    if not counts:
        return None, 0
    best_pair = max(counts, key=lambda pair: counts[pair])
    return best_pair, counts[best_pair]


def _merge_pair(symbols: list[str], pair: tuple[str, str], merged: str) -> list[str]:
    result: list[str] = []
    i = 0
    while i < len(symbols):
        if i < len(symbols) - 1 and (symbols[i], symbols[i + 1]) == pair:
            result.append(merged)
            i += 2
        else:
            result.append(symbols[i])
            i += 1
    return result


def _apply_learned_merges(
    symbols: list[str], rank_by_pair: dict[tuple[str, str], int]
) -> list[str]:
    """Applies only the trained model's merge rules, in their learned
    order (lowest rank first), and never introduces a merge not already in
    rank_by_pair (FR-026)."""
    symbols = list(symbols)
    while len(symbols) > 1:
        pairs = list(zip(symbols, symbols[1:]))
        candidate = min(
            (pair for pair in pairs if pair in rank_by_pair),
            key=lambda pair: rank_by_pair[pair],
            default=None,
        )
        if candidate is None:
            break
        symbols = _merge_pair(symbols, candidate, candidate[0] + candidate[1])
    return symbols


class BpeService:
    def __init__(self, store: SessionBPEModelStore) -> None:
        self._store = store

    def train(self, session_id: str, training_text: str, vocab_size: int) -> BPETrainResponse:
        validation.validate_upload_size(len(training_text.encode("utf-8")))
        validation.validate_non_empty_text(training_text)

        segments = _split_into_segments(training_text)
        base_symbols = _base_symbols(segments)
        _validate_vocab_size(vocab_size, len(base_symbols))

        with self._store.training_slot(session_id):
            vocabulary, merge_rules, training_log = self._run_training(
                segments, vocab_size
            )
            self._store.set(
                session_id, BPEModel(vocabulary, merge_rules, training_log)
            )

        return BPETrainResponse(
            vocabulary=vocabulary,
            merge_rules=merge_rules,
            training_log=training_log,
            vocabulary_size=len(vocabulary),
        )

    def _run_training(
        self, segments: list[tuple[str, bool]], vocab_size: int
    ) -> tuple[list[BPEVocabularyEntry], list[BPEMergeRule], list[BPETrainingStep]]:
        vocabulary: list[BPEVocabularyEntry] = []
        token_id_by_text: dict[str, int] = {}

        def _ensure_entry(text: str) -> int:
            if text not in token_id_by_text:
                token_id = len(vocabulary)
                token_id_by_text[text] = token_id
                vocabulary.append(BPEVocabularyEntry(token_id=token_id, token_text=text))
            return token_id_by_text[text]

        word_symbols: list[list[str]] = []
        for segment, is_whitespace in segments:
            if is_whitespace:
                _ensure_entry(segment)
            else:
                for char in segment:
                    _ensure_entry(char)
                word_symbols.append(list(segment))

        merge_rules: list[BPEMergeRule] = []
        training_log: list[BPETrainingStep] = []
        step = 0

        while len(vocabulary) < vocab_size:
            best_pair, frequency = _most_frequent_pair(word_symbols)
            if best_pair is None or frequency <= 1:
                break

            merged_text = best_pair[0] + best_pair[1]
            _ensure_entry(merged_text)

            step += 1
            merge_rules.append(
                BPEMergeRule(step=step, pair=list(best_pair), merged_token_text=merged_text)
            )
            training_log.append(
                BPETrainingStep(
                    step=step,
                    pair=list(best_pair),
                    frequency=frequency,
                    merged_token_text=merged_text,
                )
            )

            word_symbols = [
                _merge_pair(symbols, best_pair, merged_text) for symbols in word_symbols
            ]

        return vocabulary, merge_rules, training_log

    def tokenize(self, session_id: str, text: str) -> BPETokenizeResult:
        model = self._store.get(session_id)
        if model is None:
            raise BPEModelNotTrainedError(
                "No BPE model has been trained for this session yet. Train one first."
            )

        vocab_id_by_text = {entry.token_text: entry.token_id for entry in model.vocabulary}
        rank_by_pair = {
            tuple(rule.pair): rank for rank, rule in enumerate(model.merge_rules)
        }

        tokens: list[BPEToken] = []
        for segment, is_whitespace in _split_into_segments(text):
            if is_whitespace:
                resulting_symbols = [segment]
            else:
                resulting_symbols = _apply_learned_merges(list(segment), rank_by_pair)

            for symbol in resulting_symbols:
                tokens.append(
                    BPEToken(
                        index=len(tokens),
                        token_id=vocab_id_by_text.get(symbol, -1),
                        token_text=symbol,
                    )
                )

        character_count = len(text)
        word_count = len(text.split())
        token_count = len(tokens)

        return BPETokenizeResult(
            text=text,
            tokens=tokens,
            token_count=token_count,
            character_count=character_count,
            word_count=word_count,
            tokens_per_word=(token_count / word_count) if word_count else 0.0,
            tokens_per_character=(token_count / character_count) if character_count else 0.0,
        )


bpe_service = BpeService(session_bpe_model_store)
