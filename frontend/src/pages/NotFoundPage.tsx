import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-2 bg-slate-50 text-slate-600">
      <p className="text-lg font-medium text-slate-900">Page not found</p>
      <Link to="/projects" className="text-sm underline">
        Back to projects
      </Link>
    </div>
  );
}
