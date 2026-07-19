import type { Paginated, User } from "../types";
import { apiFetch } from "./client";

export type IssueStatus = "open" | "in_progress" | "resolved" | "closed";
export type IssuePriority = "low" | "medium" | "high" | "critical";

export interface Issue {
  id: number;
  project_id: number;
  title: string;
  description: string | null;
  status: IssueStatus;
  priority: IssuePriority;
  reporter: User;
  assignee: User | null;
  created_at: string;
  updated_at: string;
}

export interface IssueListParams {
  q?: string;
  status?: IssueStatus | "";
  priority?: IssuePriority | "";
  assignee_id?: number | "";
  sort?: string;
  page?: number;
  page_size?: number;
}

export function listIssues(projectId: number, params: IssueListParams): Promise<Paginated<Issue>> {
  const search = new URLSearchParams();
  if (params.q) search.set("q", params.q);
  if (params.status) search.set("status", params.status);
  if (params.priority) search.set("priority", params.priority);
  if (params.assignee_id) search.set("assignee_id", String(params.assignee_id));
  if (params.sort) search.set("sort", params.sort);
  if (params.page) search.set("page", String(params.page));
  if (params.page_size) search.set("page_size", String(params.page_size));

  const qs = search.toString();
  return apiFetch<Paginated<Issue>>(`/projects/${projectId}/issues${qs ? `?${qs}` : ""}`);
}

export function createIssue(
  projectId: number,
  input: { title: string; description: string | null; priority: IssuePriority; assignee_id: number | null },
): Promise<Issue> {
  return apiFetch<Issue>(`/projects/${projectId}/issues`, { method: "POST", body: input });
}

export function getIssue(issueId: number): Promise<Issue> {
  return apiFetch<Issue>(`/issues/${issueId}`);
}

export function updateIssue(
  issueId: number,
  patch: Partial<{
    title: string;
    description: string | null;
    status: IssueStatus;
    priority: IssuePriority;
    assignee_id: number | null;
  }>,
): Promise<Issue> {
  return apiFetch<Issue>(`/issues/${issueId}`, { method: "PATCH", body: patch });
}

export function deleteIssue(issueId: number): Promise<void> {
  return apiFetch<void>(`/issues/${issueId}`, { method: "DELETE" });
}
