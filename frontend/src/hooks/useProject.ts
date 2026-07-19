import { useCallback, useEffect, useState } from "react";
import * as projectsApi from "../api/projects";
import type { Project } from "../api/projects";

export function useProject(projectId: number) {
  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      setProject(await projectsApi.getProject(projectId));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load project.");
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { project, isLoading, error, reload };
}
