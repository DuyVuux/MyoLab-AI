#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[2]; REQ=['packages/semg-core/semg_core/fatigue_evidence.py','services/inference-service/evidence/fatigue_evidence_v0.1.yaml','services/inference-service/src/evidence_engine.py','scripts/data/run_fatigue_evidence.py','docs/06-ai-signal-processing/fatigue-evidence-engine-spec.md','qa-validation/requirements/day12-acceptance-criteria.md']
def main():
 m=[x for x in REQ if not (R/x).is_file()]
 if m:raise SystemExit('Thiếu '+str(m))
 c=(R/'services/inference-service/evidence/fatigue_evidence_v0.1.yaml').read_text()
 for x in ['clinical_validation_status: not_validated','do_not_output_fatigue_detected: true','do_not_output_probability: true','do_not_generate_frs: true','do_not_generate_clinical_recommendation: true']:
  if x not in c:raise SystemExit('Thiếu '+x)
 print('Day 12 artifact/safety check: PASS');return 0
if __name__=='__main__':raise SystemExit(main())
