"use client";

import { createContext, useContext, useMemo, type ReactNode } from "react";
import type { AutomationRepository } from "./automation-repository";

const AutomationRepositoryContext = createContext<AutomationRepository | null>(null);

export function AutomationRepositoryProvider(props: { repository: AutomationRepository; children: ReactNode }) {
  const value = useMemo(() => props.repository, [props.repository]);
  return <AutomationRepositoryContext.Provider value={value}>{props.children}</AutomationRepositoryContext.Provider>;
}

export function useAutomationRepository(): AutomationRepository {
  const repository = useContext(AutomationRepositoryContext);
  if (!repository) throw new Error("AutomationRepositoryProvider is missing from the active data-automation UI tree");
  return repository;
}
