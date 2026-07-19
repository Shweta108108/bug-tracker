import { useAuth } from "../auth/AuthContext";

export default function ProjectsListPage() {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-900">Projects</h1>
        <div className="flex items-center gap-4">
          <span className="text-sm text-slate-600">{user?.name}</span>
          <button onClick={logout} className="text-sm font-medium text-slate-900 underline">
            Log out
          </button>
        </div>
      </div>
      <p className="mt-6 text-slate-600">Project list coming in the next milestone.</p>
    </div>
  );
}
