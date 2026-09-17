import pytest

from app.core.bpe_session_store import SessionBPEModelStore
from app.core.errors import (
    BPEModelNotTrainedError,
    BPETrainingInProgressError,
    InvalidVocabSizeError,
)
from app.services.bpe_service import BpeService


@pytest.fixture
def service():
    return BpeService(SessionBPEModelStore())


# --- Training ---


def test_train_splits_on_whitespace_and_never_merges_across_boundary(service):
    # "aa aa" has base symbols {'a', ' '} (2). A vocab_size of 3 allows
    # exactly one merge. If merges could cross the space, "a "+"a" or
    # similar cross-boundary pairs would be candidates; they must not be.
    result = service.train("session-a", "aa aa", vocab_size=3)
    assert result.merge_rules[0].pair == ["a", "a"]
    assert " " not in "".join(result.merge_rules[0].pair)


def test_train_base_symbols_are_case_sensitive(service):
    result = service.train("session-a", "Aa Aa Aa", vocab_size=4)
    texts = {entry.token_text for entry in result.vocabulary}
    assert "A" in texts
    assert "a" in texts


def test_train_merges_most_frequent_within_word_pair_first(service):
    # "ab ab ab" -> word segments ["ab","ab","ab"], pair ("a","b") occurs
    # 3 times, more than any other pair, so it must be the first merge.
    result = service.train("session-a", "ab ab ab", vocab_size=10)
    assert result.merge_rules[0].pair == ["a", "b"]
    assert result.merge_rules[0].merged_token_text == "ab"
    assert result.training_log[0].frequency == 3


def test_train_is_deterministic_across_runs(service):
    first = service.train("session-a", "the cat sat on the mat", vocab_size=15)
    second = service.train("session-b", "the cat sat on the mat", vocab_size=15)

    first_vocab = [(e.token_id, e.token_text) for e in first.vocabulary]
    second_vocab = [(e.token_id, e.token_text) for e in second.vocabulary]
    assert first_vocab == second_vocab

    first_rules = [(r.step, r.pair, r.merged_token_text) for r in first.merge_rules]
    second_rules = [(r.step, r.pair, r.merged_token_text) for r in second.merge_rules]
    assert first_rules == second_rules


def test_train_stops_early_when_no_pair_repeats(service):
    # "abcd" has 4 distinct base symbols, no repeated adjacent pair at all,
    # so even a huge vocab_size should stop immediately with zero merges.
    result = service.train("session-a", "abcd", vocab_size=100)
    assert result.merge_rules == []
    assert result.vocabulary_size == 4


def test_train_rejects_vocab_size_at_or_below_base_symbol_count(service):
    with pytest.raises(InvalidVocabSizeError):
        service.train("session-a", "abcd", vocab_size=4)
    with pytest.raises(InvalidVocabSizeError):
        service.train("session-a", "abcd", vocab_size=3)


def test_train_rejects_non_positive_vocab_size(service):
    with pytest.raises(InvalidVocabSizeError):
        service.train("session-a", "hello world", vocab_size=0)
    with pytest.raises(InvalidVocabSizeError):
        service.train("session-a", "hello world", vocab_size=-1)


def test_train_rejects_vocab_size_over_max(service):
    with pytest.raises(InvalidVocabSizeError):
        service.train("session-a", "hello world", vocab_size=50_001)


def test_retraining_replaces_previous_model(service):
    service.train("session-a", "aa aa aa", vocab_size=3)
    second = service.train("session-a", "bb bb bb", vocab_size=3)

    result = service.tokenize("session-a", "bb")
    assert result.tokens[0].token_text == "bb"
    assert second.merge_rules[0].pair == ["b", "b"]


def test_second_training_request_while_in_progress_is_rejected(service):
    with service._store.training_slot("session-a"):
        with pytest.raises(BPETrainingInProgressError):
            service.train("session-a", "aa aa", vocab_size=5)


def test_training_slot_is_released_after_completion_so_retraining_works(service):
    service.train("session-a", "aa aa", vocab_size=5)
    # A second, sequential training call for the same session must not be
    # blocked once the first has finished.
    service.train("session-a", "bb bb", vocab_size=5)


# --- Tokenization ---


def test_tokenize_applies_only_trained_merge_rules_in_order(service):
    service.train("session-a", "ab ab ab abc", vocab_size=10)
    result = service.tokenize("session-a", "ab")
    assert [t.token_text for t in result.tokens] == ["ab"]


def test_tokenize_is_deterministic_and_does_not_mutate_model(service):
    trained = service.train("session-a", "the cat sat on the mat", vocab_size=15)
    before = [(e.token_id, e.token_text) for e in trained.vocabulary]

    first = service.tokenize("session-a", "the cat")
    second = service.tokenize("session-a", "the cat")
    assert [t.token_id for t in first.tokens] == [t.token_id for t in second.tokens]
    assert [t.token_text for t in first.tokens] == [t.token_text for t in second.tokens]

    after = [(e.token_id, e.token_text) for e in service._store.get("session-a").vocabulary]
    assert before == after


def test_tokenize_falls_back_deterministically_for_unseen_characters(service):
    service.train("session-a", "aa aa aa", vocab_size=3)
    result = service.tokenize("session-a", "z")
    assert len(result.tokens) == 1
    assert result.tokens[0].token_text == "z"
    assert result.tokens[0].token_id == -1


def test_tokenize_raises_when_no_model_trained(service):
    with pytest.raises(BPEModelNotTrainedError):
        service.tokenize("never-trained-session", "hello")
