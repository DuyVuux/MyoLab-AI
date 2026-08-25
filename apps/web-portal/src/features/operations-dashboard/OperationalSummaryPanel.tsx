"use client";

import type { OperationsSummary } from "../../contracts/automation/operations";
import styles from "./operations-dashboard.module.css";

const CELLS: Array<{ key: keyof OperationsSummary; label: string }> = [
  { key: "sessions_total", label: "Sessions" },
  { key: "imports_running", label: "Processing" },
  { key: "qc_warning", label: "QC warnings" },
  { key: "blocked", label: "Blocked" },
  { key: "awaiting_review", label: "Awaiting review" },
  { key: "completed", label: "Completed" },
];

export function OperationalSummaryPanel({ summary }: { summary: OperationsSummary }) {
  return (
    <section className={styles.panel} aria-labelledby="operations-summary-title">
      <header className={styles.header}>
        <div>
          <p className={styles.eyebrow}>DATA AUTOMATION</p>
          <h2 id="operations-summary-title">Operational summary</h2>
          <p>Research only · Technical workflow status</p>
        </div>
        <time dateTime={summary.generated_at}>{summary.generated_at}</time>
      </header>

      <div className={styles.grid}>
        {CELLS.map(({ key, label }) => (
          <article className={styles.card} key={String(key)}>
            <span>{label}</span>
            <strong>{String(summary[key])}</strong>
          </article>
        ))}
      </div>

      {summary.limitations.length ? (
        <details>
          <summary>Current limitations</summary>
          <ul>{summary.limitations.map((x) => <li key={x}>{x}</li>)}</ul>
        </details>
      ) : null}
    </section>
  );
}
