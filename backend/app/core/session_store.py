import threading
from typing import Callable, TypeVar

from app.core.errors import VocabularyInitError
from app.schemas.custom_tokenizer import VocabularyEntry

T = TypeVar("T")

_SEED_VOCABULARY_SPEC = [
    (0, "<UNK>"),
    (1, "hello"),
    (2, "world"),
]


def _build_seed_vocabulary() -> list[VocabularyEntry]:
    try:
        return [
            VocabularyEntry(token_id=token_id, token_text=token_text, frequency=0, status="initial")
            for token_id, token_text in _SEED_VOCABULARY_SPEC
        ]
    except Exception as exc:
        raise VocabularyInitError(
            "The custom tokenizer's seed vocabulary could not be initialized."
        ) from exc


class SessionVocabularyStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._sessions: dict[str, list[VocabularyEntry]] = {}

    def get_or_create(self, session_id: str) -> list[VocabularyEntry]:
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = _build_seed_vocabulary()
            return self._sessions[session_id]

    def mutate(
        self, session_id: str, fn: Callable[[list[VocabularyEntry]], T]
    ) -> T:
        """Run `fn` against the session's vocabulary while holding the lock
        for the entire read-modify-write cycle, so concurrent requests for
        the same session can't race (`fn` mutates the list in place)."""
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = _build_seed_vocabulary()
            return fn(self._sessions[session_id])

    def update(self, session_id: str, vocabulary: list[VocabularyEntry]) -> None:
        with self._lock:
            self._sessions[session_id] = vocabulary

    def reset(self, session_id: str) -> list[VocabularyEntry]:
        with self._lock:
            self._sessions[session_id] = _build_seed_vocabulary()
            return self._sessions[session_id]


session_vocabulary_store = SessionVocabularyStore()
