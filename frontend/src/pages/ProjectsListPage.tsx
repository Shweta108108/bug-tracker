import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import * as projectsApi from "../api/projects";
import type { Project } from "../api/projects";
import { NavBar } from "../components/layout/NavBar";
import { NewProjectModal } from "../components/projects/NewProjectModal";
import { Button } from "../components/ui/Button";
import { useToast } from "../components/ui/ToastProvider";

export default function ProjectsListPage() {
  const { showSuccess, showError } = useToast();
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    projectsApi
      .listProjects()
      .then(setProjects)
      .catch(() => showError("Failed to load projects."))
      .finally(() => setIsLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleCreated(project: Project) {
    setProjects((current) => [project, ...current]);
    setIsModalOpen(false);
    showSuccess(`Project "${project.name}" created.`);
    navigate(`/projects/${project.id}/issues`);
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <NavBar />
      <div className="mx-auto max-w-5xl px-6 py-8">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold text-slate-900">Projects</h1>
          <Button onClick={() => setIsModalOpen(true)}>New project</Button>
        </div>

        {isLoading && <p className="mt-6 text-sm text-slate-500">Loading…</p>}

        {!isLoading && projects.length === 0 && (
          <p className="mt-6 text-sm text-slate-600">
            You don't belong to any projects yet. Create one to get started.
          </p>
        )}

        <ul className="mt-6 divide-y divide-slate-200 rounded-lg border border-slate-200 bg-white">
          {projects.map((project) => (
            <li key={project.id}>
              <Link
                to={`/projects/${project.id}/issues`}
                className="flex items-center justify-between px-4 py-3 hover:bg-slate-50"
              >
                <div>
                  <p className="font-medium text-slate-900">
                    {project.name} <span className="text-slate-400">· {project.key}</span>
                  </p>
                  {project.description && (
                    <p className="text-sm text-slate-500">{project.description}</p>
                  )}
                </div>
                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
                  {project.role}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </div>

      {isModalOpen && (
        <NewProjectModal onClose={() => setIsModalOpen(false)} onCreated={handleCreated} />
      )}
    </div>
  );
}
