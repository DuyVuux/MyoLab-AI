#!/usr/bin/env python3
from pathlib import Path
R=Path(__file__).resolve().parents[2]
REQ=['packages/semg-core/semg_core/trend.py','services/feature-extraction-service/configs/trend_features_v0.1.yaml','services/feature-extraction-service/src/trend_feature_extractor.py','scripts/data/run_trend_features.py','scripts/data/verify_trend_features.py','docs/06-ai-signal-processing/trend-feature-math-primer.md','docs/06-ai-signal-processing/trend-feature-spec.md','qa-validation/requirements/day11-acceptance-criteria.md']
def main():
 m=[x for x in REQ if not (R/x).is_file()]
 if m: raise SystemExit('Thiếu:\n'+'\n'.join(m))
 c=(R/'services/feature-extraction-service/configs/trend_features_v0.1.yaml').read_text()
 for x in ['clinical_validation_status: not_validated','do_not_emit_inferential_statistics: true','do_not_interpret_fatigue: true','do_not_train_ml: true']:
  if x not in c: raise SystemExit('Thiếu '+x)
 print('Day 11 artifact/safety check: PASS'); return 0
if __name__=='__main__': raise SystemExit(main())
