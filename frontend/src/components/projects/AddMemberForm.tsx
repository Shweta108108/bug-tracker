import { useState, type FormEvent } from "react";
import * as projectsApi from "../../api/projects";
import type { Member, ProjectRole } from "../../api/projects";
import { ApiError } from "../../types";
import { Button } from "../ui/Button";
import { Input } from "../ui/Input";
import { Select } from "../ui/Select";
import { useToast } from "../ui/ToastProvider";

interface AddMemberFormProps {
  projectId: number;
  onAdded: (member: Member) => void;
}

export function AddMemberForm({ projectId, onAdded }: AddMemberFormProps) {
  const { showSuccess, showError } = useToast();
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<ProjectRole>("member");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const member = await projectsApi.addMember(projectId, { email, role });
      onAdded(member);
      setEmail("");
      showSuccess(`Added ${member.user.email} as ${member.role}.`);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Failed to add member.";
      setError(message);
      showError(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex items-end gap-2">
      <div className="flex-1">
        <Input
          id="member-email"
          label="Add member by email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          error={error ?? undefined}
        />
      </div>
      <Select
        id="member-role"
        value={role}
        onChange={(e) => setRole(e.target.value as ProjectRole)}
        options={[
          { value: "member", label: "Member" },
          { value: "maintainer", label: "Maintainer" },
        ]}
      />
      <Button type="submit" isLoading={isSubmitting}>
        Add
      </Button>
    </form>
  );
}
