"""Helpers tạo manifest deterministic cho offline analysis package."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


def canonical_json_sha256(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class StageRecord:
    stage_id: str
    status: str
    downstream_allowed: bool
    output_file: str
    output_payload_sha256: str
    config_id: str | None
    reason_codes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage_id": self.stage_id,
            "status": self.status,
            "downstream_allowed": self.downstream_allowed,
            "output_file": self.output_file,
            "output_payload_sha256": self.output_payload_sha256,
            "config_id": self.config_id,
            "reason_codes": list(dict.fromkeys(self.reason_codes)),
        }


def build_analysis_fingerprint(
    *,
    session_id: str,
    source_hash_sha256: str,
    config_hashes: dict[str, str],
    stage_records: list[StageRecord],
    final_conclusion: str,
    confidence_category: str,
) -> str:
    payload = {
        "session_id": session_id,
        "source_hash_sha256": source_hash_sha256,
        "config_hashes": dict(sorted(config_hashes.items())),
        "stage_records": [record.to_dict() for record in stage_records],
        "final_conclusion": final_conclusion,
        "confidence_category": confidence_category,
    }
    return canonical_json_sha256(payload)
