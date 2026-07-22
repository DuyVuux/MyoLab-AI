#!/usr/bin/env python3
"""Import one Generic CSV session and run Signal Quality Gate v0.1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SEMGC_PATH = ROOT / "packages" / "semg-core"
INGESTION_PATH = ROOT / "services" / "signal-ingestion-service" / "src"
QC_PATH = ROOT / "services" / "quality-gate-service" / "src"
for path in (SEMGC_PATH, INGESTION_PATH, QC_PATH):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from importers.csv_importer import CSVImporter  # type: ignore # noqa: E402
from config_loader import load_protocol, load_qc_config  # type: ignore # noqa: E402
from quality_gate import QualityGate, build_import_rejected_result  # type: ignore # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--protocol",
        type=Path,
        default=Path("clinical/protocols/quad-isometric-60s.v0.1.yaml"),
    )
    parser.add_argument(
        "--qc-config",
        type=Path,
        default=Path("services/quality-gate-service/configs/qc_v0.1.yaml"),
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json-output", action="store_true")
    parser.add_argument("--diagnostic-mode", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument(
        "--expect-status",
        choices=("pass", "warning", "fail", "import_rejected"),
    )
    parser.add_argument(
        "--expect-reason",
        action="append",
        default=[],
        help="Reason code expected in the top-level QC reason_codes array.",
    )
    parser.add_argument(
        "--expect-mfcv-reason",
        action="append",
        default=[],
        help="Reason code expected in mfcv.reason_codes.",
    )
    return parser.parse_args()


def _manifest_session_id(path: Path) -> str:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "UNKNOWN_SESSION"
    if isinstance(raw, dict):
        return str(raw.get("session_id") or "UNKNOWN_SESSION")
    return "UNKNOWN_SESSION"


def _validate_expectations(payload: dict[str, Any], args: argparse.Namespace) -> list[str]:
    errors: list[str] = []
    if args.expect_status and payload["status"] != args.expect_status:
        errors.append(
            f"Expected status={args.expect_status!r}; observed {payload['status']!r}"
        )
    observed_reasons = set(payload.get("reason_codes", []))
    for reason in args.expect_reason:
        if reason not in observed_reasons:
            errors.append(f"Expected top-level reason code not observed: {reason}")
    observed_mfcv = set(payload.get("mfcv", {}).get("reason_codes", []))
    for reason in args.expect_mfcv_reason:
        if reason not in observed_mfcv:
            errors.append(f"Expected MFCV reason code not observed: {reason}")
    return errors


def main() -> int:
    args = parse_args()
    try:
        config = load_qc_config(args.qc_config)
        protocol = load_protocol(args.protocol)
    except (FileNotFoundError, ValueError, OSError, RuntimeError) as exc:
        print(f"CONFIG ERROR: {exc}", file=sys.stderr)
        return 2

    importer = CSVImporter()
    import_result = importer.import_session(args.manifest)
    if not import_result.ok or import_result.signal is None:
        result = build_import_rejected_result(
            session_id=_manifest_session_id(args.manifest),
            blocking_codes=import_result.blocking_codes,
            warning_codes=import_result.warning_codes,
            issue_details=[issue.to_dict() for issue in import_result.issues],
        )
    else:
        gate = QualityGate(config)
        result = gate.run(
            import_result.signal,
            protocol,
            diagnostic_mode=args.diagnostic_mode,
        )

    payload = result.to_dict()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
            encoding="utf-8",
        )

    if args.json_output:
        print(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False))
    elif not args.quiet:
        print(
            f"QC {payload['status'].upper()}: session={payload['session_id']} "
            f"analysis_allowed={payload['analysis_allowed']}"
        )
        print(f"reason_codes={payload['reason_codes']}")
        print(
            f"mfcv.eligible={payload['mfcv']['eligible']} "
            f"mfcv.reason_codes={payload['mfcv']['reason_codes']}"
        )
        for check in payload["checks"]:
            print(
                f"- {check['check_id']}: {check['status']} "
                f"{check['reason_codes']}"
            )

    expectation_errors = _validate_expectations(payload, args)
    if expectation_errors:
        for error in expectation_errors:
            print(f"EXPECTATION FAILED: {error}", file=sys.stderr)
        return 3

    # Without explicit expected outcomes, fail/import_rejected produce non-zero
    # exit codes so shell pipelines stop safely. With --expect-status, a matched
    # negative fixture is an accepted test and exits zero.
    if args.expect_status:
        return 0
    return 0 if payload["analysis_allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
