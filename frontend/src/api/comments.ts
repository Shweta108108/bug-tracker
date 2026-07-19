import type { User } from "../types";
import { apiFetch } from "./client";

export interface Comment {
  id: number;
  issue_id: number;
  author: User;
  body: string;
  created_at: string;
}

export function listComments(issueId: number): Promise<Comment[]> {
  return apiFetch<Comment[]>(`/issues/${issueId}/comments`);
}

export function addComment(issueId: number, body: string): Promise<Comment> {
  return apiFetch<Comment>(`/issues/${issueId}/comments`, { method: "POST", body: { body } });
}
