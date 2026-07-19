import type { Issue, IssuePriority, IssueStatus } from "../../api/issues";
import type { Member } from "../../api/projects";
import { Select } from "../ui/Select";

function formatTimestamp(iso: string): string {
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(
    new Date(iso),
  );
}

interface IssueMetaProps {
  issue: Issue;
  members: Member[];
  isMaintainer: boolean;
  canEditPriority: boolean;
  onChange: (patch: Partial<{ status: IssueStatus; priority: IssuePriority; assignee_id: number | null }>) => void;
}

export function IssueMeta({ issue, members, isMaintainer, canEditPriority, onChange }: IssueMetaProps) {
  return (
    <div className="grid grid-cols-2 gap-4 rounded-lg border border-slate-200 bg-white p-4 text-sm">
      <div>
        <p className="font-medium text-slate-500">Status</p>
        {isMaintainer ? (
          <Select
            id="meta-status"
            value={issue.status}
            onChange={(e) => onChange({ status: e.target.value as IssueStatus })}
            options={[
              { value: "open", label: "Open" },
              { value: "in_progress", label: "In progress" },
              { value: "resolved", label: "Resolved" },
              { value: "closed", label: "Closed" },
            ]}
          />
        ) : (
          <p className="mt-1 text-slate-900">{issue.status}</p>
        )}
      </div>

      <div>
        <p className="font-medium text-slate-500">Priority</p>
        {canEditPriority ? (
          <Select
            id="meta-priority"
            value={issue.priority}
            onChange={(e) => onChange({ priority: e.target.value as IssuePriority })}
            options={[
              { value: "low", label: "Low" },
              { value: "medium", label: "Medium" },
              { value: "high", label: "High" },
              { value: "critical", label: "Critical" },
            ]}
          />
        ) : (
          <p className="mt-1 text-slate-900">{issue.priority}</p>
        )}
      </div>

      <div>
        <p className="font-medium text-slate-500">Assignee</p>
        {isMaintainer ? (
          <Select
            id="meta-assignee"
            placeholder="Unassigned"
            value={issue.assignee ? String(issue.assignee.id) : ""}
            onChange={(e) => onChange({ assignee_id: e.target.value ? Number(e.target.value) : null })}
            options={members.map((m) => ({ value: String(m.user.id), label: m.user.name }))}
          />
        ) : (
          <p className="mt-1 text-slate-900">{issue.assignee?.name ?? "Unassigned"}</p>
        )}
      </div>

      <div>
        <p className="font-medium text-slate-500">Reporter</p>
        <p className="mt-1 text-slate-900">{issue.reporter.name}</p>
      </div>

      <div>
        <p className="font-medium text-slate-500">Created</p>
        <p className="mt-1 text-slate-900">{formatTimestamp(issue.created_at)}</p>
      </div>

      <div>
        <p className="font-medium text-slate-500">Updated</p>
        <p className="mt-1 text-slate-900">{formatTimestamp(issue.updated_at)}</p>
      </div>
    </div>
  );
}
