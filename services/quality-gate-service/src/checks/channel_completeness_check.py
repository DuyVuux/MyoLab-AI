"""Basic usable-channel and shape check."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np

from semg_core.io import NormalizedSignal

from result_models import CheckResult
from checks.common import get_nested


def run(
    signal: NormalizedSignal,
    protocol: Mapping[str, Any],
    config: Mapping[str, Any],
) -> CheckResult:
    configured_minimum = int(
        get_nested(
            config,
            "structural_checks",
            "usable_channels",
            "minimum_count",
            default=1,
        )
    )
    protocol_minimum = int(
        get_nested(
            protocol,
            "acquisition",
            "minimum_basic_semg_channels",
            default=1,
        )
    )
    minimum_count = max(configured_minimum, protocol_minimum)

    usable: list[str] = []
    unusable: list[str] = []
    length_mismatches: list[str] = []
    for channel_id, channel in signal.channels.items():
        if channel.sample_count != signal.sample_count:
            length_mismatches.append(channel_id)
        if channel.sample_count == signal.sample_count and np.any(np.isfinite(channel.samples_uV)):
            usable.append(channel_id)
        else:
            unusable.append(channel_id)

    details: dict[str, Any] = {
        "minimum_usable_channel_count": minimum_count,
        "total_channel_count": signal.channel_count,
        "usable_channel_ids": sorted(usable),
        "unusable_channel_ids": sorted(unusable),
        "length_mismatch_channel_ids": sorted(length_mismatches),
    }
    if len(usable) < minimum_count or length_mismatches:
        return CheckResult(
            check_id="channel_completeness",
            status="fail",
            severity="critical",
            reason_codes=("NO_USABLE_SIGNAL_CHANNEL",),
            details=details,
        )
    return CheckResult(
        check_id="channel_completeness",
        status="pass",
        severity="critical",
        details=details,
    )
