from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

SUPPORTED_VALUES = frozenset(
    {"SUPPORTED", "TRAIN", "ELIGIBLE", "CORE", "CONFIRMED"}
)


def _collect_mapping_entries(document: dict[str, Any]) -> list[tuple[str, Any]]:
    mappings = document.get("mappings")
    if isinstance(mappings, list):
        entries: list[tuple[str, Any]] = []
        for index, item in enumerate(mappings):
            if not isinstance(item, dict):
                raise ValueError(f"Mapping entry {index} must be an object")
            source_label = item.get("source_label")
            if not isinstance(source_label, str) or not source_label.strip():
                raise ValueError(f"Mapping entry {index} has no source_label")
            entries.append((source_label, item))
        return entries

    labels = document.get("labels", document)
    if not isinstance(labels, dict):
        raise ValueError("Label dictionary must contain 'mappings' or 'labels'")
    return [(str(source), item) for source, item in labels.items()]


def load_supported_canonical_labels(path: str | Path) -> set[str]:
    document = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("Label dictionary root must be a mapping")

    canonical_by_source: dict[str, str] = {}
    supported: set[str] = set()
    for source_label, item in _collect_mapping_entries(document):
        if isinstance(item, str):
            canonical = item
            eligibility = "SUPPORTED"
        elif isinstance(item, dict):
            canonical = item.get("canonical_label") or item.get("canonical")
            eligibility = str(
                item.get("analysis_eligibility")
                or item.get("mapping_status")
                or item.get("status")
                or ""
            ).upper()
        else:
            continue
        if not isinstance(canonical, str) or not canonical.strip():
            raise ValueError(f"Missing canonical label for source {source_label!r}")
        canonical = canonical.strip().lower()
        prior = canonical_by_source.get(source_label)
        if prior is not None and prior != canonical:
            raise ValueError(
                f"Conflicting canonical mappings for source {source_label!r}"
            )
        canonical_by_source[source_label] = canonical
        if canonical == "unknown":
            continue
        if eligibility in SUPPORTED_VALUES or eligibility.startswith("SUPPORTED"):
            supported.add(canonical)
    return supported


def ordered_intersection(
    first: set[str],
    second: set[str],
    project_order: tuple[str, ...],
) -> list[str]:
    return [label for label in project_order if label in first and label in second]


def build_ontology_report(
    mendeley_labels: set[str],
    grabmyo_labels: set[str],
    project_order: tuple[str, ...],
) -> dict[str, Any]:
    intersection = ordered_intersection(
        mendeley_labels, grabmyo_labels, project_order
    )
    return {
        "schema_version": "day30-common-ontology.v1",
        "class_order": list(project_order),
        "mendeley_supported": [
            label for label in project_order if label in mendeley_labels
        ],
        "grabmyo_supported": [
            label for label in project_order if label in grabmyo_labels
        ],
        "intersection": intersection,
        "support": {
            label: {
                "mendeley": label in mendeley_labels,
                "grabmyo": label in grabmyo_labels,
            }
            for label in project_order
        },
        "unknown_supervised_core_allowed": False,
        "synthetic_fill_allowed": False,
    }

