"""DAY37 evidence-tier-aware QC error analysis.

The module never merges evidence tiers into a single accuracy and distinguishes
final QC gate errors from detector-level surrogate errors and unresolved states.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml

VERSION = "day37-qc-error-analysis.v0.2.0"
CLAIM_SCOPE = "RESEARCH_ONLY"


class Day37Error(ValueError):
    pass


@dataclass(frozen=True)
class StratumRow:
    source: str
    evidence_tier: str
    scope: str
    domain_axis: str
    detector_family: str
    denominator: int
    expected_positive_or_block: int
    actual_positive_or_block: int
    false_allow_or_fn: int
    false_block_or_fp: int
    unresolved: int
    metric_semantics: str
    claim_scope: str = CLAIM_SCOPE


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _int(row: dict[str, str], key: str) -> int:
    value = row.get(key, "")
    return int(float(value)) if value not in {"", None} else 0


def build_day34_strata(performance_csv: Path) -> list[StratumRow]:
    rows: list[StratumRow] = []
    for item in read_csv(performance_csv):
        denominator = _int(item, "scorable_item_count")
        if denominator <= 0:
            raise Day37Error(f"invalid DAY34 denominator for {item['family_id']}")
        rows.append(
            StratumRow(
                source="DAY34_SYNTHETIC_LF",
                evidence_tier="SYNTHETIC_KNOWN_TRUTH",
                scope="WINDOW_DETECTOR_SURROGATE",
                domain_axis="ARTIFACT_FAMILY",
                detector_family=item["family_id"],
                denominator=denominator,
                expected_positive_or_block=_int(item, "scorable_truth_positive_count"),
                actual_positive_or_block=_int(item, "tp") + _int(item, "fp"),
                false_allow_or_fn=_int(item, "fn"),
                false_block_or_fp=_int(item, "fp"),
                unresolved=_int(item, "positive_unresolved") + _int(item, "negative_unresolved"),
                metric_semantics="DETECTOR_FN_FP_NOT_FINAL_QC_ALLOW_BLOCK",
            )
        )
    return rows


def build_day36_strata(results_csv: Path, manifest_yaml: Path) -> list[StratumRow]:
    actual = {row["case_id"]: row for row in read_csv(results_csv)}
    manifest = yaml.safe_load(manifest_yaml.read_text(encoding="utf-8"))
    groups: dict[str, dict[str, int]] = {}
    for case in manifest["cases"]:
        row = actual.get(case["case_id"])
        if row is None:
            raise Day37Error(f"missing DAY36 result {case['case_id']}")
        axis = case["axis"]
        g = groups.setdefault(axis, {"n": 0, "expected": 0, "actual": 0, "fa": 0, "fb": 0, "unresolved": 0})
        expected = bool(case["expected_quality_blocked"])
        observed = row["quality_blocked"] == "True"
        g["n"] += 1
        g["expected"] += int(expected)
        g["actual"] += int(observed)
        g["fa"] += int(expected and not observed)
        g["fb"] += int((not expected) and observed)
        g["unresolved"] += int(row["distribution_support_status"] == "UNKNOWN")
    out = []
    for axis, g in sorted(groups.items()):
        out.append(
            StratumRow(
                source="DAY36_DOMAIN_CHALLENGE",
                evidence_tier="SYNTHETIC_KNOWN_TRUTH",
                scope="WINDOW_QC_GATE",
                domain_axis=axis,
                detector_family="QC_COMPOSITE_SENTINEL",
                denominator=g["n"],
                expected_positive_or_block=g["expected"],
                actual_positive_or_block=g["actual"],
                false_allow_or_fn=g["fa"],
                false_block_or_fp=g["fb"],
                unresolved=g["unresolved"],
                metric_semantics="FINAL_QC_FALSE_ALLOW_FALSE_BLOCK_SENTINEL",
            )
        )
    return out


def validate_strata(rows: Iterable[StratumRow]) -> None:
    for row in rows:
        if row.denominator <= 0:
            raise Day37Error("denominator must be positive")
        for value in (
            row.expected_positive_or_block,
            row.actual_positive_or_block,
            row.false_allow_or_fn,
            row.false_block_or_fp,
            row.unresolved,
        ):
            if value < 0 or value > row.denominator:
                raise Day37Error("metric count outside denominator")
        if row.evidence_tier != "SYNTHETIC_KNOWN_TRUTH":
            raise Day37Error("DAY37 reference evaluation has only synthetic truth")


def build_risk_cases(day34_candidates: Path, day36_results: Path, day36_manifest: Path) -> list[dict[str, Any]]:
    risks: list[dict[str, Any]] = []
    for row in read_csv(day34_candidates):
        reasons = row["selection_reasons"]
        if row["truth_window_misaligned"] == "True":
            category = "CORPUS_TRUTH_GAP"
            severity = 100
        elif "DAY29_HARD_INTEGRITY_OVERRIDE" in reasons:
            category = "HARD_INTEGRITY_CONTROL"
            severity = 90
        elif "KNOWN_TRUTH_TARGET_UNRESOLVED" in reasons:
            category = "UNRESOLVED_KNOWN_TRUTH"
            severity = 85
        elif "PHYSIOLOGY_PRESERVATION_SENTINEL" in reasons:
            category = "PHYSIOLOGY_SENTINEL"
            severity = 80
        elif "DETECTOR_DISAGREEMENT" in reasons:
            category = "DETECTOR_DISAGREEMENT"
            severity = 60
        else:
            category = "REPRESENTATIVE_CONTROL"
            severity = 20
        risks.append({
            "case_id": row["item_id"],
            "source": "DAY34",
            "category": category,
            "severity_score": severity + int(row["priority_score"]),
            "reason": reasons,
            "replay_command": "python3 scripts/dev/day34_analysis_runner.py",
            "clinical_claim": False,
        })
    actual = {row["case_id"]: row for row in read_csv(day36_results)}
    manifest = yaml.safe_load(day36_manifest.read_text(encoding="utf-8"))
    for case in manifest["cases"]:
        row = actual[case["case_id"]]
        if bool(case["expected_quality_blocked"]):
            category = "EXPECTED_HARD_BLOCK_CONTROL"
            severity = 75
        elif row["distribution_support_status"] == "UNKNOWN":
            category = "DOMAIN_SUPPORT_UNKNOWN"
            severity = 70
        elif row["distribution_support_status"] == "SHIFTED":
            category = "DOMAIN_SHIFT_SENTINEL"
            severity = 55
        elif case.get("physiology_preservation_stress"):
            category = "PHYSIOLOGY_SENTINEL"
            severity = 80
        else:
            category = "REFERENCE_CONTROL"
            severity = 10
        risks.append({
            "case_id": case["case_id"],
            "source": "DAY36",
            "category": category,
            "severity_score": severity,
            "reason": row["distribution_reason_codes"] or row["qc_disposition"],
            "replay_command": "python3 scripts/dev/day36_challenge_runner.py",
            "clinical_claim": False,
        })
    risks.sort(key=lambda x: (-x["severity_score"], x["case_id"]))
    return risks[:20]


def acquisition_proxy(day34_candidates: Path) -> dict[str, Any]:
    rows = read_csv(day34_candidates)
    total = len(rows)
    informative = 0
    strata: dict[str, int] = {}
    for row in rows:
        strata[row["acquisition_stratum"]] = strata.get(row["acquisition_stratum"], 0) + 1
        reasons = row["selection_reasons"]
        if any(token in reasons for token in ("DETECTOR_DISAGREEMENT", "DAY29_HARD_INTEGRITY_OVERRIDE", "KNOWN_TRUTH_TARGET_UNRESOLVED", "PHYSIOLOGY_PRESERVATION_SENTINEL", "CORPUS_TRUTH_WINDOW_MISALIGNMENT")):
            informative += 1
    return {
        "items": total,
        "proxy_informative_items": informative,
        "proxy_information_yield": informative / total if total else None,
        "strata": strata,
        "interpretation": "PROXY_ONLY_NOT_ACTIVE_LEARNING_PERFORMANCE",
    }


def write_strata_csv(path: Path, rows: list[StratumRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(StratumRow.__dataclass_fields__)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)
