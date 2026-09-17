from fastapi import APIRouter, Header

from app.api.custom_tokenizer_routes import require_session_id
from app.schemas.bpe import BPETokenizeRequest, BPETokenizeResult, BPETrainRequest, BPETrainResponse
from app.services import validation
from app.services.bpe_service import bpe_service

router = APIRouter(prefix="/api/v1/bpe")


@router.post("/train", response_model=BPETrainResponse)
def train(
    request: BPETrainRequest, x_session_id: str | None = Header(default=None)
) -> BPETrainResponse:
    session_id = require_session_id(x_session_id)
    return bpe_service.train(session_id, request.training_text, request.vocab_size)


@router.post("/tokenize/text", response_model=BPETokenizeResult)
def tokenize_text(
    request: BPETokenizeRequest, x_session_id: str | None = Header(default=None)
) -> BPETokenizeResult:
    session_id = require_session_id(x_session_id)
    validation.validate_non_empty_text(request.text)
    return bpe_service.tokenize(session_id, request.text)
