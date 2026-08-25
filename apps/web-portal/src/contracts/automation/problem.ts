export interface AutomationProblem {
  code: string;
  title: string;
  message: string;
  retryable: boolean;
  evidence_ref?: string;
  http_status?: number;
}

export class AutomationProblemError extends Error {
  readonly problem: AutomationProblem;

  constructor(problem: AutomationProblem) {
    super(`${problem.code}: ${problem.message}`);
    this.name = "AutomationProblemError";
    this.problem = problem;
  }
}

export function contractProblem(message: string, evidenceRef?: string): AutomationProblem {
  return {
    code: "FRONTEND_BACKEND_CONTRACT_MISMATCH",
    title: "Backend response did not match the verified UI contract",
    message,
    retryable: false,
    evidence_ref: evidenceRef,
  };
}
