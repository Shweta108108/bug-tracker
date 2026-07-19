import { useState, type FormEvent } from "react";
import * as commentsApi from "../../api/comments";
import type { Comment } from "../../api/comments";
import { ApiError } from "../../types";
import { Button } from "../ui/Button";
import { useToast } from "../ui/ToastProvider";

interface CommentComposerProps {
  issueId: number;
  onAdded: (comment: Comment) => void;
}

export function CommentComposer({ issueId, onAdded }: CommentComposerProps) {
  const { showError } = useToast();
  const [body, setBody] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!body.trim()) return;
    setIsSubmitting(true);
    try {
      const comment = await commentsApi.addComment(issueId, body);
      onAdded(comment);
      setBody("");
    } catch (err) {
      showError(err instanceof ApiError ? err.message : "Failed to add comment.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mt-4 space-y-2">
      <textarea
        rows={3}
        placeholder="Add a comment…"
        value={body}
        onChange={(e) => setBody(e.target.value)}
        className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
      />
      <div className="flex justify-end">
        <Button type="submit" isLoading={isSubmitting} disabled={!body.trim()}>
          Comment
        </Button>
      </div>
    </form>
  );
}
