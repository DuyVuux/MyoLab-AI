from __future__ import annotations

import csv
from pathlib import Path

import pytest

from data.evidence_catalog import EvidenceCatalogError, load_catalog, validate_catalog

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "docs/05-data/day25-research/dataset-inventory-v0.2.csv"


def read_rows() -> list[dict[str, str]]:
    with INVENTORY.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_inventory_is_valid_and_research_grounded() -> None:
    rows = load_catalog(INVENTORY)
    summary = validate_catalog(rows)
    assert summary.total >= 20
    assert summary.priority_free_core >= 5
    assert summary.restricted >= 2
    assert summary.to_verify >= 8


def test_duplicate_dataset_id_is_rejected() -> None:
    rows = read_rows()
    rows.append(dict(rows[0]))
    with pytest.raises(EvidenceCatalogError, match="DUPLICATE_DATASET_ID"):
        validate_catalog(rows)


def test_noncommercial_dataset_cannot_be_priority_core() -> None:
    rows = read_rows()
    target = next(row for row in rows if row["dataset_id"] == "PUTEMG")
    target["category"] = "PRIORITY_FREE_CORE"
    with pytest.raises(EvidenceCatalogError, match="PRIORITY_FREE_CORE_LICENSE_NOT_PERMISSIVE"):
        validate_catalog(rows)


def test_restricted_reference_requires_governed_access() -> None:
    rows = read_rows()
    target = next(row for row in rows if row["dataset_id"] == "PHYSIOMIO")
    target["access_class"] = "FREE_OPEN_NO_REGISTRATION"
    with pytest.raises(EvidenceCatalogError, match="RESTRICTED_REFERENCE_ACCESS_MISMATCH"):
        validate_catalog(rows)
