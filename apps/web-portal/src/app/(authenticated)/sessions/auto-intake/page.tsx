'use client';

import { useMemo } from 'react';
import { AutomationRepositoryProvider, createAutomationRepository } from '@/data/automation';
import { AutoDataIntakeWorkspace } from '@/features/auto-data-intake';
import { LIVE_AUTOMATION_ENDPOINTS } from '@/lib/api/automation/live-endpoints.generated';
import styles from '@/features/auto-data-intake/auto-data-intake.module.css';

const apiBaseUrl = process.env.NEXT_PUBLIC_AUTOMATION_API_BASE_URL ?? '';

export default function AutoIntakePage() {
  const repository = useMemo(
    () => apiBaseUrl
      ? createAutomationRepository({
          mode: 'real',
          apiBaseUrl,
          endpoints: LIVE_AUTOMATION_ENDPOINTS,
        })
      : null,
    [],
  );

  if (!repository) {
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
          <span className={styles.state} data-state="BLOCKED">BLOCKED</span>
        </header>

        <div className={styles.error} role="alert">
          <strong>Automation backend is not configured.</strong>
          <p>
            Set NEXT_PUBLIC_AUTOMATION_API_BASE_URL to a verified automation API before importing data.
          </p>
          <p>No downstream result should be assumed from this state.</p>
        </div>
      </section>
    );
  }

  return (
    <AutomationRepositoryProvider repository={repository}>
      <AutoDataIntakeWorkspace />
    </AutomationRepositoryProvider>
  );
}
