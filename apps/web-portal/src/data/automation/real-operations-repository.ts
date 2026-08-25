import type { AutomationOperationsRepository } from "./ui-i4-repository";
import type { OperationsSummary } from "../../contracts/automation/operations";
import { parseOperationsSummary } from "../../contracts/automation/ui-i4-validators";
import { AutomationHttpClient } from "../../lib/api/automation/http";
import type { UiI4EndpointCatalog } from "../../lib/api/automation/ui-i4-endpoints";

export class RealOperationsRepository implements AutomationOperationsRepository {
  constructor(
    private readonly http: AutomationHttpClient,
    private readonly endpoints: UiI4EndpointCatalog,
  ) {}

  async getOperationsSummary(): Promise<OperationsSummary> {
    const endpoint = this.endpoints.operations_summary;
    if (endpoint.verification !== "VERIFIED" || !endpoint.template) {
      throw new Error("BACKEND_CONTRACT_NOT_VERIFIED:operations_summary");
    }
    return parseOperationsSummary(
      await this.http.json<unknown>(endpoint.template),
    );
  }
}
