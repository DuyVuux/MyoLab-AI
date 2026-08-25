import type { Identifier, ProvenanceRef } from "./common";
import type { QualityAssessment } from "./quality";
import type { MetricEvidence } from "./metric";

export interface SessionEvidenceBundle {
  session_id: Identifier;
  provenance: ProvenanceRef;
  quality?: QualityAssessment;
  metrics: MetricEvidence[];
  limitations: string[];
  review_case_ids?: Identifier[];
  evidence_refs?: string[];
}
