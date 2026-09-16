from app.schemas.tokenize import SourceType
from app.services.tokenizer_service import tokenize


def test_tokenize_known_string():
    result = tokenize("Hello world", "cl100k_base", SourceType.text)

    assert result.statistics.token_count == len(result.tokens)
    assert result.statistics.token_count > 0
    assert result.statistics.character_count == len("Hello world")
    assert result.statistics.word_count == 2

    for index, token in enumerate(result.tokens):
        assert token.index == index
        assert isinstance(token.token_id, int)
        assert isinstance(token.decoded_text, str)
        assert isinstance(token.token_bytes, list)
        assert all(isinstance(b, int) and 0 <= b <= 255 for b in token.token_bytes)
        assert bytes(token.token_bytes).decode("utf-8", errors="replace") == token.decoded_text

    assert result.statistics.tokens_per_word == (
        result.statistics.token_count / result.statistics.word_count
    )
    assert result.statistics.tokens_per_character == (
        result.statistics.token_count / result.statistics.character_count
    )


def test_tokenize_single_character_single_word():
    result = tokenize("a", "cl100k_base", SourceType.text)

    assert result.statistics.character_count == 1
    assert result.statistics.word_count == 1
    assert result.statistics.token_count >= 1
