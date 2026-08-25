"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useAutomationRepository } from "../../data/automation";
import type {
  CreateImportRequest,
  ImportJob,
  PipelineJob,
  QualityAssessment,
  SessionMappingState,
  SessionPreflight,
  UploadImportRequest,
} from "../../contracts/automation";
import { AutomationProblemError } from "../../contracts/automation/problem";
import { deriveAutoDataUiState } from "./flow";

export interface AutoDataIntakeController {
  importJob: ImportJob | null;
  pipelineJob: PipelineJob | null;
  preflight: SessionPreflight | null;
  mapping: SessionMappingState | null;
  quality: QualityAssessment | null;
  error: Error | null;
  busy: boolean;
  uiState: ReturnType<typeof deriveAutoDataUiState>;
  upload(request: UploadImportRequest): Promise<void>;
  startWorkspaceImport(request: CreateImportRequest): Promise<void>;
  refresh(): Promise<void>;
  reset(): void;
}

const POLL_MS = 1000;

function isExpectedNotReady(error: unknown): boolean {
  if (!(error instanceof AutomationProblemError)) return false;
  return [404, 409, 425].includes(error.problem.http_status ?? 0);
}

export function useAutoDataIntake(): AutoDataIntakeController {
  const repository = useAutomationRepository();
  const [importJob, setImportJob] = useState<ImportJob | null>(null);
  const [pipelineJob, setPipelineJob] = useState<PipelineJob | null>(null);
  const [preflight, setPreflight] = useState<SessionPreflight | null>(null);
  const [mapping, setMapping] = useState<SessionMappingState | null>(null);
  const [quality, setQuality] = useState<QualityAssessment | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [busy, setBusy] = useState(false);
  const generation = useRef(0);

  const refresh = useCallback(async () => {
    if (!importJob) return;
    const currentGeneration = generation.current;
    try {
      if (importJob.pipeline_job_id) {
        const job = await repository.getPipelineJob(importJob.pipeline_job_id);
        if (currentGeneration !== generation.current) return;
        setPipelineJob(job);
        if (job.status === "FAILED" || job.status === "BLOCKED") return;
      }

      const sessionId = importJob.session_id;
      if (!sessionId) return;

      let currentPreflight: SessionPreflight;
      try {
        currentPreflight = await repository.getPreflight(sessionId);
      } catch (e) {
        if (isExpectedNotReady(e)) return;
        throw e;
      }
      if (currentGeneration !== generation.current) return;
      setPreflight(currentPreflight);
      if (!currentPreflight.can_proceed) return;

      const currentMapping = await repository.getMapping(sessionId);
      if (currentGeneration !== generation.current) return;
      setMapping(currentMapping);
      if (currentMapping.unresolved_count > 0) return;

      const currentQuality = await repository.getQuality(sessionId);
      if (currentGeneration !== generation.current) return;
      setQuality(currentQuality);
    } catch (e) {
      if (currentGeneration !== generation.current) return;
      setError(e instanceof Error ? e : new Error("AUTO_DATA_REFRESH_FAILED"));
    }
  }, [importJob, repository]);

  const begin = useCallback(async (action: () => Promise<ImportJob>) => {
    generation.current += 1;
    setBusy(true);
    setError(null);
    setImportJob(null);
    setPipelineJob(null);
    setPreflight(null);
    setMapping(null);
    setQuality(null);
    try {
      setImportJob(await action());
    } catch (e) {
      setError(e instanceof Error ? e : new Error("AUTO_DATA_IMPORT_FAILED"));
    } finally {
      setBusy(false);
    }
  }, []);

  const upload = useCallback(
    (request: UploadImportRequest) => begin(() => repository.uploadImport(request)),
    [begin, repository],
  );

  const startWorkspaceImport = useCallback(
    (request: CreateImportRequest) => begin(() => repository.createImport(request)),
    [begin, repository],
  );

  const reset = useCallback(() => {
    generation.current += 1;
    setImportJob(null);
    setPipelineJob(null);
    setPreflight(null);
    setMapping(null);
    setQuality(null);
    setError(null);
    setBusy(false);
  }, []);

  useEffect(() => {
    if (!importJob) return;
    const terminal =
      quality !== null ||
      importJob.status === "FAILED" ||
      importJob.status === "BLOCKED" ||
      pipelineJob?.status === "FAILED" ||
      pipelineJob?.status === "BLOCKED";
    if (terminal) return;

    const timer = window.setInterval(() => void refresh(), POLL_MS);
    void refresh();
    return () => window.clearInterval(timer);
  }, [importJob, pipelineJob?.status, quality, refresh]);

  const uiState = useMemo(
    () => deriveAutoDataUiState({ importJob, pipelineJob, preflight, mapping, quality }),
    [importJob, pipelineJob, preflight, mapping, quality],
  );

  return {
    importJob,
    pipelineJob,
    preflight,
    mapping,
    quality,
    error,
    busy,
    uiState,
    upload,
    startWorkspaceImport,
    refresh,
    reset,
  };
}
