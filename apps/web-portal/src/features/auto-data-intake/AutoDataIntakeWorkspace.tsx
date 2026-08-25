"use client";

import { useMemo, useState } from "react";
import type { ImportFormat } from "../../contracts/automation";
import { useAutoDataIntake } from "./useAutoDataIntake";
import styles from "./auto-data-intake.module.css";

type SourceMode = "BROWSER_FILE" | "WORKSPACE_PATH";

export function AutoDataIntakeWorkspace() {
  const controller = useAutoDataIntake();
  const [mode, setMode] = useState<SourceMode>("BROWSER_FILE");
  const [file, setFile] = useState<File | null>(null);
  const [workspacePath, setWorkspacePath] = useState("");
  const [expectedFormat, setExpectedFormat] = useState<ImportFormat>("UNKNOWN");

  const canSubmit =
    !controller.busy &&
    (mode === "BROWSER_FILE" ? file !== null : workspacePath.trim().length > 0);

  const statusText = useMemo(() => {
    switch (controller.uiState) {
      case "IDLE": return "Select a research data source to begin.";
      case "IMPORTING": return "Source is being hashed, detected, parsed and canonicalized.";
      case "WAITING_FOR_PIPELINE": return "Automation pipeline is running.";
      case "PREFLIGHT": return "Waiting for validation evidence.";
      case "MAPPING_REVIEW": return "Automatic mapping needs human resolution.";
      case "QC_RUNNING": return "Quality-control analysis is running.";
      case "QUALITY_READY": return "Quality evidence is ready.";
      case "BLOCKED": return "Automation stopped safely. Review the evidence below.";
      case "FAILED": return "Automation failed safely. No downstream result should be assumed.";
    }
  }, [controller.uiState]);

  return (
    <section className={styles.workspace} aria-labelledby="auto-data-title">
      <header className={styles.header}>
        <div>
          <p className={styles.eyebrow}>DATA AUTOMATION</p>
          <h1 id="auto-data-title">Automated sEMG intake & quality</h1>
          <p className={styles.boundary}>
            Research only · Not clinically validated · Not for clinical use
          </p>
        </div>
        <span className={styles.state} data-state={controller.uiState}>
          {controller.uiState}
        </span>
      </header>

      <div className={styles.card}>
        <h2>1. Source</h2>

        <fieldset className={styles.modeChoice}>
          <legend>Source type</legend>
          <label>
            <input
              type="radio"
              checked={mode === "BROWSER_FILE"}
              onChange={() => {
                setMode("BROWSER_FILE");
                setExpectedFormat("UNKNOWN");
              }}
            />
            Single CSV upload
          </label>
          <label>
            <input
              type="radio"
              checked={mode === "WORKSPACE_PATH"}
              onChange={() => setMode("WORKSPACE_PATH")}
            />
            Workspace file/directory
          </label>
        </fieldset>

        {mode === "BROWSER_FILE" ? (
          <div className={styles.formGrid}>
            <label>
              <span>Noraxon single CSV</span>
              <input
                type="file"
                accept=".csv,text/csv"
                onChange={(event) => setFile(event.target.files?.[0] ?? null)}
              />
            </label>
            <label>
              <span>Expected format</span>
              <select
                value={expectedFormat}
                onChange={(event) => setExpectedFormat(event.target.value as ImportFormat)}
              >
                <option value="UNKNOWN">Auto-detect</option>
                <option value="NORAXON_SINGLE_CSV">Noraxon single CSV</option>
              </select>
            </label>
          </div>
        ) : (
          <div className={styles.formGrid}>
            <label>
              <span>Allowed workspace path</span>
              <input
                type="text"
                value={workspacePath}
                placeholder="/approved/workspace/export"
                onChange={(event) => setWorkspacePath(event.target.value)}
              />
            </label>
            <label>
              <span>Expected format</span>
              <select
                value={expectedFormat}
                onChange={(event) => setExpectedFormat(event.target.value as ImportFormat)}
              >
                <option value="UNKNOWN">Auto-detect</option>
                <option value="NORAXON_SINGLE_CSV">Noraxon single CSV</option>
                <option value="NORAXON_SEPARATED_CSV">Noraxon separated export</option>
              </select>
            </label>
          </div>
        )}

        <p className={styles.help}>
          Separated Noraxon exports are handled as an approved workspace directory in UI-I2;
          the browser must not pretend one CSV represents the complete export.
        </p>

        <button
          type="button"
          disabled={!canSubmit}
          onClick={() => {
            if (mode === "BROWSER_FILE") {
              if (!file) return;
              void controller.upload({
                file,
                expected_format: expectedFormat === "UNKNOWN" ? undefined : expectedFormat,
              });
              return;
            }
            void controller.startWorkspaceImport({
              source_name: workspacePath.split(/[\\/]/).filter(Boolean).at(-1) ?? "workspace-source",
              source_kind: "WORKSPACE_PATH",
              workspace_path: workspacePath,
              expected_format: expectedFormat === "UNKNOWN" ? undefined : expectedFormat,
            });
          }}
        >
          {controller.busy ? "Starting…" : "Import and run automatically"}
        </button>
      </div>

      <div className={styles.card} aria-live="polite">
        <h2>2. Automation status</h2>
        <p>{statusText}</p>

        {controller.importJob && (
          <dl className={styles.details}>
            <div><dt>Import</dt><dd>{controller.importJob.status}</dd></div>
            <div><dt>Format</dt><dd>{controller.importJob.detected_format ?? "Pending"}</dd></div>
            <div><dt>Source hash</dt><dd className={styles.mono}>{controller.importJob.source_hash ?? "Pending"}</dd></div>
            <div><dt>Signals</dt><dd>{controller.importJob.signal_count ?? "Pending"}</dd></div>
          </dl>
        )}

        {controller.pipelineJob?.stages && (
          <ol className={styles.timeline}>
            {controller.pipelineJob.stages.map((stage) => (
              <li key={stage.name}>
                <strong>{stage.name}</strong>
                <span>{stage.status}</span>
                {stage.reason_codes?.length ? <small>{stage.reason_codes.join(", ")}</small> : null}
              </li>
            ))}
          </ol>
        )}
      </div>

      {controller.preflight && (
        <div className={styles.card}>
          <h2>3. Preflight</h2>
          <p>
            <strong>{controller.preflight.overall_status}</strong>
            {" · "}
            {controller.preflight.can_proceed ? "Can proceed" : "Blocked"}
          </p>
          <ul className={styles.list}>
            {controller.preflight.checks.map((check) => (
              <li key={check.check_id}>
                <span>{check.label}</span>
                <strong>{check.status}</strong>
                {check.reason_code ? <code>{check.reason_code}</code> : null}
              </li>
            ))}
          </ul>
        </div>
      )}

      {controller.mapping && (
        <div className={styles.card}>
          <h2>4. Channel mapping</h2>
          <p>{controller.mapping.resolved_count} resolved · {controller.mapping.unresolved_count} need review</p>
          {controller.mapping.unresolved_count === 0 ? (
            <p>All available mappings were resolved automatically.</p>
          ) : (
            <ul className={styles.list}>
              {controller.mapping.candidates
                .filter((item) => item.decision !== "AUTO_MATCHED")
                .map((item) => (
                  <li key={item.vendor_signal_name}>
                    <span>{item.vendor_signal_name}</span>
                    <strong>{item.decision}</strong>
                    {item.reason_code ? <code>{item.reason_code}</code> : null}
                  </li>
                ))}
            </ul>
          )}
        </div>
      )}

      {controller.quality && (
        <div className={styles.card}>
          <h2>5. Quality evidence</h2>
          <p>Overall <strong>{controller.quality.overall_status}</strong></p>
          <p>
            Eligible windows:{" "}
            {controller.quality.eligible_window_fraction == null
              ? "Unknown"
              : `${(controller.quality.eligible_window_fraction * 100).toFixed(1)}%`}
          </p>
          <ul className={styles.list}>
            {controller.quality.findings.map((finding, index) => (
              <li key={finding.finding_id ?? `${finding.reason_code}-${index}`}>
                <span>
                  {finding.channel_id ?? finding.scope}
                  {finding.start_s != null && finding.end_s != null
                    ? ` · ${finding.start_s.toFixed(2)}–${finding.end_s.toFixed(2)} s`
                    : ""}
                </span>
                <strong>{finding.status}</strong>
                <code>{finding.reason_code}</code>
              </li>
            ))}
          </ul>
        </div>
      )}

      {controller.error && (
        <div className={styles.error} role="alert">
          <strong>Automation stopped.</strong>
          <p>{controller.error.message}</p>
          <p>No downstream result should be assumed from this failure.</p>
          <button type="button" onClick={() => void controller.refresh()}>
            Retry status check
          </button>
        </div>
      )}
    </section>
  );
}
