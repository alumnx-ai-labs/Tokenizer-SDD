from enum import Enum

from pydantic import BaseModel


class SupportedEncoding(str, Enum):
    cl100k_base = "cl100k_base"
    o200k_base = "o200k_base"
    p50k_base = "p50k_base"
    r50k_base = "r50k_base"


class SourceType(str, Enum):
    text = "text"
    txt_file = "txt_file"
    pdf_file = "pdf_file"


class Token(BaseModel):
    index: int
    token_id: int
    decoded_text: str
    token_bytes: list[int]


class TokenStatistics(BaseModel):
    character_count: int
    word_count: int
    token_count: int
    tokens_per_word: float
    tokens_per_character: float


class TokenizationResult(BaseModel):
    text: str
    encoding: SupportedEncoding
    source_type: SourceType
    tokens: list[Token]
    statistics: TokenStatistics


class TextTokenizeRequest(BaseModel):
    text: str
    encoding: SupportedEncoding


class EncodingsResponse(BaseModel):
    encodings: list[SupportedEncoding]


class ErrorResponse(BaseModel):
    error_code: str
    detail: str
