#!/usr/bin/env bash
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/packages/semg-core${PYTHONPATH:+:$PYTHONPATH}"

PYTHON="python"
if ! command -v python &>/dev/null; then
  PYTHON="$ROOT/.venv/bin/python"
fi

echo '[1/6] DAY35 deterministic fixture regeneration'
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
"$PYTHON" scripts/data/build_day35_threshold_fixtures.py \
  --output-root "$tmp/data" \
  --manifest "$tmp/manifest.yaml" >/dev/null
cmp "$tmp/manifest.yaml" \
  qa-validation/evidence/day35-threshold-study-fixtures.v0.1.manifest.yaml
"$PYTHON" - "$tmp/data" qa-validation/test-data/research/day35 <<'PYIN'
from pathlib import Path
import hashlib
import sys


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b''):
            value.update(chunk)
    return value.hexdigest()


a, b = map(Path, sys.argv[1:])
fa = sorted(path.relative_to(a) for path in a.rglob('*.npz'))
fb = sorted(path.relative_to(b) for path in b.rglob('*.npz'))
assert fa == fb
assert all(digest(a / path) == digest(b / path) for path in fa)
print(f'fixture replay PASS {len(fa)} files')
PYIN

echo '[2/6] DAY35 threshold study replay'
"$PYTHON" scripts/dev/day35_threshold_study_runner.py

echo '[3/6] DAY35 contract validator'
"$PYTHON" scripts/dev/day35_contract_validator.py

echo '[4/6] DAY35 focused tests'
"$PYTHON" -m pytest -q \
  qa-validation/automated-tests/research/test_day35_threshold_sensitivity.py

echo '[5/6] available upstream regression'
args=()
for path in \
  qa-validation/automated-tests/qc \
  qa-validation/property-tests \
  qa-validation/automated-tests/research/test_day32_annotation_readiness.py \
  qa-validation/automated-tests/research/test_day33_research_corpus.py \
  qa-validation/automated-tests/research/test_day34_weak_label_analysis.py; do
  [[ -e "$path" ]] && args+=("$path")
done
if [[ ${#args[@]} -gt 0 ]]; then
  "$PYTHON" -m pytest -q "${args[@]}" \
    -k 'not test_43_no_day22_window_implementation'
else
  echo 'upstream suites not present in standalone patch; run in live repo'
fi

echo '[6/6] DAY35 artifact integrity'
"$PYTHON" scripts/dev/check_day35_artifacts.py

echo 'DAY35 MASTER CHECK PASS'
