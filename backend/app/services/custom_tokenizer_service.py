import re

from app.core.errors import InvalidTokenizerStateError, MalformedTokenDataError
from app.core.session_store import SessionVocabularyStore, session_vocabulary_store
from app.schemas.custom_tokenizer import (
    CustomToken,
    CustomTokenizationResult,
    VocabularyEntry,
    VocabularyResponse,
    ResetResponse,
)


def _canonical_status(frequency: int) -> str:
    return "initial" if frequency == 0 else "existing"


class CustomTokenizerService:
    def __init__(self, store: SessionVocabularyStore) -> None:
        self._store = store

    def split(self, text: str) -> list[str]:
        preprocessed = re.split(r'([,.:;?_!"()\']|--|\s)', text)
        return [item.strip() for item in preprocessed if item.strip()]

    def _check_vocabulary_integrity(self, vocabulary: list[VocabularyEntry]) -> None:
        seen_ids: set[int] = set()
        for entry in vocabulary:
            if not isinstance(entry.token_id, int) or isinstance(entry.token_id, bool):
                raise MalformedTokenDataError(
                    "A vocabulary entry has a non-integer token_id."
                )
            if not isinstance(entry.token_text, str) or not entry.token_text:
                raise MalformedTokenDataError(
                    "A vocabulary entry has an empty or non-string token_text."
                )
            if not isinstance(entry.frequency, int) or isinstance(entry.frequency, bool):
                raise MalformedTokenDataError(
                    "A vocabulary entry has a non-integer frequency."
                )
            if entry.token_id in seen_ids:
                raise InvalidTokenizerStateError(
                    "The custom tokenizer's vocabulary contains a duplicate token ID."
                )
            seen_ids.add(entry.token_id)

    def _lookup_key(self, unit: str) -> str:
        return unit.lower() if unit.isalpha() else unit

    def _tokenize_locked(
        self, vocabulary: list[VocabularyEntry], text: str
    ) -> tuple[list[CustomToken], int, list[VocabularyEntry]]:
        """Runs entirely inside SessionVocabularyStore.mutate()'s lock, so the
        whole read-modify-write cycle for this session is atomic — two
        concurrent requests for the same new word can never both create a
        new entry or race on the same entry's frequency."""
        self._check_vocabulary_integrity(vocabulary)

        index_by_key = {self._lookup_key(entry.token_text): i for i, entry in enumerate(vocabulary)}
        newly_created_ids: set[int] = set()

        units = self.split(text)
        tokens: list[CustomToken] = []
        new_token_count = 0

        for i, unit in enumerate(units):
            key = self._lookup_key(unit)

            if key in index_by_key:
                entry = vocabulary[index_by_key[key]]
                entry.frequency += 1
                is_new = False
            else:
                new_id = max((e.token_id for e in vocabulary), default=-1) + 1
                entry = VocabularyEntry(
                    token_id=new_id, token_text=unit, frequency=1, status="new"
                )
                vocabulary.append(entry)
                index_by_key[key] = len(vocabulary) - 1
                newly_created_ids.add(new_id)
                is_new = True
                new_token_count += 1

            tokens.append(
                CustomToken(index=i, token_id=entry.token_id, token_text=unit, is_new=is_new)
            )

        # Persist canonical status (never "new") so it doesn't leak into later,
        # unrelated requests; the response snapshot below overrides "new" for
        # entries created by *this* call only.
        for entry in vocabulary:
            entry.status = _canonical_status(entry.frequency)

        vocabulary_snapshot = [
            entry.model_copy(update={"status": "new"}) if entry.token_id in newly_created_ids else entry
            for entry in vocabulary
        ]

        return tokens, new_token_count, vocabulary_snapshot

    def tokenize(self, session_id: str, text: str) -> CustomTokenizationResult:
        tokens, new_token_count, vocabulary_snapshot = self._store.mutate(
            session_id, lambda vocabulary: self._tokenize_locked(vocabulary, text)
        )

        character_count = len(text)
        word_count = len(text.split())
        token_count = len(tokens)

        return CustomTokenizationResult(
            text=text,
            tokens=tokens,
            token_count=token_count,
            character_count=character_count,
            word_count=word_count,
            tokens_per_word=(token_count / word_count) if word_count else 0.0,
            tokens_per_character=(token_count / character_count) if character_count else 0.0,
            vocabulary_size=len(vocabulary_snapshot),
            new_token_count=new_token_count,
            vocabulary=vocabulary_snapshot,
        )

    def get_vocabulary(self, session_id: str) -> VocabularyResponse:
        vocabulary = self._store.get_or_create(session_id)
        self._check_vocabulary_integrity(vocabulary)
        return VocabularyResponse(vocabulary=list(vocabulary), vocabulary_size=len(vocabulary))

    def reset(self, session_id: str) -> ResetResponse:
        vocabulary = self._store.reset(session_id)
        return ResetResponse(vocabulary=list(vocabulary), vocabulary_size=len(vocabulary))


custom_tokenizer_service = CustomTokenizerService(session_vocabulary_store)
