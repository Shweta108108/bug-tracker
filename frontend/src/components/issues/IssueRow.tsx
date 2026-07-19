import { Link } from "react-router-dom";
import type { Issue } from "../../api/issues";

const STATUS_LABELS: Record<Issue["status"], string> = {
  open: "Open",
  in_progress: "In progress",
  resolved: "Resolved",
  closed: "Closed",
};

const STATUS_CLASSES: Record<Issue["status"], string> = {
  open: "bg-blue-100 text-blue-700",
  in_progress: "bg-amber-100 text-amber-700",
  resolved: "bg-emerald-100 text-emerald-700",
  closed: "bg-slate-200 text-slate-600",
};

const PRIORITY_CLASSES: Record<Issue["priority"], string> = {
  low: "bg-slate-100 text-slate-600",
  medium: "bg-blue-100 text-blue-700",
  high: "bg-orange-100 text-orange-700",
  critical: "bg-red-100 text-red-700",
};

export function IssueRow({ issue, projectId }: { issue: Issue; projectId: number }) {
  return (
    <Link
      to={`/projects/${projectId}/issues/${issue.id}`}
      className="flex items-center justify-between px-4 py-3 hover:bg-slate-50"
    >
      <div className="min-w-0">
        <p className="truncate font-medium text-slate-900">{issue.title}</p>
        <p className="text-xs text-slate-500">
          Reported by {issue.reporter.name}
          {issue.assignee && ` · Assigned to ${issue.assignee.name}`}
        </p>
      </div>
      <div className="flex shrink-0 items-center gap-2">
        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${PRIORITY_CLASSES[issue.priority]}`}>
          {issue.priority}
        </span>
        <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_CLASSES[issue.status]}`}>
          {STATUS_LABELS[issue.status]}
        </span>
      </div>
    </Link>
  );
}
