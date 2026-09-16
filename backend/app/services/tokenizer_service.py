import tiktoken

from app.schemas.tokenize import SourceType, Token, TokenizationResult, TokenStatistics


def tokenize(text: str, encoding: str, source_type: SourceType) -> TokenizationResult:
    enc = tiktoken.get_encoding(encoding)
    token_ids = enc.encode(text)

    tokens = []
    for index, token_id in enumerate(token_ids):
        token_bytes = enc.decode_single_token_bytes(token_id)
        tokens.append(
            Token(
                index=index,
                token_id=token_id,
                decoded_text=token_bytes.decode("utf-8", errors="replace"),
                token_bytes=list(token_bytes),
            )
        )

    character_count = len(text)
    word_count = len(text.split())
    token_count = len(tokens)

    statistics = TokenStatistics(
        character_count=character_count,
        word_count=word_count,
        token_count=token_count,
        tokens_per_word=(token_count / word_count) if word_count else 0.0,
        tokens_per_character=(token_count / character_count) if character_count else 0.0,
    )

    return TokenizationResult(
        text=text,
        encoding=encoding,
        source_type=source_type,
        tokens=tokens,
        statistics=statistics,
    )
