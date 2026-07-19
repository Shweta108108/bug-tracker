import type { IssueListParams } from "../../api/issues";
import { Select } from "../ui/Select";

interface IssueFiltersProps {
  value: IssueListParams;
  onChange: (patch: Partial<IssueListParams>) => void;
  assigneeOptions: { value: string; label: string }[];
}

const STATUS_OPTIONS = [
  { value: "open", label: "Open" },
  { value: "in_progress", label: "In progress" },
  { value: "resolved", label: "Resolved" },
  { value: "closed", label: "Closed" },
];

const PRIORITY_OPTIONS = [
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
  { value: "critical", label: "Critical" },
];

const SORT_OPTIONS = [
  { value: "-created_at", label: "Newest first" },
  { value: "created_at", label: "Oldest first" },
  { value: "-priority", label: "Priority: high to low" },
  { value: "priority", label: "Priority: low to high" },
  { value: "status", label: "Status" },
];

export function IssueFilters({ value, onChange, assigneeOptions }: IssueFiltersProps) {
  return (
    <div className="flex flex-wrap items-end gap-3">
      <div className="min-w-[200px] flex-1">
        <label className="block text-sm font-medium text-slate-700" htmlFor="issue-search">
          Search
        </label>
        <input
          id="issue-search"
          type="text"
          placeholder="Search by title…"
          value={value.q ?? ""}
          onChange={(e) => onChange({ q: e.target.value })}
          className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
        />
      </div>
      <Select
        label="Status"
        id="filter-status"
        placeholder="Any"
        options={STATUS_OPTIONS}
        value={value.status ?? ""}
        onChange={(e) => onChange({ status: e.target.value as IssueListParams["status"] })}
      />
      <Select
        label="Priority"
        id="filter-priority"
        placeholder="Any"
        options={PRIORITY_OPTIONS}
        value={value.priority ?? ""}
        onChange={(e) => onChange({ priority: e.target.value as IssueListParams["priority"] })}
      />
      <Select
        label="Assignee"
        id="filter-assignee"
        placeholder="Any"
        options={assigneeOptions}
        value={value.assignee_id ? String(value.assignee_id) : ""}
        onChange={(e) => onChange({ assignee_id: e.target.value ? Number(e.target.value) : "" })}
      />
      <Select
        label="Sort"
        id="filter-sort"
        options={SORT_OPTIONS}
        value={value.sort ?? "-created_at"}
        onChange={(e) => onChange({ sort: e.target.value })}
      />
    </div>
  );
}
