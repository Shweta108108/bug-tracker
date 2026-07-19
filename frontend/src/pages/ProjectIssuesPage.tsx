import { useEffect, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import * as projectsApi from "../api/projects";
import type { Member } from "../api/projects";
import type { Issue, IssueListParams } from "../api/issues";
import { AddMemberForm } from "../components/projects/AddMemberForm";
import { MemberList } from "../components/projects/MemberList";
import { IssueFilters } from "../components/issues/IssueFilters";
import { IssueRow } from "../components/issues/IssueRow";
import { NewIssueModal } from "../components/issues/NewIssueModal";
import { Pagination } from "../components/issues/Pagination";
import { NavBar } from "../components/layout/NavBar";
import { Button } from "../components/ui/Button";
import { useToast } from "../components/ui/ToastProvider";
import { useIssues } from "../hooks/useIssues";
import { useProject } from "../hooks/useProject";
import { useDebouncedValue } from "../hooks/useDebouncedValue";

const PAGE_SIZE = 20;

export default function ProjectIssuesPage() {
  const { projectId: projectIdParam } = useParams();
  const projectId = Number(projectIdParam);
  const { showError } = useToast();
  const { project, isLoading: isProjectLoading } = useProject(projectId);
  const [members, setMembers] = useState<Member[]>([]);
  const [isNewIssueOpen, setIsNewIssueOpen] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();

  const rawSearch = searchParams.get("q") ?? "";
  const debouncedSearch = useDebouncedValue(rawSearch, 300);

  const params: IssueListParams = {
    q: debouncedSearch || undefined,
    status: (searchParams.get("status") as IssueListParams["status"]) ?? "",
    priority: (searchParams.get("priority") as IssueListParams["priority"]) ?? "",
    assignee_id: searchParams.get("assignee_id") ? Number(searchParams.get("assignee_id")) : "",
    sort: searchParams.get("sort") ?? "-created_at",
    page: Number(searchParams.get("page")) || 1,
    page_size: PAGE_SIZE,
  };

  const { data, isLoading, error, reload } = useIssues(projectId, params);

  useEffect(() => {
    projectsApi
      .listMembers(projectId)
      .then(setMembers)
      .catch(() => showError("Failed to load project members."));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId]);

  useEffect(() => {
    if (error) showError(error);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [error]);

  function patchParams(patch: Record<string, string | number | undefined>) {
    const next = new URLSearchParams(searchParams);
    for (const [key, value] of Object.entries(patch)) {
      if (value === undefined || value === "") {
        next.delete(key);
      } else {
        next.set(key, String(value));
      }
    }
    if (!("page" in patch)) {
      next.delete("page");
    }
    setSearchParams(next);
  }

  function handleIssueCreated(_issue: Issue) {
    setIsNewIssueOpen(false);
    reload();
  }

  const isMaintainer = project?.role === "maintainer";

  return (
    <div className="min-h-screen bg-slate-50">
      <NavBar />
      <div className="mx-auto max-w-5xl px-6 py-8">
        <Link to="/projects" className="text-sm text-slate-500 hover:underline">
          ← Projects
        </Link>

        {isProjectLoading && <p className="mt-2 text-sm text-slate-500">Loading…</p>}

        {project && (
          <>
            <div className="mt-2 flex items-center justify-between">
              <div>
                <h1 className="text-xl font-semibold text-slate-900">
                  {project.name} <span className="text-slate-400">· {project.key}</span>
                </h1>
                {project.description && <p className="text-sm text-slate-600">{project.description}</p>}
              </div>
              <Button onClick={() => setIsNewIssueOpen(true)}>New issue</Button>
            </div>

            {isMaintainer && (
              <div className="mt-6 rounded-lg border border-slate-200 bg-white p-4">
                <h2 className="text-sm font-semibold text-slate-900">Manage members</h2>
                <div className="mt-3">
                  <AddMemberForm
                    projectId={projectId}
                    onAdded={(member) => setMembers((current) => [...current, member])}
                  />
                </div>
                <div className="mt-3">
                  <MemberList members={members} />
                </div>
              </div>
            )}

            <div className="mt-6 rounded-lg border border-slate-200 bg-white p-4">
              <IssueFilters
                value={{ ...params, q: rawSearch }}
                onChange={(patch) =>
                  patchParams(patch as Record<string, string | number | undefined>)
                }
                assigneeOptions={members.map((m) => ({
                  value: String(m.user.id),
                  label: m.user.name,
                }))}
              />
            </div>

            <div className="mt-4 rounded-lg border border-slate-200 bg-white">
              {isLoading && <p className="p-4 text-sm text-slate-500">Loading issues…</p>}
              {!isLoading && data && data.items.length === 0 && (
                <p className="p-4 text-sm text-slate-600">No issues match your filters.</p>
              )}
              {!isLoading && data && data.items.length > 0 && (
                <ul className="divide-y divide-slate-200">
                  {data.items.map((issue) => (
                    <li key={issue.id}>
                      <IssueRow issue={issue} projectId={projectId} />
                    </li>
                  ))}
                </ul>
              )}
              {data && (
                <Pagination
                  page={data.page}
                  pageSize={data.page_size}
                  total={data.total}
                  onPageChange={(page) => patchParams({ page })}
                />
              )}
            </div>
          </>
        )}
      </div>

      {isNewIssueOpen && project && (
        <NewIssueModal
          projectId={projectId}
          members={members}
          onClose={() => setIsNewIssueOpen(false)}
          onCreated={handleIssueCreated}
        />
      )}
    </div>
  );
}
