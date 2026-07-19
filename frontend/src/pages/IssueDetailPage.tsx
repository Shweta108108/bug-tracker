import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import * as commentsApi from "../api/comments";
import type { Comment } from "../api/comments";
import * as issuesApi from "../api/issues";
import type { Issue, IssuePriority, IssueStatus } from "../api/issues";
import * as projectsApi from "../api/projects";
import type { Member } from "../api/projects";
import { CommentComposer } from "../components/comments/CommentComposer";
import { CommentThread } from "../components/comments/CommentThread";
import { IssueMeta } from "../components/issues/IssueMeta";
import { NavBar } from "../components/layout/NavBar";
import { Button } from "../components/ui/Button";
import { Input, Textarea } from "../components/ui/Input";
import { useToast } from "../components/ui/ToastProvider";
import { useAuth } from "../auth/AuthContext";
import { ApiError } from "../types";

export default function IssueDetailPage() {
  const { issueId: issueIdParam } = useParams();
  const issueId = Number(issueIdParam);
  const navigate = useNavigate();
  const { user } = useAuth();
  const { showSuccess, showError } = useToast();

  const [issue, setIssue] = useState<Issue | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [isMaintainer, setIsMaintainer] = useState(false);
  const [comments, setComments] = useState<Comment[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setIsLoading(true);
      try {
        const loadedIssue = await issuesApi.getIssue(issueId);
        if (cancelled) return;
        setIssue(loadedIssue);
        setEditTitle(loadedIssue.title);
        setEditDescription(loadedIssue.description ?? "");

        const [project, memberRows, commentRows] = await Promise.all([
          projectsApi.getProject(loadedIssue.project_id),
          projectsApi.listMembers(loadedIssue.project_id),
          commentsApi.listComments(issueId),
        ]);
        if (cancelled) return;
        setIsMaintainer(project.role === "maintainer");
        setMembers(memberRows);
        setComments(commentRows);
      } catch (err) {
        if (!cancelled) {
          showError(err instanceof ApiError ? err.message : "Failed to load issue.");
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [issueId]);

  const canEditContent = Boolean(issue && user && (isMaintainer || issue.reporter.id === user.id));

  async function applyPatch(
    patch: Partial<{
      title: string;
      description: string | null;
      status: IssueStatus;
      priority: IssuePriority;
      assignee_id: number | null;
    }>,
  ) {
    if (!issue) return;
    try {
      const updated = await issuesApi.updateIssue(issue.id, patch);
      setIssue(updated);
      showSuccess("Issue updated.");
    } catch (err) {
      showError(err instanceof ApiError ? err.message : "Failed to update issue.");
    }
  }

  async function handleSaveEdit() {
    setIsSaving(true);
    await applyPatch({ title: editTitle, description: editDescription || null });
    setIsSaving(false);
    setIsEditing(false);
  }

  async function handleDelete() {
    if (!issue) return;
    if (!window.confirm("Delete this issue? This cannot be undone.")) return;
    try {
      await issuesApi.deleteIssue(issue.id);
      showSuccess("Issue deleted.");
      navigate(`/projects/${issue.project_id}/issues`);
    } catch (err) {
      showError(err instanceof ApiError ? err.message : "Failed to delete issue.");
    }
  }

  if (isLoading || !issue) {
    return (
      <div className="min-h-screen bg-slate-50">
        <NavBar />
        <p className="p-8 text-sm text-slate-500">Loading…</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <NavBar />
      <div className="mx-auto max-w-3xl px-6 py-8">
        <Link to={`/projects/${issue.project_id}/issues`} className="text-sm text-slate-500 hover:underline">
          ← Back to issues
        </Link>

        <div className="mt-2 flex items-start justify-between gap-4">
          {!isEditing ? (
            <h1 className="text-xl font-semibold text-slate-900">{issue.title}</h1>
          ) : (
            <div className="w-full">
              <Input
                id="edit-title"
                label="Title"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
              />
            </div>
          )}
          <div className="flex shrink-0 gap-2">
            {canEditContent && !isEditing && (
              <Button variant="secondary" onClick={() => setIsEditing(true)}>
                Edit
              </Button>
            )}
            {isMaintainer && (
              <Button variant="danger" onClick={handleDelete}>
                Delete
              </Button>
            )}
          </div>
        </div>

        {!isEditing ? (
          <p className="mt-3 whitespace-pre-wrap text-sm text-slate-700">
            {issue.description || "No description."}
          </p>
        ) : (
          <div className="mt-3 space-y-3">
            <Textarea
              id="edit-description"
              label="Description"
              rows={4}
              value={editDescription}
              onChange={(e) => setEditDescription(e.target.value)}
            />
            <div className="flex justify-end gap-2">
              <Button variant="secondary" onClick={() => setIsEditing(false)}>
                Cancel
              </Button>
              <Button isLoading={isSaving} onClick={handleSaveEdit}>
                Save
              </Button>
            </div>
          </div>
        )}

        <div className="mt-6">
          <IssueMeta
            issue={issue}
            members={members}
            isMaintainer={isMaintainer}
            canEditPriority={canEditContent}
            onChange={applyPatch}
          />
        </div>

        <div className="mt-6 rounded-lg border border-slate-200 bg-white p-4">
          <h2 className="text-sm font-semibold text-slate-900">Comments</h2>
          <div className="mt-3">
            <CommentThread comments={comments} />
          </div>
          <CommentComposer
            issueId={issue.id}
            onAdded={(comment) => setComments((current) => [...current, comment])}
          />
        </div>
      </div>
    </div>
  );
}
