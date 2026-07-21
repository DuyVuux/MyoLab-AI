#!/usr/bin/env python3
"""Import -> QC -> preprocessing -> hai window profile v0.1."""

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
PREPROCESS_PATH = ROOT / "services" / "preprocessing-service" / "src"
FEATURE_PATH = ROOT / "services" / "feature-extraction-service" / "src"
# Chèn feature path cuối cùng để module windowing.py của service đứng trước.
for path in (SEMGC_PATH, INGESTION_PATH, QC_PATH, PREPROCESS_PATH, FEATURE_PATH):
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Chạy offline pipeline tới segmentation/windowing v0.1."
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
    parser.add_argument("--summary-out", type=Path)
    parser.add_argument("--json-output", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--expect-status", choices=("completed", "blocked"))
    parser.add_argument("--expect-time-window-count", type=int)
    parser.add_argument("--expect-frequency-window-count", type=int)
    parser.add_argument("--expect-time-valid-window-count", type=int)
    parser.add_argument("--expect-frequency-valid-window-count", type=int)
    parser.add_argument("--expect-reason", action="append", default=[])
    return parser.parse_args()


def _session_id(path: Path) -> str:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return "UNKNOWN_SESSION"
    if isinstance(raw, dict):
        return str(raw.get("session_id") or "UNKNOWN_SESSION")
    return "UNKNOWN_SESSION"


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
        limitations=("Import bị từ chối nên không có tín hiệu để windowing.",),
    )


def _profile_map(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    plan = payload.get("plan")
    if not isinstance(plan, dict):
        return {}
    profiles = plan.get("profiles")
    if not isinstance(profiles, list):
        return {}
    return {
        str(item.get("profile_id")): item
        for item in profiles
        if isinstance(item, dict)
    }


def _first_channel_valid_count(profile: dict[str, Any] | None) -> int | None:
    if not profile:
        return None
    channels = profile.get("channels")
    if not isinstance(channels, list) or not channels:
        return None
    value = channels[0].get("valid_window_count")
    return int(value) if isinstance(value, int) else None


def _expectations(payload: dict[str, Any], args: argparse.Namespace) -> list[str]:
    errors: list[str] = []
    if args.expect_status and payload.get("status") != args.expect_status:
        errors.append(
            f"Expected status={args.expect_status}; observed={payload.get('status')}"
        )

    profiles = _profile_map(payload)
    time_profile = profiles.get("time_domain")
    frequency_profile = profiles.get("frequency_domain")

    expected_counts = (
        ("time_domain", time_profile, args.expect_time_window_count),
        ("frequency_domain", frequency_profile, args.expect_frequency_window_count),
    )
    for profile_id, profile, expected in expected_counts:
        if expected is None:
            continue
        observed = (
            profile.get("windowing", {}).get("window_count")
            if isinstance(profile, dict)
            else None
        )
        if observed != expected:
            errors.append(
                f"Expected {profile_id} window_count={expected}; observed={observed}"
            )

    expected_valid = (
        ("time_domain", time_profile, args.expect_time_valid_window_count),
        (
            "frequency_domain",
            frequency_profile,
            args.expect_frequency_valid_window_count,
        ),
    )
    for profile_id, profile, expected in expected_valid:
        if expected is None:
            continue
        observed = _first_channel_valid_count(profile)
        if observed != expected:
            errors.append(
                f"Expected first-channel {profile_id} valid_window_count={expected}; "
                f"observed={observed}"
            )

    observed_reasons = set(payload.get("reason_codes", []))
    for code in args.expect_reason:
        if code not in observed_reasons:
            errors.append(f"Expected reason not observed: {code}")
    return errors


def main() -> int:
    args = parse_args()
    try:
        protocol = load_protocol(args.protocol)
        qc_config = load_qc_config(args.qc_config)
        preprocess_config = load_preprocess_config(args.preprocess_config)
        windowing_config = load_windowing_config(args.windowing_config)
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

    result = WindowingPipeline(windowing_config).run(
        preprocessing_result,
        protocol,
    )
    payload = result.to_dict()

    if args.summary_out:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
            encoding="utf-8",
        )

    if args.json_output:
        print(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False))
    elif not args.quiet:
        print(
            f"WINDOWING {payload['status'].upper()}: session={payload['session_id']} "
            f"downstream_allowed={payload['downstream_allowed']}"
        )
        for profile_id, profile in _profile_map(payload).items():
            windowing = profile["windowing"]
            print(
                f"- profile={profile_id} purpose={profile['purpose']} "
                f"windows={windowing['window_count']} "
                f"L={windowing['window_size_samples']} "
                f"H={windowing['hop_size_samples']}"
            )
            for channel in profile["channels"]:
                print(
                    f"  channel={channel['channel_id']} "
                    f"valid={channel['valid_window_count']} "
                    f"invalid={channel['invalid_window_count']}"
                )
        if payload.get("plan"):
            print("plan_hash_sha256=" + payload["plan"]["plan_hash_sha256"])
        for code in payload.get("reason_codes", []):
            print(f"reason={code}")

    errors = _expectations(payload, args)
    if errors:
        for error in errors:
            print(f"EXPECTATION FAILED: {error}", file=sys.stderr)
        return 3
    if args.expect_status:
        return 0
    return 0 if result.downstream_allowed else 1


if __name__ == "__main__":
    raise SystemExit(main())
