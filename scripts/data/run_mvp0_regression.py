#!/usr/bin/env python3
"""Chạy regression matrix MVP-0 và tạo evidence JSON/Markdown.

Script này chỉ tạo software/analytical evidence trên synthetic fixtures.
Nó không ước lượng clinical performance.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import shutil
import sys
from typing import Any, Mapping

import numpy as np
import scipy
import yaml

ROOT = Path(__file__).resolve().parents[2]
PIPELINES = ROOT / "ai-core/pipelines"
if str(PIPELINES) not in sys.path:
    sys.path.insert(0, str(PIPELINES))

from analysis_manifest import canonical_json_sha256
from offline_analysis import run_offline_analysis


class RegressionProfileError(ValueError):
    pass


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_regression_profile(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping):
        raise RegressionProfileError("Regression profile phải là object/map")
    profile = dict(raw)
    if profile.get("schema_version") != "mvp0-regression-profile.v0.1":
        raise RegressionProfileError("Sai schema_version")
    if profile.get("profile_id") != "mvp0_regression_v0.1":
        raise RegressionProfileError("Sai profile_id")
    if profile.get("clinical_validation_status") != "not_validated":
        raise RegressionProfileError("clinical_validation_status phải là not_validated")
    scenarios = profile.get("scenarios")
    order = profile.get("scenario_order")
    if not isinstance(scenarios, Mapping) or not isinstance(order, list):
        raise RegressionProfileError("Thiếu scenarios/scenario_order")
    if set(order) != set(scenarios):
        raise RegressionProfileError("scenario_order không khớp scenarios")
    repeat = profile.get("repeatability", {})
    if repeat.get("scenario_id") not in scenarios or int(repeat.get("reruns", 0)) < 2:
        raise RegressionProfileError("Repeatability config không hợp lệ")
    return profile


def scan_forbidden_keys(payload: Any, forbidden: set[str], path: str = "root") -> list[str]:
    hits: list[str] = []
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            key_s = str(key)
            if key_s in forbidden:
                hits.append(f"{path}.{key_s}")
            hits.extend(scan_forbidden_keys(value, forbidden, f"{path}.{key_s}"))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            hits.extend(scan_forbidden_keys(value, forbidden, f"{path}[{index}]"))
    return hits


def within_range(value: float, bounds: list[float] | tuple[float, float]) -> bool:
    low, high = float(bounds[0]), float(bounds[1])
    return low <= float(value) <= high


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_package(analysis_dir: Path, manifest: Mapping[str, Any], forbidden: set[str]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    all_payloads: list[Any] = [manifest]
    for record in manifest["pipeline"]["stage_records"]:
        target = analysis_dir / record["output_file"]
        exists = target.is_file()
        checks.append({"check_id": f"stage_file:{record['stage_id']}", "passed": exists})
        if exists:
            payload = load_json(target)
            all_payloads.append(payload)
            actual_hash = canonical_json_sha256(payload)
            checks.append({
                "check_id": f"stage_hash:{record['stage_id']}",
                "passed": actual_hash == record["output_payload_sha256"],
                "expected": record["output_payload_sha256"],
                "actual": actual_hash,
            })
    hits: list[str] = []
    for payload in all_payloads:
        hits.extend(scan_forbidden_keys(payload, forbidden))
    checks.append({"check_id": "forbidden_key_scan", "passed": not hits, "hits": hits})
    checks.append({
        "check_id": "clinical_use_disabled",
        "passed": manifest["final"]["clinical_use_allowed"] is False,
    })
    checks.append({
        "check_id": "human_review_required",
        "passed": manifest["final"]["human_review_required"] is True,
    })
    return {"passed": all(item["passed"] for item in checks), "checks": checks}


def extract_trend_percent_changes(trend_payload: Mapping[str, Any]) -> dict[str, float]:
    channels = trend_payload.get("channels", [])
    if not channels:
        return {}
    trends = channels[0].get("trends", {})
    result: dict[str, float] = {}
    for feature in ("rms", "mav", "mdf", "mnf"):
        record = trends.get(feature, {})
        metrics = record.get("metrics") or {}
        summary = metrics.get("early_late_summary") or {}
        pct = summary.get("percent_change") or {}
        value = pct.get("value")
        if value is not None:
            result[feature] = float(value)
    return result


def scenario_signature(manifest: Mapping[str, Any], qc: Mapping[str, Any], inference: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "analysis_status": manifest["status"],
        "qc_status": qc["status"],
        "qc_reason_codes": list(qc.get("reason_codes", [])),
        "technical_conclusion": manifest["final"]["technical_conclusion"],
        "confidence_category": manifest["final"]["engineering_confidence_category"],
        "inference_status": inference["status"],
        "final_downstream_allowed": bool(inference.get("downstream_allowed", False)),
        "stage_statuses": {
            item["stage_id"]: {
                "status": item["status"],
                "downstream_allowed": bool(item["downstream_allowed"]),
            }
            for item in manifest["pipeline"]["stage_records"]
        },
    }


def check_expected(actual: Mapping[str, Any], expected: Mapping[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for key in (
        "qc_status", "analysis_status", "technical_conclusion",
        "confidence_category", "inference_status", "final_downstream_allowed",
    ):
        checks.append({
            "check_id": f"expected:{key}",
            "passed": actual.get(key) == expected.get(key),
            "expected": expected.get(key),
            "actual": actual.get(key),
        })
    expected_reasons = set(expected.get("qc_reason_codes", []))
    actual_reasons = set(actual.get("qc_reason_codes", []))
    checks.append({
        "check_id": "expected:qc_reason_codes",
        "passed": expected_reasons.issubset(actual_reasons),
        "expected_subset": sorted(expected_reasons),
        "actual": sorted(actual_reasons),
    })
    return checks


def stable_report_payload(report: Mapping[str, Any]) -> dict[str, Any]:
    """Lấy phần dùng tính regression fingerprint, bỏ runtime/timestamp/path."""
    return {
        "schema_version": report["schema_version"],
        "profile_id": report["profile"]["profile_id"],
        "profile_sha256": report["profile"]["profile_sha256"],
        "evidence_scope": report["evidence_scope"],
        "clinical_validation_status": report["clinical_validation_status"],
        "passed": report["passed"],
        "scenarios": [
            {
                "scenario_id": item["scenario_id"],
                "passed": item["passed"],
                "signature": item["signature"],
                "numeric_anchors": item.get("numeric_anchors"),
            }
            for item in report["scenarios"]
        ],
        "repeatability": report["repeatability"],
        "safety_summary": report["safety_summary"],
    }


def render_markdown(report: Mapping[str, Any], title: str) -> str:
    lines = [
        f"# {title}", "",
        f"- **Profile:** `{report['profile']['profile_id']}`",
        f"- **Kết quả:** {'PASS' if report['passed'] else 'FAIL'}",
        f"- **Phạm vi evidence:** `{report['evidence_scope']}`",
        f"- **Clinical validation:** `{report['clinical_validation_status']}`",
        f"- **Regression fingerprint:** `{report['regression_fingerprint_sha256']}`",
        "", "## Ma trận scenario", "",
        "| Scenario | QC | Analysis | Kết luận kỹ thuật | Confidence | Kết quả |",
        "|---|---|---|---|---|---|",
    ]
    for item in report["scenarios"]:
        sig = item["signature"]
        lines.append(
            f"| `{item['scenario_id']}` | `{sig['qc_status']}` | `{sig['analysis_status']}` | "
            f"`{sig['technical_conclusion']}` | `{sig['confidence_category']}` | "
            f"{'PASS' if item['passed'] else 'FAIL'} |"
        )
    lines += [
        "", "## Repeatability", "",
        f"- Cùng analysis fingerprint: `{report['repeatability']['same_analysis_fingerprint']}`",
        f"- Cùng stage payload hashes: `{report['repeatability']['same_stage_payload_hashes']}`",
        "", "## Giới hạn", "",
    ]
    for item in report["limitations"]:
        lines.append(f"- {item}")
    lines += [
        "", "## Kết luận", "",
        "Báo cáo này chỉ chứng minh software/analytical regression trên synthetic fixtures. "
        "Nó không chứng minh clinical validity, clinical utility hoặc model performance trên dữ liệu người bệnh.", "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--markdown-out", type=Path, required=True)
    parser.add_argument("--validation-report", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    profile_path = args.profile if args.profile.is_absolute() else ROOT / args.profile
    profile = load_regression_profile(profile_path)
    output_root = args.output_root if args.output_root.is_absolute() else ROOT / args.output_root
    if output_root.exists() and args.overwrite:
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    forbidden = set(str(x) for x in profile["forbidden_keys"])
    scenario_results: list[dict[str, Any]] = []
    manifests_by_id: dict[str, dict[str, Any]] = {}

    for scenario_id in profile["scenario_order"]:
        cfg = profile["scenarios"][scenario_id]
        manifest_path = Path(cfg["manifest"])
        manifest_path = manifest_path if manifest_path.is_absolute() else ROOT / manifest_path
        run_dir = output_root / ("golden-run-1" if scenario_id == "golden" else scenario_id.replace("_", "-"))
        if run_dir.exists():
            shutil.rmtree(run_dir)
        manifest = run_offline_analysis(
            manifest_path=manifest_path,
            output_dir=run_dir,
            config_path=ROOT / profile["pipeline_config"],
        )
        manifests_by_id[scenario_id] = manifest
        qc = load_json(run_dir / "01-qc-result.json")
        inference = load_json(run_dir / "10-explainable-inference.json")
        signature = scenario_signature(manifest, qc, inference)
        checks = check_expected(signature, cfg["expected"])
        package = verify_package(run_dir, manifest, forbidden)
        checks.append({"check_id": "package_integrity", "passed": package["passed"]})
        numeric_anchors = None
        if scenario_id == "golden":
            time_payload = load_json(run_dir / "04-time-domain-features.json")
            freq_payload = load_json(run_dir / "06-frequency-features.json")
            trend_payload = load_json(run_dir / "07-trend-features.json")
            anchors_cfg = profile["synthetic_golden_numeric_anchors"]
            changes = extract_trend_percent_changes(trend_payload)
            confidence = float(inference["technical_confidence"]["final_score_0_to_1"])
            numeric_checks = [
                {"check_id": "time_domain_row_count", "passed": time_payload["summary"]["computed_row_count"] == int(anchors_cfg["time_domain_row_count"]), "actual": time_payload["summary"]["computed_row_count"]},
                {"check_id": "frequency_domain_row_count", "passed": freq_payload["summary"]["computed_row_count"] == int(anchors_cfg["frequency_domain_row_count"]), "actual": freq_payload["summary"]["computed_row_count"]},
                {"check_id": "computed_trend_channel_count", "passed": trend_payload["summary"]["computed_channel_count"] == int(anchors_cfg["computed_trend_channel_count"]), "actual": trend_payload["summary"]["computed_channel_count"]},
                {"check_id": "engineering_confidence_range", "passed": within_range(confidence, anchors_cfg["engineering_confidence_range"]), "actual": confidence, "expected_range": anchors_cfg["engineering_confidence_range"]},
            ]
            for feature, bounds in anchors_cfg["percent_change_ranges"].items():
                value = changes.get(feature)
                numeric_checks.append({
                    "check_id": f"percent_change_range:{feature}",
                    "passed": value is not None and within_range(value, bounds),
                    "actual": value,
                    "expected_range": bounds,
                })
            checks.extend(numeric_checks)
            numeric_anchors = {"percent_changes": changes, "engineering_confidence": confidence, "checks": numeric_checks}
        scenario_results.append({
            "scenario_id": scenario_id,
            "manifest_file": manifest_path.name,
            "analysis_fingerprint_sha256": manifest["analysis_fingerprint_sha256"],
            "passed": all(item["passed"] for item in checks),
            "signature": signature,
            "checks": checks,
            "package_verification": package,
            "numeric_anchors": numeric_anchors,
        })

    repeat_cfg = profile["repeatability"]
    golden_manifest_path = ROOT / profile["scenarios"][repeat_cfg["scenario_id"]]["manifest"]
    rerun_dir = output_root / "golden-run-2"
    if rerun_dir.exists():
        shutil.rmtree(rerun_dir)
    golden_2 = run_offline_analysis(
        manifest_path=golden_manifest_path,
        output_dir=rerun_dir,
        config_path=ROOT / profile["pipeline_config"],
    )
    golden_1 = manifests_by_id[repeat_cfg["scenario_id"]]
    hashes_1 = {x["stage_id"]: x["output_payload_sha256"] for x in golden_1["pipeline"]["stage_records"]}
    hashes_2 = {x["stage_id"]: x["output_payload_sha256"] for x in golden_2["pipeline"]["stage_records"]}
    repeatability = {
        "scenario_id": repeat_cfg["scenario_id"],
        "rerun_count": 2,
        "same_analysis_fingerprint": golden_1["analysis_fingerprint_sha256"] == golden_2["analysis_fingerprint_sha256"],
        "same_stage_payload_hashes": hashes_1 == hashes_2,
        "analysis_fingerprints": [golden_1["analysis_fingerprint_sha256"], golden_2["analysis_fingerprint_sha256"]],
        "stage_payload_hashes_run_1": hashes_1,
        "stage_payload_hashes_run_2": hashes_2,
    }
    safety_summary = {
        "all_packages_integrity_passed": all(x["package_verification"]["passed"] for x in scenario_results),
        "all_fail_scenarios_abstained": all(
            x["signature"]["technical_conclusion"] == "abstained"
            for x in scenario_results if x["scenario_id"].startswith("fail_")
        ),
        "all_warning_scenarios_propagated": all(
            x["signature"]["analysis_status"] == "completed_with_warnings"
            for x in scenario_results if x["scenario_id"].startswith("warning_")
        ),
    }
    report: dict[str, Any] = {
        "schema_version": "mvp0-regression-report.v0.1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "profile": {
            "profile_id": profile["profile_id"],
            "profile_sha256": file_sha256(profile_path),
            "pipeline_config": profile["pipeline_config"],
            "pipeline_config_sha256": file_sha256(ROOT / profile["pipeline_config"]),
        },
        "evidence_scope": profile["evidence_scope"],
        "clinical_validation_status": profile["clinical_validation_status"],
        "passed": all(x["passed"] for x in scenario_results)
            and repeatability["same_analysis_fingerprint"]
            and repeatability["same_stage_payload_hashes"]
            and all(safety_summary.values()),
        "scenarios": scenario_results,
        "repeatability": repeatability,
        "safety_summary": safety_summary,
        "runtime_versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "limitations": list(profile.get("limitations", [])),
    }
    report["regression_fingerprint_sha256"] = canonical_json_sha256(stable_report_payload(report))

    json_out = args.json_out if args.json_out.is_absolute() else ROOT / args.json_out
    md_out = args.markdown_out if args.markdown_out.is_absolute() else ROOT / args.markdown_out
    validation_out = args.validation_report if args.validation_report.is_absolute() else ROOT / args.validation_report
    for target in (json_out, md_out, validation_out):
        target.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    md_text = render_markdown(report, "Báo cáo regression MVP-0 — Day 16")
    md_out.write_text(md_text, encoding="utf-8")
    validation_text = render_markdown(report, "Analytical Validation Report MVP-0") + "\n## Quyết định Gate 4\n\n" + (
        "**PASS ở mức technical offline MVP-0.** Chưa được phép suy rộng thành clinical validation.\n"
        if report["passed"] else
        "**FAIL.** Không chuyển sang API contract trước khi xử lý regression failures.\n"
    )
    validation_out.write_text(validation_text, encoding="utf-8")
    print("MVP-0 REGRESSION:", "PASS" if report["passed"] else "FAIL")
    print("Regression fingerprint:", report["regression_fingerprint_sha256"])
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
