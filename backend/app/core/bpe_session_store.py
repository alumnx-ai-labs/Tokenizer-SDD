import threading
from contextlib import contextmanager
from typing import Iterator

from app.core.errors import BPETrainingInProgressError
from app.schemas.bpe import BPEMergeRule, BPETrainingStep, BPEVocabularyEntry


class BPEModel:
    def __init__(
        self,
        vocabulary: list[BPEVocabularyEntry],
        merge_rules: list[BPEMergeRule],
        training_log: list[BPETrainingStep],
    ) -> None:
        self.vocabulary = vocabulary
        self.merge_rules = merge_rules
        self.training_log = training_log


class SessionBPEModelStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._models: dict[str, BPEModel] = {}
        self._training_sessions: set[str] = set()

    def get(self, session_id: str) -> BPEModel | None:
        with self._lock:
            return self._models.get(session_id)

    def set(self, session_id: str, model: BPEModel) -> None:
        with self._lock:
            self._models[session_id] = model

    @contextmanager
    def training_slot(self, session_id: str) -> Iterator[None]:
        """Reserves the session's training slot for the duration of the
        `with` block, rejecting a second concurrent training request for the
        same session (FR-021) rather than queueing or running it alongside
        the first."""
        with self._lock:
            if session_id in self._training_sessions:
                raise BPETrainingInProgressError(
                    "A BPE training run is already in progress for this session."
                )
            self._training_sessions.add(session_id)
        try:
            yield
        finally:
            with self._lock:
                self._training_sessions.discard(session_id)


session_bpe_model_store = SessionBPEModelStore()
