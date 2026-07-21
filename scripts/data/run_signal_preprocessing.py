#!/usr/bin/env python3
"""Import -> QC -> preprocessing v0.1 cho một session."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SEMGC_PATH = ROOT / "packages" / "semg-core"
INGESTION_PATH = ROOT / "services" / "signal-ingestion-service" / "src"
QC_PATH = ROOT / "services" / "quality-gate-service" / "src"
PREPROCESS_PATH = ROOT / "services" / "preprocessing-service" / "src"
for path in (SEMGC_PATH, INGESTION_PATH, QC_PATH, PREPROCESS_PATH):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from importers.csv_importer import CSVImporter  # noqa: E402
from config_loader import load_protocol, load_qc_config  # noqa: E402
from quality_gate import QualityGate, build_import_rejected_result  # noqa: E402
from preprocess_config import load_preprocess_config  # noqa: E402
from pipeline import PreprocessingPipeline  # noqa: E402


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
    parser.add_argument(
        "--preprocess-config",
        type=Path,
        default=Path("services/preprocessing-service/configs/preprocess_v0.1.yaml"),
    )
    parser.add_argument("--summary-out", type=Path)
    parser.add_argument("--npz-out", type=Path)
    parser.add_argument("--json-output", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--expect-status", choices=("completed", "blocked"))
    parser.add_argument("--expect-step", action="append", default=[])
    parser.add_argument("--expect-skipped-step", action="append", default=[])
    parser.add_argument("--expect-reason", action="append", default=[])
    return parser.parse_args()


def _session_id(path: Path) -> str:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return "UNKNOWN_SESSION"
    return str(raw.get("session_id") or "UNKNOWN_SESSION") if isinstance(raw, dict) else "UNKNOWN_SESSION"


def _save_npz(path: Path, result: Any) -> None:
    if result.signal is None:
        raise ValueError("Không thể lưu NPZ khi preprocessing bị block")
    payload: dict[str, np.ndarray] = {"time_s": result.signal.time_s}
    for channel_id, channel in result.signal.channels.items():
        safe = re.sub(r"[^A-Za-z0-9_]", "_", channel_id)
        payload[f"channel_{safe}_uV"] = channel.samples_uV
        payload[f"channel_{safe}_valid_mask"] = channel.valid_sample_mask
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **payload)


def _expectations(payload: dict[str, Any], args: argparse.Namespace) -> list[str]:
    errors: list[str] = []
    if args.expect_status and payload["status"] != args.expect_status:
        errors.append(f"Expected status={args.expect_status}; observed={payload['status']}")
    step_status = {item["step_id"]: item["status"] for item in payload["steps"]}
    for step in args.expect_step:
        if step_status.get(step) != "applied":
            errors.append(f"Expected applied step not observed: {step}")
    for step in args.expect_skipped_step:
        if step_status.get(step) != "skipped":
            errors.append(f"Expected skipped step not observed: {step}")
    reasons = set(payload.get("reason_codes", []))
    for reason in args.expect_reason:
        if reason not in reasons:
            errors.append(f"Expected reason not observed: {reason}")
    return errors


def main() -> int:
    args = parse_args()
    try:
        protocol = load_protocol(args.protocol)
        qc_config = load_qc_config(args.qc_config)
        preprocess_config = load_preprocess_config(args.preprocess_config)
    except Exception as exc:
        print(f"CONFIG ERROR: {exc}", file=sys.stderr)
        return 2

    importer = CSVImporter()
    imported = importer.import_session(args.manifest)
    if not imported.ok or imported.signal is None:
        qc_result = build_import_rejected_result(
            session_id=_session_id(args.manifest),
            blocking_codes=imported.blocking_codes,
            warning_codes=imported.warning_codes,
            issue_details=[issue.to_dict() for issue in imported.issues],
        )
        # Tạo object giả tối thiểu là không an toàn; vì không có NormalizedSignal,
        # CLI trả về payload block trực tiếp theo contract preprocessing.
        payload = {
            "schema_version": "preprocessing-result.v0.1",
            "session_id": qc_result.session_id,
            "status": "blocked",
            "downstream_allowed": False,
            "config": {"config_id": "preprocess_v0.1", "execution_mode": "offline_zero_phase"},
            "inherited_qc": {"status": qc_result.status, "reason_codes": list(qc_result.reason_codes)},
            "reason_codes": ["PREPROCESSING_BLOCKED_BY_QC", *qc_result.reason_codes],
            "steps": [],
            "signal_summary": None,
            "limitations": ["Import bị từ chối nên preprocessing không chạy."],
        }
        result = None
    else:
        qc_result = QualityGate(qc_config).run(imported.signal, protocol)
        result = PreprocessingPipeline(preprocess_config).run(imported.signal, qc_result)
        payload = result.to_dict()

    if args.summary_out:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
            encoding="utf-8",
        )
    if args.npz_out:
        if result is None or result.signal is None:
            print("NPZ ERROR: preprocessing không tạo signal", file=sys.stderr)
            return 4
        _save_npz(args.npz_out, result)

    if args.json_output:
        print(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False))
    elif not args.quiet:
        print(
            f"PREPROCESSING {payload['status'].upper()}: session={payload['session_id']} "
            f"downstream_allowed={payload['downstream_allowed']}"
        )
        for step in payload["steps"]:
            print(f"- {step['step_id']}: {step['status']}")
        if payload["signal_summary"]:
            print(
                "combined_output_hash_sha256="
                + payload["signal_summary"]["combined_output_hash_sha256"]
            )

    errors = _expectations(payload, args)
    if errors:
        for error in errors:
            print(f"EXPECTATION FAILED: {error}", file=sys.stderr)
        return 3
    if args.expect_status:
        return 0
    return 0 if payload["downstream_allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
