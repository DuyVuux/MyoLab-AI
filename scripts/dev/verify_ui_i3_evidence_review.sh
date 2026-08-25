#!/usr/bin/env bash
set -euo pipefail
cd "${1:-.}"
PYTHON="${PYTHON:-}"
[[ -n "$PYTHON" ]] || { [[ -x .venv/bin/python ]] && PYTHON=.venv/bin/python || PYTHON=python3; }
echo "== UI-I3 route audit =="; set +e; "$PYTHON" scripts/dev/audit_and_promote_ui_i3_contracts.py .; R=$?; set -e
[[ "$R" -eq 0 ]] || { echo "BLOCKED_EVIDENCE_BINDING: required routes are not VERIFIED"; exit 4; }
echo "== UI-I3 real-mode smoke =="; "$PYTHON" scripts/dev/run_ui_i3_live_backend_smoke.py .
echo "== UI-I3 live binding =="; set +e; "$PYTHON" scripts/dev/verify_ui_i3_live_binding.py .; B=$?; set -e
[[ "$B" -eq 0 ]] || { echo "BLOCKED_EVIDENCE_BINDING: live canonical smoke required"; exit 5; }
echo "== UI-I3 API tests =="; "$PYTHON" -m pytest -q qa-validation/automated-tests/test_ui_i3_api_boundary.py
echo "== Frontend type-check =="; pnpm --dir apps/web-portal type-check
echo "== Frontend build =="; pnpm --dir apps/web-portal build
echo "PASS: AUTO_DATA_EVIDENCE_READY"
