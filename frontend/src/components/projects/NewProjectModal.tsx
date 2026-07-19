import { useState, type FormEvent } from "react";
import * as projectsApi from "../../api/projects";
import type { Project } from "../../api/projects";
import { Button } from "../ui/Button";
import { Input } from "../ui/Input";
import { Modal } from "../ui/Modal";
import { useToast } from "../ui/ToastProvider";
import { ApiError } from "../../types";

interface NewProjectModalProps {
  onClose: () => void;
  onCreated: (project: Project) => void;
}

export function NewProjectModal({ onClose, onCreated }: NewProjectModalProps) {
  const { showError } = useToast();
  const [name, setName] = useState("");
  const [key, setKey] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const project = await projectsApi.createProject({
        name,
        key: key.toUpperCase(),
        description: description || null,
      });
      onCreated(project);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Failed to create project.";
      setError(message);
      showError(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <Modal title="New project" onClose={onClose}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          id="project-name"
          label="Name"
          required
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <Input
          id="project-key"
          label="Key"
          required
          maxLength={10}
          value={key}
          onChange={(e) => setKey(e.target.value.toUpperCase())}
          hint="Short uppercase identifier, e.g. WEB, API."
        />
        <Input
          id="project-description"
          label="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" isLoading={isSubmitting}>
            Create project
          </Button>
        </div>
      </form>
    </Modal>
  );
}
