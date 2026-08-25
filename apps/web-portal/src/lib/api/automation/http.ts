import { AutomationProblemError, type AutomationProblem } from "../../../contracts/automation/problem";

export interface AutomationHttpClientOptions {
  baseUrl: string;
  fetchImpl?: typeof fetch;
  defaultHeaders?: Record<string, string>;
}

function joinUrl(baseUrl: string, path: string): string {
  return `${baseUrl.replace(/\/$/, "")}/${path.replace(/^\//, "")}`;
}

async function problemFromResponse(response: Response): Promise<AutomationProblem> {
  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }
  const rec = typeof payload === "object" && payload !== null ? payload as Record<string, unknown> : {};
  return {
    code: typeof rec.code === "string" ? rec.code : `HTTP_${response.status}`,
    title: typeof rec.title === "string" ? rec.title : "Automation API request failed",
    message:
      typeof rec.message === "string"
        ? rec.message
        : typeof rec.detail === "string"
          ? rec.detail
          : "The request could not be completed. No downstream result should be assumed.",
    retryable: Boolean(rec.retryable ?? (response.status >= 500 || response.status === 429)),
    evidence_ref: typeof rec.evidence_ref === "string" ? rec.evidence_ref : undefined,
    http_status: response.status,
  };
}

export class AutomationHttpClient {
  private readonly fetchImpl: typeof fetch;
  private readonly baseUrl: string;
  private readonly defaultHeaders: Record<string, string>;

  constructor(options: AutomationHttpClientOptions) {
    this.fetchImpl = options.fetchImpl ?? ((input, init) => fetch(input, init));
    this.baseUrl = options.baseUrl;
    this.defaultHeaders = options.defaultHeaders ?? {};
  }

  private async execute<T>(path: string, init?: RequestInit): Promise<T> {
    const response = await this.fetchImpl(joinUrl(this.baseUrl, path), {
      ...init,
      headers: {
        Accept: "application/json",
        ...(init?.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
        ...this.defaultHeaders,
        ...(init?.headers ?? {}),
      },
    });
    if (!response.ok) {
      throw new AutomationProblemError(await problemFromResponse(response));
    }
    if (response.status === 204) return undefined as T;
    return await response.json() as T;
  }

  json<T>(path: string, init?: RequestInit): Promise<T> {
    return this.execute<T>(path, init);
  }

  form<T>(path: string, body: FormData, init?: Omit<RequestInit, "body">): Promise<T> {
    return this.execute<T>(path, { ...init, method: init?.method ?? "POST", body });
  }
}
