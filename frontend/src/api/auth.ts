import type { User } from "../types";
import { apiFetch } from "./client";

interface TokenResponse {
  access_token: string;
  token_type: string;
}

export function signup(name: string, email: string, password: string): Promise<User> {
  return apiFetch<User>("/auth/signup", { method: "POST", body: { name, email, password } });
}

export function login(email: string, password: string): Promise<TokenResponse> {
  return apiFetch<TokenResponse>("/auth/login", { method: "POST", body: { email, password } });
}

export function getMe(): Promise<User> {
  return apiFetch<User>("/me");
}
