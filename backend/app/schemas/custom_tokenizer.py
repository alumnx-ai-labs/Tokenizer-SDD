from pydantic import BaseModel


class VocabularyEntry(BaseModel):
    token_id: int
    token_text: str
    frequency: int
    status: str


class CustomToken(BaseModel):
    index: int
    token_id: int
    token_text: str
    is_new: bool


class CustomTokenizeRequest(BaseModel):
    text: str


class CustomTokenizationResult(BaseModel):
    text: str
    tokens: list[CustomToken]
    token_count: int
    character_count: int
    word_count: int
    tokens_per_word: float
    tokens_per_character: float
    vocabulary_size: int
    new_token_count: int
    vocabulary: list[VocabularyEntry]


class VocabularyResponse(BaseModel):
    vocabulary: list[VocabularyEntry]
    vocabulary_size: int


class ResetResponse(BaseModel):
    vocabulary: list[VocabularyEntry]
    vocabulary_size: int
