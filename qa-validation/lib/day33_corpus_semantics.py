"""DAY33 corpus semantics and safety guards."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


ALLOWED_TIERS = {
    "SYNTHETIC_KNOWN_TRUTH",
    "WEAK_LABEL_CANDIDATE",
    "EXPERT_ANNOTATION",
    "ADJUDICATED_REFERENCE",
}
FORBIDDEN_SYNTHETIC_TOKENS = {
    "stroke",
    "paresis",
    "paralysis",
    "atrophy",
    "clinical_gold_standard",
    "diagnosis",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_catalog(catalog: dict[str, Any]) -> None:
    if catalog.get("raw_payload_policy") != "EXTERNAL_STORAGE_ONLY_NOT_COMMITTED":
        raise ValueError("public raw payload policy must remain external-only")
    active = [d for d in catalog.get("datasets", []) if d.get("corpus_eligible")]
    if not active:
        raise ValueError("catalog must contain at least one corpus-eligible source")
    for dataset in active:
        if dataset.get("license_status") != "VERIFIED":
            raise ValueError("corpus-eligible public source requires verified license")
        if dataset.get("raw_payload_in_repo") is not False:
            raise ValueError("public raw payload must not be committed")
        if dataset.get("clinical_evidence") is not False:
            raise ValueError("public external source cannot be promoted to clinical evidence")


def validate_manifest(manifest: dict[str, Any], corpus_root: Path) -> None:
    if manifest.get("claim_scope") != "RESEARCH_ONLY":
        raise ValueError("DAY33 corpus claim scope must be RESEARCH_ONLY")
    partition = manifest["partition_policy"]
    if partition.get("locked_truth_visible_to_day33") is not False:
        raise ValueError("locked truth must remain hidden in DAY33")
    dev_seeds: set[int] = set()
    locked_seeds: set[int] = set()
    locked_ids: set[str] = set()
    for item in manifest.get("items", []):
        tier = item.get("evidence_tier")
        if tier not in ALLOWED_TIERS:
            raise ValueError("unknown evidence tier")
        if tier != "SYNTHETIC_KNOWN_TRUTH":
            raise ValueError("DAY33 payload items are synthetic known-truth only")
        if item["source_context"].get("direct_identifiers_present") is not False:
            raise ValueError("direct identifiers forbidden")
        if item["source_context"].get("clinical_evidence") is not False:
            raise ValueError("synthetic fixture cannot be clinical evidence")
        if item["window_context"].get("annotation_unit_type") != "QC_WINDOW_WITH_CONTEXT":
            raise ValueError("random/contextless crop forbidden")
        path = corpus_root / item["signal_artifact"]["relative_path"]
        if not path.exists():
            raise ValueError(f"missing signal artifact: {path}")
        if sha256_file(path) != item["signal_artifact"]["sha256"]:
            raise ValueError("signal artifact hash mismatch")
        serialized = json.dumps(item, sort_keys=True).lower()
        if any(token in serialized for token in FORBIDDEN_SYNTHETIC_TOKENS):
            raise ValueError("synthetic pathology/diagnosis claim forbidden")
        seed = int(item["provenance"]["seed"])
        if item["partition"] == "benchmark-development":
            dev_seeds.add(seed)
            if item.get("synthetic_truth") is None:
                raise ValueError("development synthetic item requires visible truth")
        elif item["partition"] == "benchmark-locked":
            locked_seeds.add(seed)
            locked_ids.add(item["item_id"])
            if item.get("synthetic_truth") is not None:
                raise ValueError("locked truth leakage detected")
        else:
            raise ValueError("unknown partition")
    if dev_seeds & locked_seeds:
        raise ValueError("development/locked seed overlap")
    commitments = {
        item["item_id"] for item in manifest.get("locked_truth_commitments", [])
    }
    if commitments != locked_ids:
        raise ValueError("locked truth commitment coverage mismatch")


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))
