import os

import fitz
from fastapi.testclient import TestClient

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


def test_user_story_1_paste_text():
    response = client.post(
        "/api/v1/tokenize/text",
        json={"text": "Integration test for pasted text.", "encoding": "cl100k_base"},
    )
    assert response.status_code == 200
    assert response.json()["source_type"] == "text"

    error_response = client.post(
        "/api/v1/tokenize/text", json={"text": "", "encoding": "cl100k_base"}
    )
    assert error_response.status_code == 400


def test_user_story_2_txt_upload():
    response = client.post(
        "/api/v1/tokenize/file",
        files={"file": ("story2.txt", b"Integration test for a txt upload.")},
        data={"encoding": "cl100k_base"},
    )
    assert response.status_code == 200
    assert response.json()["source_type"] == "txt_file"

    error_response = client.post(
        "/api/v1/tokenize/file",
        files={"file": ("story2.csv", b"not,supported")},
        data={"encoding": "cl100k_base"},
    )
    assert error_response.status_code == 400


def test_user_story_3_pdf_upload():
    pdf_bytes = _build_pdf("Integration test for a PDF upload.")
    response = client.post(
        "/api/v1/tokenize/file",
        files={"file": ("story3.pdf", pdf_bytes)},
        data={"encoding": "cl100k_base"},
    )
    assert response.status_code == 200
    assert response.json()["source_type"] == "pdf_file"

    corrupted_response = client.post(
        "/api/v1/tokenize/file",
        files={"file": ("story3.pdf", b"not a real pdf")},
        data={"encoding": "cl100k_base"},
    )
    assert corrupted_response.status_code == 400


def test_statelessness_across_requests():
    repo_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    files_before = set(os.listdir(repo_root))

    first_response = client.post(
        "/api/v1/tokenize/text",
        json={"text": "First unique request payload.", "encoding": "cl100k_base"},
    )
    second_response = client.post(
        "/api/v1/tokenize/text",
        json={"text": "Second, completely different payload.", "encoding": "cl100k_base"},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert "First unique request payload." not in second_response.json()["text"]
    assert second_response.json()["text"] == "Second, completely different payload."

    files_after = set(os.listdir(repo_root))
    assert files_before == files_after


def test_custom_tokenizer_end_to_end_flow_and_reset():
    session_id = "integration-custom-session"

    tokenize_response = client.post(
        "/api/v1/custom-tokenizer/tokenize/text",
        json={"text": "hello integrationword"},
        headers={"X-Session-Id": session_id},
    )
    assert tokenize_response.status_code == 200
    body = tokenize_response.json()
    is_new_by_text = {t["token_text"]: t["is_new"] for t in body["tokens"]}
    assert is_new_by_text["integrationword"] is True

    vocabulary_response = client.get(
        "/api/v1/custom-tokenizer/vocabulary", headers={"X-Session-Id": session_id}
    )
    assert any(
        entry["token_text"] == "integrationword"
        for entry in vocabulary_response.json()["vocabulary"]
    )

    reset_response = client.post(
        "/api/v1/custom-tokenizer/reset", headers={"X-Session-Id": session_id}
    )
    assert reset_response.status_code == 200
    assert reset_response.json()["vocabulary_size"] == 3
    assert not any(
        entry["token_text"] == "integrationword"
        for entry in reset_response.json()["vocabulary"]
    )


def test_custom_tokenizer_session_isolation():
    client.post(
        "/api/v1/custom-tokenizer/tokenize/text",
        json={"text": "isolationword"},
        headers={"X-Session-Id": "integration-session-a"},
    )
    other_session_vocabulary = client.get(
        "/api/v1/custom-tokenizer/vocabulary",
        headers={"X-Session-Id": "integration-session-b"},
    ).json()["vocabulary"]

    assert not any(entry["token_text"] == "isolationword" for entry in other_session_vocabulary)
