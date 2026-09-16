from fastapi.testclient import TestClient

from app.core.config import FRONTEND_ORIGIN
from app.main import app

client = TestClient(app)


def test_preflight_allows_frontend_origin_for_custom_tokenizer():
    response = client.options(
        "/api/v1/custom-tokenizer/tokenize/text",
        headers={
            "Origin": FRONTEND_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,x-session-id",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == FRONTEND_ORIGIN
    assert "POST" in response.headers["access-control-allow-methods"]
    allowed_headers = response.headers["access-control-allow-headers"].lower()
    assert "content-type" in allowed_headers
    assert "x-session-id" in allowed_headers


def test_simple_get_includes_allow_origin_header():
    response = client.get("/api/v1/encodings", headers={"Origin": FRONTEND_ORIGIN})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == FRONTEND_ORIGIN
