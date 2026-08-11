from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--repo-root', default='.')
    a = p.parse_args()
    root = Path(a.repo_root).resolve()
    required = ['qa-validation/test-data/synthetic/generators/semg_dropout_factory.py', 'qa-validation/test-data/golden/qc/dropout/manifest.yaml', 'qa-validation/automated-tests/qc/test_dropout_detector.py', 'services/quality-gate-service/src/detectors/dropout.py', 'clinical/labels/day23-qc-labeling-function-registry-delta.v0.1.yaml']
    missing = [x for x in required if not (root / x).is_file()]
    upstream = ['packages/common-schemas/json/labeling-function-output.schema.json', 'packages/common-schemas/json/qc-window-identity.schema.json']
    missing_up = [x for x in upstream if not (root / x).is_file()]
    live_window_candidates = [root / 'packages/semg-core/semg_core/qc_windowing.py', root / 'packages/semg-core/src/windowing.py']
    if not any((p.is_file() for p in live_window_candidates)):
        missing_up.append('DAY22 WindowIdentity Python module')
    if missing or missing_up:
        print(json.dumps({'status': 'FAIL', 'missing_day': missing, 'missing_upstream': missing_up}, indent=2))
        return 2
    print(json.dumps({'status': 'PASS', 'day': 23, 'required_artifacts': len(required), 'window_identity_inherited': True, 'labeling_function_output_inherited': True, 'final_qc_deferred_to_day30': True}, indent=2))
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
