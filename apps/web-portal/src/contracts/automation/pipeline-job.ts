import type { Identifier, IsoDateTime, PipelineJobStatus } from "./common";

export interface PipelineStage {
  name: string;
  status: PipelineJobStatus;
  started_at?: IsoDateTime;
  finished_at?: IsoDateTime;
  reason_codes?: string[];
}

export interface PipelineJob {
  job_id: Identifier;
  session_id?: Identifier;
  status: PipelineJobStatus;
  current_stage?: string;
  stages?: PipelineStage[];
  reason_codes?: string[];
  evidence_ref?: string;
  updated_at?: IsoDateTime;
}
