import type { OperationsSummary } from "../../contracts/automation/operations";

export interface AutomationOperationsRepository {
  getOperationsSummary(): Promise<OperationsSummary>;
}
