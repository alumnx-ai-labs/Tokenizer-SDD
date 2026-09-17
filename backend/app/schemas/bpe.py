from pydantic import BaseModel


class BPEVocabularyEntry(BaseModel):
    token_id: int
    token_text: str


class BPEMergeRule(BaseModel):
    step: int
    pair: list[str]
    merged_token_text: str


class BPETrainingStep(BaseModel):
    step: int
    pair: list[str]
    frequency: int
    merged_token_text: str


class BPETrainRequest(BaseModel):
    training_text: str
    vocab_size: int


class BPETrainResponse(BaseModel):
    vocabulary: list[BPEVocabularyEntry]
    merge_rules: list[BPEMergeRule]
    training_log: list[BPETrainingStep]
    vocabulary_size: int


class BPETokenizeRequest(BaseModel):
    text: str


class BPEToken(BaseModel):
    index: int
    token_id: int
    token_text: str


class BPETokenizeResult(BaseModel):
    text: str
    tokens: list[BPEToken]
    token_count: int
    character_count: int
    word_count: int
    tokens_per_word: float
    tokens_per_character: float
