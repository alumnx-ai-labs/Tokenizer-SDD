import os

MAX_UPLOAD_BYTES = 5 * 1024 * 1024

SUPPORTED_ENCODINGS = ["cl100k_base", "o200k_base", "p50k_base", "r50k_base"]

FRONTEND_ORIGIN = os.environ.get("TOKENIZER_FRONTEND_ORIGIN", "http://localhost:5173")
