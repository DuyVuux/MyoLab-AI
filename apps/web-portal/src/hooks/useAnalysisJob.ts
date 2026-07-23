import { useEffect, useRef, useState } from "react";

import type { AnalysisClient } from "../lib/analysis-client";
import { pollingDelayMs } from "../lib/pollingSchedule";
import type { AnalysisJob } from "../schemas/analysis-job.schema";
import { isTerminalAnalysisStatus } from "../schemas/analysis-job.schema";

export interface UseAnalysisJobResult {
  readonly job: AnalysisJob | null;
  readonly loading: boolean;
  readonly error: string | null;
}

export function useAnalysisJob(client: AnalysisClient, analysisId: string | null): UseAnalysisJobResult {
  const [job, setJob] = useState<AnalysisJob | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const attemptRef = useRef(0);

  useEffect(() => {
    if (!analysisId) return;
    let cancelled = false;
    let timeoutId: ReturnType<typeof setTimeout> | null = null;
    attemptRef.current = 0;
    setLoading(true);
    setError(null);

    const poll = async (): Promise<void> => {
      try {
        const next = await client.getJob(analysisId);
        if (cancelled) return;
        setJob(next);
        setLoading(false);
        if (!isTerminalAnalysisStatus(next.status)) {
          const delay = pollingDelayMs(attemptRef.current++);
          timeoutId = setTimeout(() => { void poll(); }, delay);
        }
      } catch (reason) {
        if (cancelled) return;
        setLoading(false);
        setError(reason instanceof Error ? reason.message : "ANALYSIS_POLL_FAILED");
      }
    };
    void poll();
    return () => {
      cancelled = true;
      if (timeoutId !== null) clearTimeout(timeoutId);
    };
  }, [analysisId, client]);

  return { job, loading, error };
}
