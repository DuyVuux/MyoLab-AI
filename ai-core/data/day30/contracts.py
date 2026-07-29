from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DatasetProfile:
    dataset_id: str
    sampling_rate_hz: float
    signal_unit: str
    channel_policy_id: str
    session_structure: str


@dataclass(frozen=True)
class WindowSpec:
    window_ms: int
    hop_ms: int


@dataclass(frozen=True)
class ChannelDecision:
    dataset_id: str
    primary_channels: tuple[str, ...]
    excluded_channels: tuple[str, ...]
    quarantined_channels: tuple[str, ...]
    direct_anatomical_mapping_allowed: bool = False


@dataclass(frozen=True)
class DatasetView:
    view_id: str
    dataset_ids: tuple[str, ...]
    classes: tuple[str, ...]
    channel_policy_id: str
    role: str
    pooled_training_allowed: bool = False


ALLOWED_PARTITIONS = frozenset({"train", "validation"})
FORBIDDEN_PARTITIONS = frozenset({"test", "sealed_test", "outer_test"})
PROTECTED_LABELS = frozenset(
    {"unknown", "ambiguous", "artifact", "not_attempted", "transition"}
)
PROJECT_CLASS_ORDER = (
    "rest",
    "hand_open",
    "hand_close",
    "wrist_flexion",
    "wrist_extension",
)

