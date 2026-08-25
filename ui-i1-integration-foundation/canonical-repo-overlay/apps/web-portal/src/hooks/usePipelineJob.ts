"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { PipelineJob } from "../contracts/automation";
import { useAutomationRepository } from "../data/automation";

export interface UsePipelineJobOptions {
  enabled?: boolean;
  pollMs?: number;
}

export function usePipelineJob(jobId: string | null | undefined, options: UsePipelineJobOptions = {}) {
  const repository = useAutomationRepository();
  const { enabled = true, pollMs = 1500 } = options;
  const generation = useRef(0);
  const [job, setJob] = useState<PipelineJob | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(false);

  const refresh = useCallback(async () => {
    if (!jobId || !enabled) return;
    const current = ++generation.current;
    setLoading(true);
    try {
      const next = await repository.getPipelineJob(jobId);
      if (generation.current === current) {
        setJob(next); setError(null);
      }
    } catch (e) {
      if (generation.current === current) setError(e instanceof Error ? e : new Error(String(e)));
    } finally {
      if (generation.current === current) setLoading(false);
    }
  }, [enabled, jobId, repository]);

  useEffect(() => {
    if (!jobId || !enabled) return;
    void refresh();
    const timer = window.setInterval(() => {
      if (job?.status === "COMPLETED" || job?.status === "FAILED" || job?.status === "BLOCKED") return;
      void refresh();
    }, Math.max(500, pollMs));
    return () => { generation.current += 1; window.clearInterval(timer); };
  }, [enabled, jobId, job?.status, pollMs, refresh]);

  return { job, error, loading, refresh };
}
