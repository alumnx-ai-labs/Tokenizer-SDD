import fitz
from fastapi.testclient import TestClient

from app.core.config import MAX_UPLOAD_BYTES
from app.main import app
from app.schemas.custom_tokenizer import VocabularyEntry
from app.services.custom_tokenizer_service import custom_tokenizer_service

client = TestClient(app)


def _build_pdf(text: str | None) -> bytes:
    document = fitz.open()
    page = document.new_page()
    if text:
        page.insert_text((72, 72), text)
    pdf_bytes = document.tobytes()
    document.close()
    return pdf_bytes


# --- POST /api/v1/custom-tokenizer/tokenize/text ---


def test_custom_tokenize_text_success():
    response = client.post(
        "/api/v1/custom-tokenizer/tokenize/text",
        json={"text": "hello developer"},
        headers={"X-Session-Id": "test-session-1"},
    )
    assert response.status_code == 200
    body = response.json()
    is_new_by_text = {t["token_text"]: t["is_new"] for t in body["tokens"]}
    assert is_new_by_text["hello"] is False
    assert is_new_by_text["developer"] is True
    # "hello developer" splits into "hello", "developer" (FR-007); "developer"
    # is the only new vocabulary entry the first time it appears.
    assert body["new_token_count"] == 1


def test_custom_tokenize_missing_session_id():
    response = client.post(
        "/api/v1/custom-tokenizer/tokenize/text", json={"text": "hello"}
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "missing_session_id"


def test_custom_tokenize_empty_text():
    response = client.post(
        "/api/v1/custom-tokenizer/tokenize/text",
        json={"text": "   "},
        headers={"X-Session-Id": "test-session-2"},
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "empty_input"


def test_custom_tokenize_session_isolation():
    client.post(
        "/api/v1/custom-tokenizer/tokenize/text",
        json={"text": "alpha"},
        headers={"X-Session-Id": "session-alpha"},
    )
    response = client.get(
        "/api/v1/custom-tokenizer/vocabulary", headers={"X-Session-Id": "session-beta"}
    )
    vocab_terms = {e["token_text"] for e in response.json()["vocabulary"]}
    assert "alpha" not in vocab_terms


def test_custom_tokenize_invalid_tokenizer_state():
    custom_tokenizer_service._store.update(
        "corrupt-api-session",
        [
            VocabularyEntry(token_id=0, token_text="a", frequency=0, status="initial"),
            VocabularyEntry(token_id=0, token_text="b", frequency=0, status="initial"),
        ],
    )
    response = client.post(
        "/api/v1/custom-tokenizer/tokenize/text",
        json={"text": "a"},
        headers={"X-Session-Id": "corrupt-api-session"},
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "invalid_tokenizer_state"


# --- GET /api/v1/custom-tokenizer/vocabulary ---


def test_get_vocabulary_auto_creates_seed_for_unseen_session():
    response = client.get(
        "/api/v1/custom-tokenizer/vocabulary", headers={"X-Session-Id": "brand-new-session"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["vocabulary_size"] == 3
    assert {e["token_text"] for e in body["vocabulary"]} == {"<UNK>", "hello", "world"}


def test_get_vocabulary_reflects_prior_tokenizations():
    client.post(
        "/api/v1/custom-tokenizer/tokenize/text",
        json={"text": "developer"},
        headers={"X-Session-Id": "session-with-history"},
    )
    response = client.get(
        "/api/v1/custom-tokenizer/vocabulary", headers={"X-Session-Id": "session-with-history"}
    )
    assert any(e["token_text"] == "developer" for e in response.json()["vocabulary"])


# --- POST /api/v1/custom-tokenizer/tokenize/file ---


def test_custom_tokenize_txt_file_success():
    response = client.post(
        "/api/v1/custom-tokenizer/tokenize/file",
        files={"file": ("sample.txt", b"hello developer")},
        headers={"X-Session-Id": "file-session-1"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["text"] == "hello developer"


def test_custom_tokenize_pdf_file_success():
    pdf_bytes = _build_pdf("hello developer")
    response = client.post(
        "/api/v1/custom-tokenizer/tokenize/file",
        files={"file": ("sample.pdf", pdf_bytes)},
        headers={"X-Session-Id": "file-session-2"},
    )
    assert response.status_code == 200


def test_custom_tokenize_file_unsupported_type():
    response = client.post(
        "/api/v1/custom-tokenizer/tokenize/file",
        files={"file": ("data.csv", b"a,b,c")},
        headers={"X-Session-Id": "file-session-3"},
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "unsupported_file_type"


def test_custom_tokenize_file_invalid_pdf():
    response = client.post(
        "/api/v1/custom-tokenizer/tokenize/file",
        files={"file": ("corrupted.pdf", b"not a real pdf")},
        headers={"X-Session-Id": "file-session-4"},
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "invalid_pdf"


def test_custom_tokenize_file_no_extractable_text():
    pdf_bytes = _build_pdf(None)
    response = client.post(
        "/api/v1/custom-tokenizer/tokenize/file",
        files={"file": ("blank.pdf", pdf_bytes)},
        headers={"X-Session-Id": "file-session-5"},
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "no_extractable_text"


def test_custom_tokenize_file_too_large():
    oversized_content = b"a" * (MAX_UPLOAD_BYTES + 1)
    response = client.post(
        "/api/v1/custom-tokenizer/tokenize/file",
        files={"file": ("big.txt", oversized_content)},
        headers={"X-Session-Id": "file-session-6"},
    )
    assert response.status_code == 413
    assert response.json()["error_code"] == "upload_too_large"


# --- POST /api/v1/custom-tokenizer/reset ---


def test_reset_restores_exact_seed_vocabulary():
    session_id = "reset-session"
    client.post(
        "/api/v1/custom-tokenizer/tokenize/text",
        json={"text": "hello developer world"},
        headers={"X-Session-Id": session_id},
    )
    response = client.post(
        "/api/v1/custom-tokenizer/reset", headers={"X-Session-Id": session_id}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["vocabulary_size"] == 3
    assert all(e["frequency"] == 0 for e in body["vocabulary"])

    follow_up = client.get(
        "/api/v1/custom-tokenizer/vocabulary", headers={"X-Session-Id": session_id}
    )
    assert follow_up.json()["vocabulary_size"] == 3
