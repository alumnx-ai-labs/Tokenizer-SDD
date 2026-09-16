from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import SUPPORTED_ENCODINGS


class TokenizerError(Exception):
    error_code = "internal_error"
    status_code = 500

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class EmptyInputError(TokenizerError):
    error_code = "empty_input"
    status_code = 400


class UnsupportedFileTypeError(TokenizerError):
    error_code = "unsupported_file_type"
    status_code = 400


class InvalidPDFError(TokenizerError):
    error_code = "invalid_pdf"
    status_code = 400


class NoExtractableTextError(TokenizerError):
    error_code = "no_extractable_text"
    status_code = 400


class UnsupportedEncodingError(TokenizerError):
    error_code = "unsupported_encoding"
    status_code = 422


class UploadTooLargeError(TokenizerError):
    error_code = "upload_too_large"
    status_code = 413


class MissingSessionIdError(TokenizerError):
    error_code = "missing_session_id"
    status_code = 400


class InvalidTokenizerStateError(TokenizerError):
    error_code = "invalid_tokenizer_state"
    status_code = 400


class VocabularyInitError(TokenizerError):
    error_code = "vocabulary_init_error"
    status_code = 500


class MalformedTokenDataError(TokenizerError):
    error_code = "malformed_token_data"
    status_code = 400


def _error_response(request: Request, exc: TokenizerError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "detail": exc.detail},
    )


async def tokenizer_error_handler(request: Request, exc: TokenizerError) -> JSONResponse:
    return _error_response(request, exc)


async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    for error in exc.errors():
        if "encoding" in error.get("loc", ()):
            return JSONResponse(
                status_code=422,
                content={
                    "error_code": "unsupported_encoding",
                    "detail": (
                        "Unsupported encoding. Supported encodings: "
                        f"{', '.join(SUPPORTED_ENCODINGS)}."
                    ),
                },
            )
    return JSONResponse(
        status_code=422,
        content={"error_code": "internal_error", "detail": "Invalid request payload."},
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "internal_error",
            "detail": "An unexpected error occurred while processing the request.",
        },
    )


def register_exception_handlers(app) -> None:
    app.add_exception_handler(TokenizerError, tokenizer_error_handler)
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
