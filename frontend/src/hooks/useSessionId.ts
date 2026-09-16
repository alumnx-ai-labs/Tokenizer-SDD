import { useState } from "react";

const STORAGE_KEY = "tokenizer-session-id";

function loadOrCreateSessionId(): string {
  try {
    const existing = localStorage.getItem(STORAGE_KEY);
    if (existing) {
      return existing;
    }
    const created = crypto.randomUUID();
    localStorage.setItem(STORAGE_KEY, created);
    return created;
  } catch {
    return crypto.randomUUID();
  }
}

export function useSessionId(): string {
  const [sessionId] = useState<string>(loadOrCreateSessionId);
  return sessionId;
}
