import type { Comment } from "../../api/comments";

function formatTimestamp(iso: string): string {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(iso));
}

export function CommentThread({ comments }: { comments: Comment[] }) {
  if (comments.length === 0) {
    return <p className="text-sm text-slate-500">No comments yet.</p>;
  }

  return (
    <ul className="space-y-4">
      {comments.map((comment) => (
        <li key={comment.id} className="rounded-md border border-slate-200 p-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-900">{comment.author.name}</span>
            <span className="text-xs text-slate-400">{formatTimestamp(comment.created_at)}</span>
          </div>
          <p className="mt-1 whitespace-pre-wrap text-sm text-slate-700">{comment.body}</p>
        </li>
      ))}
    </ul>
  );
}
