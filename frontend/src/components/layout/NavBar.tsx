import { Link } from "react-router-dom";
import { useAuth } from "../../auth/AuthContext";

export function NavBar() {
  const { user, logout } = useAuth();

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <Link to="/projects" className="text-lg font-semibold text-slate-900">
          IssueHub
        </Link>
        <div className="flex items-center gap-4">
          <span className="text-sm text-slate-600">{user?.name}</span>
          <button onClick={logout} className="text-sm font-medium text-slate-900 underline">
            Log out
          </button>
        </div>
      </div>
    </header>
  );
}
