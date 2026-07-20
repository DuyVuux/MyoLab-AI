"""Shared helpers for individual quality checks."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from semg_core.io import NormalizedSignal


def get_nested(mapping: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    value: Any = mapping
    for key in keys:
        if not isinstance(value, Mapping) or key not in value:
            return default
        value = value[key]
    return value


def active_phase_id(protocol: Mapping[str, Any]) -> str:
    value = get_nested(protocol, "analysis", "active_phase_id", default="active_contraction")
    return str(value)


def active_channel_samples(
    signal: NormalizedSignal,
    protocol: Mapping[str, Any],
) -> dict[str, Any]:
    """Return active-phase arrays, or whole recording when no phase is available."""

    phase_id = active_phase_id(protocol)
    try:
        phase_slice = signal.phase_slice(phase_id)
    except (KeyError, ValueError):
        phase_slice = slice(0, signal.sample_count)
    return {
        channel_id: channel.samples_uV[phase_slice]
        for channel_id, channel in signal.channels.items()
    }
