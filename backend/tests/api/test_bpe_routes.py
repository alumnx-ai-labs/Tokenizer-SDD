from fastapi.testclient import TestClient

from app.core.config import MAX_UPLOAD_BYTES
from app.main import app

client = TestClient(app)


# --- POST /api/v1/bpe/train ---


def test_train_success():
    response = client.post(
        "/api/v1/bpe/train",
        json={"training_text": "ab ab ab", "vocab_size": 10},
        headers={"X-Session-Id": "train-session-1"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "vocabulary" in body
    assert "merge_rules" in body
    assert "training_log" in body
    assert body["vocabulary_size"] == len(body["vocabulary"])


def test_train_missing_session_id():
    response = client.post(
        "/api/v1/bpe/train", json={"training_text": "ab ab ab", "vocab_size": 10}
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "missing_session_id"


def test_train_empty_text():
    response = client.post(
        "/api/v1/bpe/train",
        json={"training_text": "   ", "vocab_size": 10},
        headers={"X-Session-Id": "train-session-2"},
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "empty_input"


def test_train_text_too_large():
    oversized_text = "a" * (MAX_UPLOAD_BYTES + 1)
    response = client.post(
        "/api/v1/bpe/train",
        json={"training_text": oversized_text, "vocab_size": 10},
        headers={"X-Session-Id": "train-session-3"},
    )
    assert response.status_code == 413
    assert response.json()["error_code"] == "upload_too_large"


def test_train_vocab_size_zero_is_rejected():
    response = client.post(
        "/api/v1/bpe/train",
        json={"training_text": "ab ab ab", "vocab_size": 0},
        headers={"X-Session-Id": "train-session-4"},
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "invalid_vocab_size"


def test_train_vocab_size_negative_is_rejected():
    response = client.post(
        "/api/v1/bpe/train",
        json={"training_text": "ab ab ab", "vocab_size": -5},
        headers={"X-Session-Id": "train-session-5"},
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "invalid_vocab_size"


def test_train_vocab_size_at_or_below_base_symbol_count_is_rejected():
    response = client.post(
        "/api/v1/bpe/train",
        json={"training_text": "abcd", "vocab_size": 4},
        headers={"X-Session-Id": "train-session-6"},
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "invalid_vocab_size"


def test_train_vocab_size_over_max_is_rejected():
    response = client.post(
        "/api/v1/bpe/train",
        json={"training_text": "ab ab ab", "vocab_size": 50_001},
        headers={"X-Session-Id": "train-session-7"},
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "invalid_vocab_size"


def test_train_second_request_while_in_progress_is_rejected():
    from app.services.bpe_service import bpe_service

    session_id = "train-session-8"
    with bpe_service._store.training_slot(session_id):
        response = client.post(
            "/api/v1/bpe/train",
            json={"training_text": "aa aa", "vocab_size": 5},
            headers={"X-Session-Id": session_id},
        )
    assert response.status_code == 409
    assert response.json()["error_code"] == "bpe_training_in_progress"


def test_retraining_replaces_previous_model_via_api():
    session_id = "train-session-9"
    client.post(
        "/api/v1/bpe/train",
        json={"training_text": "aa aa aa", "vocab_size": 3},
        headers={"X-Session-Id": session_id},
    )
    client.post(
        "/api/v1/bpe/train",
        json={"training_text": "bb bb bb", "vocab_size": 3},
        headers={"X-Session-Id": session_id},
    )
    response = client.post(
        "/api/v1/bpe/tokenize/text",
        json={"text": "bb"},
        headers={"X-Session-Id": session_id},
    )
    assert response.status_code == 200
    assert response.json()["tokens"][0]["token_text"] == "bb"


# --- POST /api/v1/bpe/tokenize/text ---


def test_tokenize_success_after_training():
    session_id = "tokenize-session-1"
    client.post(
        "/api/v1/bpe/train",
        json={"training_text": "ab ab ab", "vocab_size": 10},
        headers={"X-Session-Id": session_id},
    )
    response = client.post(
        "/api/v1/bpe/tokenize/text",
        json={"text": "ab"},
        headers={"X-Session-Id": session_id},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["tokens"][0]["token_text"] == "ab"
    assert isinstance(body["tokens"][0]["token_id"], int)


def test_tokenize_without_trained_model_is_rejected():
    response = client.post(
        "/api/v1/bpe/tokenize/text",
        json={"text": "hello"},
        headers={"X-Session-Id": "never-trained-session"},
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "bpe_model_not_trained"


def test_tokenize_empty_text_is_rejected():
    session_id = "tokenize-session-2"
    client.post(
        "/api/v1/bpe/train",
        json={"training_text": "ab ab ab", "vocab_size": 10},
        headers={"X-Session-Id": session_id},
    )
    response = client.post(
        "/api/v1/bpe/tokenize/text",
        json={"text": "   "},
        headers={"X-Session-Id": session_id},
    )
    assert response.status_code == 400
    assert response.json()["error_code"] == "empty_input"


def test_tokenize_missing_session_id():
    response = client.post("/api/v1/bpe/tokenize/text", json={"text": "hello"})
    assert response.status_code == 400
    assert response.json()["error_code"] == "missing_session_id"
