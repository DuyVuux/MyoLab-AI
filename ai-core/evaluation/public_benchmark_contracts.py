from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from pathlib import Path
import re
from typing import Any


class ContractValidationError(ValueError):
    """Raised when a public benchmark record violates the frozen contract."""


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_VALID_SPLITS = {"DEVELOPMENT", "LOCKED_EVALUATION"}
_VALID_QC_STATUS = {"QC_ELIGIBLE", "QC_INELIGIBLE", "QC_ABSTAINED"}
_NO_INJECTED = "NO_INJECTED_CORRUPTION"
_VALID_PERTURBATIONS = {
    _NO_INJECTED,
    "DROPOUT",
    "CLIPPING",
    "POWERLINE_INTERFERENCE",
    "LOW_FREQUENCY_CONTAMINATION",
}


def _require_non_empty(value: str | None, field_name: str) -> None:
    if value is None or not str(value).strip():
        raise ContractValidationError(f"{field_name} is required")


def _require_finite(value: float | None, field_name: str, *, allow_none: bool = False) -> None:
    if value is None:
        if allow_none:
            return
        raise ContractValidationError(f"{field_name} is required")
    if not math.isfinite(float(value)):
        raise ContractValidationError(f"{field_name} must be finite")


@dataclass(frozen=True, slots=True)
class PublicFeatureWindowRecord:
    dataset_id: str
    subject_id: str
    session_id: str
    split: str
    window_id: str
    channel_id: str
    task: str | None
    start_sample: int
    end_sample: int
    fs_hz: float
    qc_status: str
    qc_reason_codes: tuple[str, ...]
    metric_eligible: bool
    rms: float | None
    mav: float | None
    mdf_hz: float | None
    mnf_hz: float | None
    processing_profile: str
    feature_registry_version: str
    source_hash: str
    schema_version: str = "PublicFeatureWindowRecord.v1.2"

    def __post_init__(self) -> None:
        for field_name in (
            "dataset_id",
            "subject_id",
            "session_id",
            "window_id",
            "channel_id",
            "processing_profile",
            "feature_registry_version",
            "source_hash",
        ):
            _require_non_empty(getattr(self, field_name), field_name)
        if self.split not in _VALID_SPLITS:
            raise ContractValidationError(f"split must be one of {sorted(_VALID_SPLITS)}")
        if self.qc_status not in _VALID_QC_STATUS:
            raise ContractValidationError(f"qc_status must be one of {sorted(_VALID_QC_STATUS)}")
        if self.start_sample < 0 or self.end_sample <= self.start_sample:
            raise ContractValidationError("window sample bounds are invalid")
        _require_finite(self.fs_hz, "fs_hz")
        if self.fs_hz <= 0:
            raise ContractValidationError("fs_hz must be positive")
        if not _SHA256_RE.fullmatch(self.source_hash):
            raise ContractValidationError("source_hash must be a lowercase SHA-256 hex digest")
        if self.metric_eligible:
            if self.qc_status != "QC_ELIGIBLE":
                raise ContractValidationError("metric_eligible requires QC_ELIGIBLE")
            for field_name in ("rms", "mav", "mdf_hz", "mnf_hz"):
                _require_finite(getattr(self, field_name), field_name)
            if float(self.rms) < 0 or float(self.mav) < 0:
                raise ContractValidationError("amplitude features must be non-negative")
        else:
            if not self.qc_reason_codes:
                raise ContractValidationError("ineligible windows require reason codes")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ResearchExampleRecord:
    example_id: str
    window_id: str
    perturbation_type: str
    perturbation_parameters: dict[str, Any]
    perturbation_seed: int
    target_label: str
    split: str
    group_id: str
    feature_table_version: str
    generator_version: str
    schema_version: str = "ResearchExampleRecord.v1.0"

    def __post_init__(self) -> None:
        for field_name in (
            "example_id",
            "window_id",
            "perturbation_type",
            "target_label",
            "split",
            "group_id",
            "feature_table_version",
            "generator_version",
        ):
            _require_non_empty(getattr(self, field_name), field_name)
        if self.split not in _VALID_SPLITS:
            raise ContractValidationError(f"split must be one of {sorted(_VALID_SPLITS)}")
        if "CLEAN_SIGNAL" in {self.perturbation_type, self.target_label}:
            raise ContractValidationError("CLEAN_SIGNAL is not a valid known-truth target")
        if self.perturbation_type not in _VALID_PERTURBATIONS:
            raise ContractValidationError("perturbation_type is not registered")
        if self.target_label not in {_NO_INJECTED, "INJECTED_CORRUPTION"} | _VALID_PERTURBATIONS:
            raise ContractValidationError("target_label is not registered")
        if self.perturbation_type == _NO_INJECTED and self.perturbation_parameters:
            raise ContractValidationError("NO_INJECTED_CORRUPTION must not carry injection parameters")

    @property
    def claims_clean_clinical_signal(self) -> bool:
        return False

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["label_semantics"] = "NO_INJECTED_CORRUPTION_IS_NOT_CLEAN_SIGNAL"
        return data


def load_m5r_decision_ledger(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    decisions: dict[str, str] = {}
    current_id: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("DEC-M5R-"):
            current_id = line
        elif current_id and line.startswith("Decision:"):
            decisions[current_id] = line.split(":", 1)[1].strip()
            current_id = None
    return decisions
