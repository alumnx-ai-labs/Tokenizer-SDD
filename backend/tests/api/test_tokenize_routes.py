import fitz
from fastapi.testclient import TestClient

from app.core.config import MAX_UPLOAD_BYTES
from app.main import app

client = TestClient(app)


def _build_pdf(text: str | None) -> bytes:
    document = fitz.open()
    page = document.new_page()
    if text:
        page.insert_text((72, 72), text)
    pdf_bytes = document.tobytes()
    document.close()
    return pdf_bytes


# --- GET /api/v1/encodings ---


def test_get_encodings():
    response = client.get("/api/v1/encodings")
    assert response.status_code == 200
    assert response.json() == {
        "encodings": ["cl100k_base", "o200k_base", "p50k_base", "r50k_base"]
    }


# --- POST /api/v1/tokenize/text (US1) ---


def test_tokenize_text_success():
    response = client.post(
        "/api/v1/tokenize/text",
        json={"text": "Hello, tokenizer world!", "encoding": "cl100k_base"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["source_type"] == "text"
    assert body["statistics"]["token_count"] == len(body["tokens"])
    for token in body["tokens"]:
        assert isinstance(token["token_bytes"], list)
        assert all(isinstance(b, int) for b in token["token_bytes"])


def test_tokenize_text_empty_input():
    response = client.post(
        "/api/v1/tokenize/text", json={"text": "   ", "encoding": "cl100k_base"}
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "empty_input"


def test_tokenize_text_unsupported_encoding():
    response = client.post(
        "/api/v1/tokenize/text", json={"text": "hi", "encoding": "not_a_real_encoding"}
    )
    assert response.status_code == 422
    assert response.json()["error_code"] == "unsupported_encoding"


def test_tokenize_text_too_large():
    oversized_text = "a" * (MAX_UPLOAD_BYTES + 1)
    response = client.post(
        "/api/v1/tokenize/text",
        json={"text": oversized_text, "encoding": "cl100k_base"},
    )
    assert response.status_code == 413
    assert response.json()["error_code"] == "upload_too_large"


# --- POST /api/v1/tokenize/file with .txt uploads (US2) ---


def test_tokenize_txt_file_success():
    response = client.post(
        "/api/v1/tokenize/file",
        files={"file": ("sample.txt", b"Hello, tokenizer world!")},
        data={"encoding": "cl100k_base"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["source_type"] == "txt_file"
    assert body["text"] == "Hello, tokenizer world!"
    assert all(isinstance(token["token_bytes"], list) for token in body["tokens"])


def test_tokenize_txt_file_empty():
    response = client.post(
        "/api/v1/tokenize/file",
        files={"file": ("empty.txt", b"")},
        data={"encoding": "cl100k_base"},
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "empty_input"


def test_tokenize_file_unsupported_extension():
    response = client.post(
        "/api/v1/tokenize/file",
        files={"file": ("data.csv", b"a,b,c")},
        data={"encoding": "cl100k_base"},
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "unsupported_file_type"


def test_tokenize_file_too_large():
    oversized_content = b"a" * (MAX_UPLOAD_BYTES + 1)
    response = client.post(
        "/api/v1/tokenize/file",
        files={"file": ("big.txt", oversized_content)},
        data={"encoding": "cl100k_base"},
    )
    assert response.status_code == 413
    assert response.json()["error_code"] == "upload_too_large"


def test_tokenize_file_unsupported_encoding():
    response = client.post(
        "/api/v1/tokenize/file",
        files={"file": ("sample.txt", b"hello world")},
        data={"encoding": "not_a_real_encoding"},
    )
    assert response.status_code == 422
    assert response.json()["error_code"] == "unsupported_encoding"


def test_tokenize_txt_file_binary_content_rejected():
    response = client.post(
        "/api/v1/tokenize/file",
        files={"file": ("binary.txt", bytes([0xFF, 0xFE, 0x00, 0x80, 0x81]))},
        data={"encoding": "cl100k_base"},
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "unsupported_file_type"


# --- POST /api/v1/tokenize/file with .pdf uploads (US3) ---


def test_tokenize_pdf_file_success():
    pdf_bytes = _build_pdf("Hello, tokenizer world!")
    response = client.post(
        "/api/v1/tokenize/file",
        files={"file": ("sample.pdf", pdf_bytes)},
        data={"encoding": "cl100k_base"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["source_type"] == "pdf_file"
    assert "Hello" in body["text"]


def test_tokenize_pdf_file_corrupted():
    response = client.post(
        "/api/v1/tokenize/file",
        files={"file": ("corrupted.pdf", b"not a real pdf")},
        data={"encoding": "cl100k_base"},
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "invalid_pdf"


def test_tokenize_pdf_file_no_extractable_text():
    pdf_bytes = _build_pdf(None)
    response = client.post(
        "/api/v1/tokenize/file",
        files={"file": ("blank.pdf", pdf_bytes)},
        data={"encoding": "cl100k_base"},
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "no_extractable_text"
