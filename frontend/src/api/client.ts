import { ApiError, type ApiErrorBody } from "../types";
import { clearToken, getToken } from "./authToken";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

interface RequestOptions {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  body?: unknown;
}

export async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    method: options.method ?? "GET",
    headers,
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
  });

  if (res.status === 401) {
    clearToken();
    window.dispatchEvent(new CustomEvent("issuehub:unauthorized"));
  }

  if (res.status === 204) {
    return undefined as T;
  }

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    const errorBody: ApiErrorBody = data?.error ?? {
      code: "UNKNOWN_ERROR",
      message: "Something went wrong. Please try again.",
    };
    throw new ApiError(res.status, errorBody);
  }

  return data as T;
}
