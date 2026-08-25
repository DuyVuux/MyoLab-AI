'use client';

import { useMemo } from 'react';
import { AutomationRepositoryProvider, createAutomationRepository } from '@/data/automation';
import { AutoDataIntakeWorkspace } from '@/features/auto-data-intake';
import { LIVE_AUTOMATION_ENDPOINTS } from '@/lib/api/automation/live-endpoints.generated';

const apiBaseUrl = process.env.NEXT_PUBLIC_AUTOMATION_API_BASE_URL ?? '';

export default function AutoIntakePage() {
  const repository = useMemo(
    () => createAutomationRepository({
      mode: 'real',
      apiBaseUrl,
      endpoints: LIVE_AUTOMATION_ENDPOINTS,
    }),
    [],
  );

  return (
    <AutomationRepositoryProvider repository={repository}>
      <AutoDataIntakeWorkspace />
    </AutomationRepositoryProvider>
  );
}
