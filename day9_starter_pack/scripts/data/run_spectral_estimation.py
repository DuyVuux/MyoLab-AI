#!/usr/bin/env python3
"""Import -> QC -> preprocessing -> windowing -> Welch PSD theo cửa sổ.

Đây là CLI offline MVP-0. Output spectral JSON chứa PSD trong dải 20--400 Hz,
không chứa raw samples, không tính MDF/MNF và không diễn giải mỏi cơ.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PATHS = (
    ROOT / "packages" / "semg-core",
    ROOT / "services" / "signal-ingestion-service" / "src",
    ROOT / "services" / "quality-gate-service" / "src",
    ROOT / "services" / "preprocessing-service" / "src",
    ROOT / "services" / "feature-extraction-service" / "src",
)
for path in reversed(PATHS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from importers.csv_importer import CSVImporter  # noqa: E402
from config_loader import load_protocol, load_qc_config  # noqa: E402
from quality_gate import QualityGate, build_import_rejected_result  # noqa: E402
from preprocess_config import load_preprocess_config  # noqa: E402
from pipeline import PreprocessingPipeline  # noqa: E402
from preprocess_result_models import PreprocessingRunResult  # noqa: E402
from window_config import load_windowing_config  # noqa: E402
from windowing import WindowingPipeline  # noqa: E402
from spectral_config import load_spectral_config  # noqa: E402
from spectral_extractor import SpectralEstimator  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Chạy offline pipeline đến Welch PSD theo frequency windows."
    )
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
    parser.add_argument(
        "--windowing-config",
        type=Path,
        default=Path(
            "services/feature-extraction-service/configs/windowing_v0.1.yaml"
        ),
    )
    parser.add_argument(
        "--spectral-config",
        type=Path,
        default=Path(
            "services/feature-extraction-service/configs/spectral_estimation_v0.1.yaml"
        ),
    )
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--csv-out", type=Path)
    parser.add_argument("--print-json", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument(
        "--expect-status",
        choices=("completed", "completed_with_exclusions", "blocked"),
    )
    parser.add_argument("--expect-total-row-count", type=int)
    parser.add_argument("--expect-computed-row-count", type=int)
    parser.add_argument("--expect-not-computed-row-count", type=int)
    parser.add_argument("--expect-frequency-bin-count", type=int)
    parser.add_argument("--expect-reason", action="append", default=[])
    return parser.parse_args()


def _session_id(path: Path) -> str:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return "UNKNOWN_SESSION"
    if not isinstance(raw, dict):
        return "UNKNOWN_SESSION"
    return str(raw.get("session_id") or "UNKNOWN_SESSION")


def _blocked_preprocess_result(
    session_id: str,
    reason_codes: tuple[str, ...],
) -> PreprocessingRunResult:
    return PreprocessingRunResult(
        session_id=session_id,
        status="blocked",
        downstream_allowed=False,
        config_id="preprocess_v0.1",
        execution_mode="offline_zero_phase",
        inherited_qc_status="import_rejected",
        inherited_qc_reason_codes=reason_codes,
        reason_codes=("PREPROCESSING_BLOCKED_BY_QC", *reason_codes),
        steps=(),
        signal=None,
        limitations=("Import bị từ chối nên không có tín hiệu để ước lượng PSD.",),
    )


def _write_csv(payload: dict[str, Any], output_path: Path) -> None:
    """Xuất bảng tóm tắt spectral, không lặp vector PSD trong CSV."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "spectral_row_id",
        "session_id",
        "channel_id",
        "muscle",
        "side",
        "role",
        "phase_id",
        "profile_id",
        "window_id",
        "window_index",
        "start_time_s",
        "end_time_exclusive_s",
        "center_time_s",
        "sample_count",
        "status",
        "band_power_uV2",
        "full_power_uV2",
        "time_domain_variance_uV2",
        "window_weighted_power_uV2",
        "parseval_ratio",
        "peak_frequency_hz",
        "qa_flags",
        "reason_codes",
        "spectral_estimator_id",
        "windowing_config_id",
        "preprocess_config_id",
        "source_signal_hash_sha256",
        "window_plan_hash_sha256",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in payload.get("rows", []):
            spectral = row.get("spectral") or {}
            writer.writerow(
                {
                    "spectral_row_id": row["spectral_row_id"],
                    "session_id": row["session_id"],
                    "channel_id": row["channel"]["channel_id"],
                    "muscle": row["channel"]["muscle"],
                    "side": row["channel"]["side"],
                    "role": row["channel"]["role"],
                    "phase_id": row["phase_id"],
                    "profile_id": row["profile_id"],
                    "window_id": row["window"]["window_id"],
                    "window_index": row["window"]["window_index"],
                    "start_time_s": row["window"]["start_time_s"],
                    "end_time_exclusive_s": row["window"][
                        "end_time_exclusive_s"
                    ],
                    "center_time_s": row["window"]["center_time_s"],
                    "sample_count": row["window"]["sample_count"],
                    "status": row["status"],
                    "band_power_uV2": spectral.get("band_power", {}).get(
                        "value", ""
                    ),
                    "full_power_uV2": spectral.get("full_power", {}).get(
                        "value", ""
                    ),
                    "time_domain_variance_uV2": spectral.get(
                        "time_domain_variance", {}
                    ).get("value", ""),
                    "parseval_ratio": spectral.get("parseval_ratio", ""),
                    "peak_frequency_hz": spectral.get("peak_frequency", {}).get(
                        "value", ""
                    ),
                    "qa_flags": "|".join(spectral.get("qa_flags", [])),
                    "reason_codes": "|".join(row.get("reason_codes", [])),
                    "spectral_estimator_id": row["provenance"][
                        "spectral_estimator_id"
                    ],
                    "windowing_config_id": row["provenance"][
                        "windowing_config_id"
                    ],
                    "preprocess_config_id": row["provenance"][
                        "preprocess_config_id"
                    ],
                    "source_signal_hash_sha256": row["provenance"][
                        "source_signal_hash_sha256"
                    ],
                    "window_plan_hash_sha256": row["provenance"][
                        "window_plan_hash_sha256"
                    ],
                }
            )


def _expectations(payload: dict[str, Any], args: argparse.Namespace) -> list[str]:
    errors: list[str] = []
    if args.expect_status and payload.get("status") != args.expect_status:
        errors.append(
            f"Expected status={args.expect_status}; observed={payload.get('status')}"
        )
    summary = payload.get("summary") or {}
    for key, expected in (
        ("total_row_count", args.expect_total_row_count),
        ("computed_row_count", args.expect_computed_row_count),
        ("not_computed_row_count", args.expect_not_computed_row_count),
    ):
        if expected is not None and summary.get(key) != expected:
            errors.append(f"Expected {key}={expected}; observed={summary.get(key)}")
    axis = payload.get("frequency_axis") or {}
    if (
        args.expect_frequency_bin_count is not None
        and axis.get("bin_count") != args.expect_frequency_bin_count
    ):
        errors.append(
            "Expected frequency bin count="
            f"{args.expect_frequency_bin_count}; observed={axis.get('bin_count')}"
        )
    observed_reasons = set(payload.get("reason_codes", []))
    for reason in args.expect_reason:
        if reason not in observed_reasons:
            errors.append(f"Expected reason not observed: {reason}")
    return errors


def main() -> int:
    args = parse_args()
    try:
        protocol = load_protocol(args.protocol)
        qc_config = load_qc_config(args.qc_config)
        preprocess_config = load_preprocess_config(args.preprocess_config)
        windowing_config = load_windowing_config(args.windowing_config)
        spectral_config = load_spectral_config(args.spectral_config)
    except Exception as exc:
        print(f"CONFIG ERROR: {exc}", file=sys.stderr)
        return 2

    imported = CSVImporter().import_session(args.manifest)
    if not imported.ok or imported.signal is None:
        qc_result = build_import_rejected_result(
            session_id=_session_id(args.manifest),
            blocking_codes=imported.blocking_codes,
            warning_codes=imported.warning_codes,
            issue_details=[issue.to_dict() for issue in imported.issues],
        )
        preprocessing_result = _blocked_preprocess_result(
            qc_result.session_id,
            qc_result.reason_codes,
        )
    else:
        qc_result = QualityGate(qc_config).run(imported.signal, protocol)
        preprocessing_result = PreprocessingPipeline(preprocess_config).run(
            imported.signal,
            qc_result,
        )

    windowing_result = WindowingPipeline(windowing_config).run(
        preprocessing_result,
        protocol,
    )
    spectral_result = SpectralEstimator(spectral_config).run(windowing_result)
    payload = spectral_result.to_dict()

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
            encoding="utf-8",
        )
    if args.csv_out:
        _write_csv(payload, args.csv_out)

    if args.print_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False))
    elif not args.quiet:
        summary = payload["summary"]
        axis = payload.get("frequency_axis") or {}
        print(
            f"SPECTRAL {payload['status'].upper()}: "
            f"session={payload['session_id']} "
            f"downstream_allowed={payload['downstream_allowed']}"
        )
        print(
            f"rows={summary['total_row_count']} "
            f"computed={summary['computed_row_count']} "
            f"not_computed={summary['not_computed_row_count']} "
            f"usable_ratio={summary['usable_window_ratio']:.6f}"
        )
        if axis:
            print(
                f"frequency_axis={axis['lower_hz']}..{axis['upper_hz']} Hz "
                f"bins={axis['bin_count']} df={axis['bin_spacing_hz']} Hz"
            )
        if payload.get("result_hash_sha256"):
            print("result_hash_sha256=" + payload["result_hash_sha256"])
        for code in payload.get("reason_codes", []):
            print(f"reason={code}")

    errors = _expectations(payload, args)
    if errors:
        for error in errors:
            print(f"EXPECTATION FAILED: {error}", file=sys.stderr)
        return 3
    if args.expect_status:
        return 0
    return 0 if spectral_result.downstream_allowed else 1


if __name__ == "__main__":
    raise SystemExit(main())
