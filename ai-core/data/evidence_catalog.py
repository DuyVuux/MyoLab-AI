from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping


REQUIRED_COLUMNS = {
    "dataset_id",
    "canonical_name",
    "category",
    "task_a_fit",
    "task_b_fit",
    "task_c_fit",
    "access_class",
    "license_class",
    "license_text",
    "evidence_status",
    "conflict_flag",
    "operational_decision",
    "source_reports",
    "last_checked",
}

ALLOWED_CATEGORIES = {
    "PRIORITY_FREE_CORE",
    "PRIORITY_FREE_CONDITIONAL",
    "USEFUL_RESEARCH_ONLY",
    "RESTRICTED_REFERENCE",
    "DATA_CONTRACT_REFERENCE",
    "TO_VERIFY",
    "REJECT_FOR_DAY25_SCOPE",
}

ALLOWED_LICENSE_CLASSES = {
    "COMMERCIAL_USE_PERMITTED",
    "RESEARCH_ONLY",
    "NONCOMMERCIAL_ONLY",
    "REDISTRIBUTION_PROHIBITED",
    "DERIVATIVES_RESTRICTED",
    "CUSTOM_AGREEMENT_REQUIRED",
    "LICENSE_NOT_FOUND",
    "LICENSE_AMBIGUOUS",
    "TO_VERIFY_NOT_NEEDED_FOR_DECISION",
}

ALLOWED_ACCESS_CLASSES = {
    "FREE_OPEN_NO_REGISTRATION",
    "FREE_WITH_REGISTRATION",
    "FREE_WITH_DUA_OR_APPLICATION",
    "ACADEMIC_ONLY_ACCESS",
    "RESTRICTED_OR_IRB_CONTROLLED",
    "PAID_FIXED_PRICE",
    "PAID_QUOTE_REQUIRED",
    "PUBLIC_DOWNLOAD_REPORTED",
    "FREE_OPEN_REPORTED",
    "ACCESS_CONFLICTING",
    "ACCESS_UNKNOWN",
}


class EvidenceCatalogError(ValueError):
    """Raised when the research catalog violates a Day 25 invariant."""


@dataclass(frozen=True)
class CatalogSummary:
    total: int
    priority_free_core: int
    restricted: int
    to_verify: int
    rejected: int


def load_catalog(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    validate_catalog(rows)
    return rows


def validate_catalog(rows: Iterable[Mapping[str, str]]) -> CatalogSummary:
    materialized = [dict(row) for row in rows]
    if not materialized:
        raise EvidenceCatalogError("EMPTY_DATASET_CATALOG")

    missing_columns = REQUIRED_COLUMNS - set(materialized[0])
    if missing_columns:
        raise EvidenceCatalogError(
            "MISSING_REQUIRED_COLUMNS:" + ",".join(sorted(missing_columns))
        )

    seen: set[str] = set()
    for row_index, row in enumerate(materialized, start=2):
        dataset_id = row.get("dataset_id", "").strip()
        if not dataset_id:
            raise EvidenceCatalogError(f"MISSING_DATASET_ID_ROW_{row_index}")
        if dataset_id in seen:
            raise EvidenceCatalogError(f"DUPLICATE_DATASET_ID:{dataset_id}")
        seen.add(dataset_id)

        category = row.get("category", "").strip()
        access_class = row.get("access_class", "").strip()
        license_class = row.get("license_class", "").strip()
        evidence_status = row.get("evidence_status", "").strip()
        source_reports = row.get("source_reports", "").strip()
        conflict_flag = row.get("conflict_flag", "").strip()

        if category not in ALLOWED_CATEGORIES:
            raise EvidenceCatalogError(
                f"INVALID_CATEGORY:{dataset_id}:{category}"
            )
        if access_class not in ALLOWED_ACCESS_CLASSES:
            raise EvidenceCatalogError(
                f"INVALID_ACCESS_CLASS:{dataset_id}:{access_class}"
            )
        if license_class not in ALLOWED_LICENSE_CLASSES:
            raise EvidenceCatalogError(
                f"INVALID_LICENSE_CLASS:{dataset_id}:{license_class}"
            )
        if not source_reports:
            raise EvidenceCatalogError(f"MISSING_SOURCE_REPORT:{dataset_id}")
        if not evidence_status:
            raise EvidenceCatalogError(f"MISSING_EVIDENCE_STATUS:{dataset_id}")

        if category == "PRIORITY_FREE_CORE":
            if license_class != "COMMERCIAL_USE_PERMITTED":
                raise EvidenceCatalogError(
                    f"PRIORITY_FREE_CORE_LICENSE_NOT_PERMISSIVE:{dataset_id}"
                )
            if "NOT_VERIFIED" in evidence_status or evidence_status == "CONFLICTING":
                raise EvidenceCatalogError(
                    f"PRIORITY_FREE_CORE_EVIDENCE_TOO_WEAK:{dataset_id}"
                )

        if license_class == "NONCOMMERCIAL_ONLY" and category == "PRIORITY_FREE_CORE":
            raise EvidenceCatalogError(
                f"NONCOMMERCIAL_DATASET_CANNOT_BE_CORE:{dataset_id}"
            )

        if category == "RESTRICTED_REFERENCE":
            if access_class not in {
                "FREE_WITH_DUA_OR_APPLICATION",
                "RESTRICTED_OR_IRB_CONTROLLED",
            }:
                raise EvidenceCatalogError(
                    f"RESTRICTED_REFERENCE_ACCESS_MISMATCH:{dataset_id}"
                )
            if license_class not in {
                "CUSTOM_AGREEMENT_REQUIRED",
                "RESEARCH_ONLY",
                "REDISTRIBUTION_PROHIBITED",
            }:
                raise EvidenceCatalogError(
                    f"RESTRICTED_REFERENCE_LICENSE_MISMATCH:{dataset_id}"
                )

        if category == "TO_VERIFY" and conflict_flag.lower() in {"", "none"}:
            # TO_VERIFY may be legal-only; require the decision to say why.
            if "VERIFY" not in row.get("operational_decision", "").upper() and "DISCOVERY" not in row.get("operational_decision", "").upper():
                raise EvidenceCatalogError(
                    f"TO_VERIFY_REQUIRES_EXPLICIT_ACTION:{dataset_id}"
                )

        # Manifests/catalogs must not contain raw samples or direct identifiers.
        forbidden_column_names = {
            "patient_name",
            "mrn",
            "email",
            "phone",
            "raw_samples",
            "signal_array",
        }
        if forbidden_column_names.intersection(row):
            raise EvidenceCatalogError(
                f"FORBIDDEN_COLUMN_IN_CATALOG:{dataset_id}"
            )

    return CatalogSummary(
        total=len(materialized),
        priority_free_core=sum(
            row["category"] == "PRIORITY_FREE_CORE" for row in materialized
        ),
        restricted=sum(
            row["category"] == "RESTRICTED_REFERENCE" for row in materialized
        ),
        to_verify=sum(row["category"] == "TO_VERIFY" for row in materialized),
        rejected=sum(
            row["category"] == "REJECT_FOR_DAY25_SCOPE"
            for row in materialized
        ),
    )
