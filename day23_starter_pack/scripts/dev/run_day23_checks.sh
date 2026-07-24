#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.."&&pwd)";cd "$ROOT"
for f in services/api-server/src/mock_api/day22_app.py apps/web-portal/src/schemas/gesture-inference.schema.ts docs/plans/DAY23_EXECUTION_PLAN.md;do [[ -f "$f" ]]||{ echo "Thiếu prerequisite/artifact: $f" >&2;exit 1;};done
export PYTHONPATH="$ROOT/services/api-server/src:$ROOT/services/api-server/src/mock_api:$ROOT/packages/semg-core:$ROOT/services/inference-service/src:${PYTHONPATH:-}"
rm -rf .day23-build
echo '[1/5] TypeScript strict';tsc -p qa-validation/configs/day23_tsconfig.json
echo '[2/5] TypeScript runtime';tsc -p qa-validation/configs/day23_runtime_tsconfig.json;node qa-validation/automated-tests/day23_metric_display.test.cjs
echo '[3/5] Python metrics/service/API/schema';pytest -q qa-validation/automated-tests/test_day23_metrics.py qa-validation/automated-tests/test_day23_service_api.py qa-validation/automated-tests/test_day23_schemas.py
echo '[4/5] Capture evidence';python - <<'PYE'
import json,sys
from pathlib import Path
root=Path.cwd();sys.path[:0]=[str(root/'services/api-server/src'),str(root/'services/api-server/src/mock_api'),str(root/'packages/semg-core'),str(root/'services/inference-service/src')]
from services.longitudinal_service import build_assessment
a=build_assessment('golden_uc2_longitudinal').model_dump(mode='json');(root/'qa-validation/evidence').mkdir(parents=True,exist_ok=True);(root/'qa-validation/evidence/day23-uc2-assessment-evidence.json').write_text(json.dumps(a,ensure_ascii=False,indent=2),encoding='utf-8');print(a['status'],a['assessmentId'])
PYE
echo '[5/5] Artifact check';python scripts/dev/check_day23_artifacts.py
rm -rf .day23-build
echo 'All Day 23 checks passed.'
