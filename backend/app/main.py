from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.bpe_routes import router as bpe_router
from app.api.custom_tokenizer_routes import router as custom_tokenizer_router
from app.api.tokenize_routes import router
from app.core.errors import register_exception_handlers

app = FastAPI(title="Tokenizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(router)
app.include_router(custom_tokenizer_router)
app.include_router(bpe_router)
