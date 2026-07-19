import { useState, type FormEvent } from "react";
import * as issuesApi from "../../api/issues";
import type { Issue, IssuePriority } from "../../api/issues";
import type { Member } from "../../api/projects";
import { ApiError } from "../../types";
import { Button } from "../ui/Button";
import { Input, Textarea } from "../ui/Input";
import { Modal } from "../ui/Modal";
import { Select } from "../ui/Select";
import { useToast } from "../ui/ToastProvider";

interface NewIssueModalProps {
  projectId: number;
  members: Member[];
  onClose: () => void;
  onCreated: (issue: Issue) => void;
}

export function NewIssueModal({ projectId, members, onClose, onCreated }: NewIssueModalProps) {
  const { showError } = useToast();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<IssuePriority>("medium");
  const [assigneeId, setAssigneeId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const issue = await issuesApi.createIssue(projectId, {
        title,
        description: description || null,
        priority,
        assignee_id: assigneeId ? Number(assigneeId) : null,
      });
      onCreated(issue);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Failed to create issue.";
      setError(message);
      showError(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Modal title="New issue" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input id="issue-title" label="Title" required value={title} onChange={(e) => setTitle(e.target.value)} />
        <Textarea
          id="issue-description"
          label="Description"
          rows={3}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <div className="flex gap-3">
          <Select
            label="Priority"
            id="issue-priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value as IssuePriority)}
            options={[
              { value: "low", label: "Low" },
              { value: "medium", label: "Medium" },
              { value: "high", label: "High" },
              { value: "critical", label: "Critical" },
            ]}
          />
          <Select
            label="Assignee"
            id="issue-assignee"
            placeholder="Unassigned"
            value={assigneeId}
            onChange={(e) => setAssigneeId(e.target.value)}
            options={members.map((m) => ({ value: String(m.user.id), label: m.user.name }))}
          />
        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" isLoading={isSubmitting}>
            Create issue
          </Button>
        </div>
      </form>
    </Modal>
  );
}
