"""DAY43 mask-not-delete semantics and metric leakage guard."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from types import MappingProxyType
from typing import Any, Mapping

import numpy as np


class MaskingError(ValueError):
    """Raised when mask/window lineage is invalid."""


@dataclass(frozen=True)
class MaskApplication:
    values: np.ndarray
    mask: np.ndarray
    window_identity: Mapping[str, Any]
    metadata: Mapping[str, Any]


def hash_array(values: np.ndarray) -> str:
    array = np.ascontiguousarray(values)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode())
    digest.update(str(array.shape).encode())
    digest.update(array.tobytes())
    return digest.hexdigest()


def freeze_window_identity(identity: Mapping[str, Any]) -> Mapping[str, Any]:
    required = {
        "window_id",
        "session_id",
        "channel_id",
        "start_sample",
        "end_sample_exclusive",
    }
    missing = required - set(identity)
    if missing:
        joined = ",".join(sorted(missing))
        raise MaskingError(f"WINDOW_IDENTITY_REQUIRED_FIELDS_MISSING:{joined}")
    return MappingProxyType(dict(identity))


def apply_metadata_mask(
    values: np.ndarray,
    mask: np.ndarray,
    window_identity: Mapping[str, Any],
) -> MaskApplication:
    signal_values = np.asarray(values, dtype=float)
    processing_mask = np.asarray(mask, dtype=bool)
    if signal_values.ndim != 1 or processing_mask.shape != signal_values.shape:
        raise MaskingError("MASK_MUST_ALIGN_1_TO_1")

    input_hash = hash_array(signal_values)
    output = signal_values.copy()
    output[processing_mask] = np.nan
    if hash_array(signal_values) != input_hash:
        raise RuntimeError("RAW_MUTATION_DETECTED")

    frozen_identity = freeze_window_identity(window_identity)
    metadata = {
        "input_hash": input_hash,
        "output_hash": hash_array(output),
        "raw_deleted": False,
        "delete_masked_samples": False,
        "preserve_sample_alignment": True,
        "masked_sample_count": int(processing_mask.sum()),
        "mask_fraction": float(processing_mask.mean()),
        "source_window_id": frozen_identity["window_id"],
    }
    return MaskApplication(
        output,
        processing_mask.copy(),
        frozen_identity,
        metadata,
    )


def metric_mask_eligibility(
    mask: np.ndarray,
    *,
    qc_signal_quality: str | None,
    processing_permission: str,
) -> dict[str, Any]:
    processing_mask = np.asarray(mask, dtype=bool)
    reason_codes: list[str] = []
    if qc_signal_quality == "FAIL":
        reason_codes.append("QC_FAIL_BLOCKS_METRIC")
    if processing_permission != "ALLOW_PROFILED_PROCESSING":
        reason_codes.append("PROCESSING_PERMISSION_NOT_GRANTED")
    if bool(processing_mask.any()):
        reason_codes.append("MASKED_WINDOW_EXCLUDED_FROM_METRIC")
    masked_fraction = (
        float(processing_mask.mean()) if processing_mask.size else 1.0
    )
    return {
        "eligible": not reason_codes,
        "metric_value": None,
        "reason_codes": reason_codes,
        "masked_fraction": masked_fraction,
    }
