import type { User } from "../types";
import { apiFetch } from "./client";

export type ProjectRole = "member" | "maintainer";

export interface Project {
  id: number;
  name: string;
  key: string;
  description: string | null;
  created_at: string;
  role: ProjectRole;
}

export interface Member {
  role: ProjectRole;
  user: User;
}

export function listProjects(): Promise<Project[]> {
  return apiFetch<Project[]>("/projects");
}

export function getProject(projectId: number): Promise<Project> {
  return apiFetch<Project>(`/projects/${projectId}`);
}

export function createProject(input: { name: string; key: string; description: string | null }): Promise<Project> {
  return apiFetch<Project>("/projects", { method: "POST", body: input });
}

export function listMembers(projectId: number): Promise<Member[]> {
  return apiFetch<Member[]>(`/projects/${projectId}/members`);
}

export function addMember(projectId: number, input: { email: string; role: ProjectRole }): Promise<Member> {
  return apiFetch<Member>(`/projects/${projectId}/members`, { method: "POST", body: input });
}
