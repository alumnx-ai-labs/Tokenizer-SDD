import os

from fastapi import APIRouter, File, Header, UploadFile

from app.core.errors import MissingSessionIdError
from app.schemas.custom_tokenizer import (
    CustomTokenizationResult,
    CustomTokenizeRequest,
    ResetResponse,
    VocabularyResponse,
)
from app.services import validation
from app.services.custom_tokenizer_service import custom_tokenizer_service

router = APIRouter(prefix="/api/v1/custom-tokenizer")


def require_session_id(x_session_id: str | None = Header(default=None)) -> str:
    if not x_session_id:
        raise MissingSessionIdError(
            "An X-Session-Id header is required for Custom Tokenizer requests."
        )
    return x_session_id


@router.post("/tokenize/text", response_model=CustomTokenizationResult)
def custom_tokenize_text(
    request: CustomTokenizeRequest, x_session_id: str | None = Header(default=None)
) -> CustomTokenizationResult:
    session_id = require_session_id(x_session_id)
    validation.validate_upload_size(len(request.text.encode("utf-8")))
    validation.validate_non_empty_text(request.text)
    return custom_tokenizer_service.tokenize(session_id, request.text)


@router.post("/tokenize/file", response_model=CustomTokenizationResult)
async def custom_tokenize_file(
    file: UploadFile = File(...), x_session_id: str | None = Header(default=None)
) -> CustomTokenizationResult:
    session_id = require_session_id(x_session_id)
    file_bytes = await file.read()

    validation.validate_upload_size(len(file_bytes))
    validation.validate_file_extension(file.filename)

    ext = os.path.splitext(file.filename or "")[1].lower()

    if ext == ".pdf":
        from app.services import pdf_service

        text = pdf_service.extract_text(file_bytes)
    else:
        text = validation.decode_text_file_content(file_bytes)

    validation.validate_non_empty_text(text)
    return custom_tokenizer_service.tokenize(session_id, text)


@router.get("/vocabulary", response_model=VocabularyResponse)
def get_vocabulary(x_session_id: str | None = Header(default=None)) -> VocabularyResponse:
    session_id = require_session_id(x_session_id)
    return custom_tokenizer_service.get_vocabulary(session_id)


@router.post("/reset", response_model=ResetResponse)
def reset_vocabulary(x_session_id: str | None = Header(default=None)) -> ResetResponse:
    session_id = require_session_id(x_session_id)
    return custom_tokenizer_service.reset(session_id)
