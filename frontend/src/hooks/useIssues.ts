import { useCallback, useEffect, useState } from "react";
import * as issuesApi from "../api/issues";
import type { Issue, IssueListParams } from "../api/issues";
import type { Paginated } from "../types";

export function useIssues(projectId: number, params: IssueListParams) {
  const [data, setData] = useState<Paginated<Issue> | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const paramsKey = JSON.stringify(params);

  const reload = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      setData(await issuesApi.listIssues(projectId, params));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load issues.");
    } finally {
      setIsLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId, paramsKey]);

  useEffect(() => {
    void reload();
  }, [reload]);

  return { data, isLoading, error, reload };
}
