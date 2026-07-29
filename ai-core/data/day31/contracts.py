"""Feature-arm and dataset-dimension contracts for Day 31."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from semg_core.day31_features import FEATURE_ORDER


@dataclass(frozen=True, slots=True)
class FeatureArm:
    """Resolved immutable feature arm."""

    arm_id: str
    feature_ids: tuple[str, ...]
    window_ms: int
    role: str = "registered"


def resolve_feature_arms(
    config: Mapping[str, Any],
) -> dict[str, FeatureArm]:
    """Resolve inheritance/exclusion and reject ambiguous arm definitions."""

    raw_arms = config.get("arms")
    if not isinstance(raw_arms, Mapping) or not raw_arms:
        raise ValueError("feature arm config must contain non-empty arms")
    resolved: dict[str, FeatureArm] = {}
    active_stack: list[str] = []

    def resolve(arm_id: str) -> FeatureArm:
        if arm_id in resolved:
            return resolved[arm_id]
        if arm_id in active_stack:
            cycle = " -> ".join((*active_stack, arm_id))
            raise ValueError(f"feature arm inheritance cycle: {cycle}")
        raw = raw_arms.get(arm_id)
        if not isinstance(raw, Mapping):
            raise TypeError(f"unknown or invalid feature arm: {arm_id}")
        active_stack.append(arm_id)
        try:
            inherited = raw.get("inherits")
            if inherited is not None:
                if not isinstance(inherited, str) or not inherited:
                    raise ValueError(f"{arm_id}.inherits must be a non-empty string")
                parent = resolve(inherited)
                feature_ids = parent.feature_ids
                inherited_window = parent.window_ms
            else:
                feature_ids = tuple(FEATURE_ORDER)
                inherited_window = 200

            if "feature_ids" in raw:
                candidate = raw["feature_ids"]
                if not isinstance(candidate, list):
                    raise ValueError(f"{arm_id}.feature_ids must be a list")
                feature_ids = tuple(candidate)
            excludes = raw.get("excludes", [])
            if not isinstance(excludes, list):
                raise TypeError(f"{arm_id}.excludes must be a list")
            unknown_excludes = sorted(set(excludes) - set(FEATURE_ORDER))
            if unknown_excludes:
                raise ValueError(
                    f"{arm_id} excludes unknown features: {unknown_excludes}"
                )
            feature_ids = tuple(
                name for name in feature_ids if name not in set(excludes)
            )
            if not feature_ids or len(feature_ids) != len(set(feature_ids)):
                raise ValueError(f"{arm_id} features must be unique and non-empty")
            unknown = sorted(set(feature_ids) - set(FEATURE_ORDER))
            if unknown:
                raise ValueError(f"{arm_id} has unknown features: {unknown}")
            window_ms = raw.get("window_ms", inherited_window)
            if (
                isinstance(window_ms, bool)
                or not isinstance(window_ms, int)
                or window_ms <= 0
            ):
                raise ValueError(f"{arm_id}.window_ms must be a positive integer")
            role = raw.get("role", "registered")
            if not isinstance(role, str) or not role:
                raise ValueError(f"{arm_id}.role must be a non-empty string")
            result = FeatureArm(
                arm_id=arm_id,
                feature_ids=feature_ids,
                window_ms=window_ms,
                role=role,
            )
            resolved[arm_id] = result
            return result
        finally:
            active_stack.pop()

    for configured_arm_id in raw_arms:
        if not isinstance(configured_arm_id, str):
            raise TypeError("feature arm identifiers must be strings")
        resolve(configured_arm_id)
    return resolved


def expected_arm_dimensions(
    arms: Mapping[str, FeatureArm],
    channel_count: int,
) -> dict[str, int]:
    """Return deterministic wide-matrix dimensions for a source view."""

    if (
        isinstance(channel_count, bool)
        or not isinstance(channel_count, int)
        or channel_count <= 0
    ):
        raise ValueError("channel_count must be a positive integer")
    return {
        arm_id: len(arm.feature_ids) * channel_count
        for arm_id, arm in arms.items()
    }
