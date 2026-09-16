from concurrent.futures import ThreadPoolExecutor

import pytest

from app.core.errors import InvalidTokenizerStateError, MalformedTokenDataError
from app.core.session_store import SessionVocabularyStore
from app.schemas.custom_tokenizer import VocabularyEntry
from app.services.custom_tokenizer_service import CustomTokenizerService


@pytest.fixture
def service():
    return CustomTokenizerService(SessionVocabularyStore())


def test_seed_vocabulary_contents_and_ids(service):
    result = service.tokenize("session-a", "placeholder")
    ids_by_text = {entry.token_text: entry.token_id for entry in result.vocabulary}

    assert ids_by_text["<UNK>"] == 0
    assert ids_by_text["hello"] == 1
    assert ids_by_text["world"] == 2


def test_known_token_lookup_reuses_id_and_increments_frequency(service):
    first = service.tokenize("session-a", "hello")
    hello_entry = next(e for e in first.vocabulary if e.token_text == "hello")
    assert hello_entry.frequency == 1

    second = service.tokenize("session-a", "hello")
    hello_entry_2 = next(e for e in second.vocabulary if e.token_text == "hello")
    assert hello_entry_2.token_id == hello_entry.token_id
    assert hello_entry_2.frequency == 2
    assert second.new_token_count == 0


def test_unseen_token_gets_next_sequential_id_and_marked_new(service):
    result = service.tokenize("session-a", "developer")
    developer_token = next(t for t in result.tokens if t.token_text == "developer")

    assert developer_token.is_new is True
    assert developer_token.token_id == 3
    assert result.new_token_count == 1
    assert result.vocabulary_size == 4


def test_repeating_input_yields_zero_new_tokens_and_same_ids(service):
    first = service.tokenize("session-a", "hello developer")
    first_ids = {t.token_text: t.token_id for t in first.tokens}

    second = service.tokenize("session-a", "hello developer")
    second_ids = {t.token_text: t.token_id for t in second.tokens}

    assert second.new_token_count == 0
    assert first_ids == second_ids
    for token in second.tokens:
        assert token.is_new is False


def test_case_insensitive_word_matching(service):
    first = service.tokenize("session-a", "Hello")
    hello_entry = next(e for e in first.vocabulary if e.token_text.lower() == "hello")
    assert hello_entry.token_text == "hello"  # first-seen casing from the seed vocabulary
    assert hello_entry.frequency == 1

    second = service.tokenize("session-a", "HELLO")
    assert second.new_token_count == 0
    hello_entry_2 = next(e for e in second.vocabulary if e.token_text.lower() == "hello")
    assert hello_entry_2.token_id == hello_entry.token_id
    assert hello_entry_2.frequency == 2


def test_split_rule_on_mixed_content(service):
    tokens = service.split("Hello, world! 123")
    assert tokens == ["Hello", ",", "world", "!", "123"]


def test_split_rule_on_unicode_text(service):
    tokens = service.split("héllo wörld")
    assert tokens == ["héllo", "wörld"]


def test_vocabulary_reset_restores_seed_state(service):
    service.tokenize("session-a", "hello developer world")
    assert service.reset("session-a").vocabulary_size == 3

    vocabulary = service.get_vocabulary("session-a").vocabulary
    assert len(vocabulary) == 3
    assert all(entry.frequency == 0 for entry in vocabulary)
    assert all(entry.status == "initial" for entry in vocabulary)


def test_session_isolation(service):
    service.tokenize("session-a", "developer")
    vocab_b = service.get_vocabulary("session-b").vocabulary
    assert not any(entry.token_text == "developer" for entry in vocab_b)


def test_tokenize_raises_on_duplicate_token_id(service):
    store = service._store
    store.update(
        "corrupt-session",
        [
            VocabularyEntry(token_id=0, token_text="a", frequency=0, status="initial"),
            VocabularyEntry(token_id=0, token_text="b", frequency=0, status="initial"),
        ],
    )
    with pytest.raises(InvalidTokenizerStateError):
        service.tokenize("corrupt-session", "a")


def test_tokenize_raises_on_malformed_token_data(service):
    store = service._store
    store.update(
        "corrupt-session-2",
        [VocabularyEntry.model_construct(token_id="not-an-int", token_text="a", frequency=0, status="initial")],
    )
    with pytest.raises(MalformedTokenDataError):
        service.tokenize("corrupt-session-2", "a")


def test_concurrent_tokenize_for_same_new_word_creates_exactly_one_entry(service):
    session_id = "concurrent-session"

    def run():
        return service.tokenize(session_id, "concurrentword")

    with ThreadPoolExecutor(max_workers=16) as executor:
        results = list(executor.map(lambda _: run(), range(16)))

    final_vocabulary = service.get_vocabulary(session_id).vocabulary
    matching_entries = [e for e in final_vocabulary if e.token_text == "concurrentword"]

    assert len(matching_entries) == 1
    assert matching_entries[0].frequency == 16
    assert len({e.token_id for e in final_vocabulary}) == len(final_vocabulary)

    new_count_total = sum(r.new_token_count for r in results)
    assert new_count_total == 1
