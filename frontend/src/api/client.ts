import type {
  ApiErrorResponse,
  CustomTokenizationResult,
  EncodingsResponse,
  ResetResponse,
  SupportedEncoding,
  TokenizationResult,
  VocabularyResponse,
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_TOKENIZER_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  error_code: string;
  detail: string;

  constructor(error_code: string, detail: string) {
    super(detail);
    this.error_code = error_code;
    this.detail = detail;
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let body: ApiErrorResponse;
    try {
      body = await response.json();
    } catch {
      throw new ApiError(
        "internal_error",
        `Unexpected response from server (status ${response.status}).`
      );
    }
    throw new ApiError(body.error_code ?? "internal_error", body.detail ?? "An unknown error occurred.");
  }
  return response.json() as Promise<T>;
}

export async function getEncodings(): Promise<SupportedEncoding[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/encodings`);
  const body = await handleResponse<EncodingsResponse>(response);
  return body.encodings;
}

export async function tokenizeText(
  text: string,
  encoding: SupportedEncoding
): Promise<TokenizationResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/tokenize/text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, encoding }),
  });
  return handleResponse<TokenizationResult>(response);
}

export async function tokenizeFile(
  file: File,
  encoding: SupportedEncoding
): Promise<TokenizationResult> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("encoding", encoding);
  const response = await fetch(`${API_BASE_URL}/api/v1/tokenize/file`, {
    method: "POST",
    body: formData,
  });
  return handleResponse<TokenizationResult>(response);
}

export async function customTokenizeText(
  text: string,
  sessionId: string
): Promise<CustomTokenizationResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/custom-tokenizer/tokenize/text`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Session-Id": sessionId },
    body: JSON.stringify({ text }),
  });
  return handleResponse<CustomTokenizationResult>(response);
}

export async function customTokenizeFile(
  file: File,
  sessionId: string
): Promise<CustomTokenizationResult> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_BASE_URL}/api/v1/custom-tokenizer/tokenize/file`, {
    method: "POST",
    headers: { "X-Session-Id": sessionId },
    body: formData,
  });
  return handleResponse<CustomTokenizationResult>(response);
}

export async function getVocabulary(sessionId: string): Promise<VocabularyResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/custom-tokenizer/vocabulary`, {
    headers: { "X-Session-Id": sessionId },
  });
  return handleResponse<VocabularyResponse>(response);
}

export async function resetVocabulary(sessionId: string): Promise<ResetResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/custom-tokenizer/reset`, {
    method: "POST",
    headers: { "X-Session-Id": sessionId },
  });
  return handleResponse<ResetResponse>(response);
}
