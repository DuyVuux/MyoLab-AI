"""Protocol/reference/target compatibility check."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from semg_core.io import NormalizedSignal

from result_models import CheckResult
from checks.common import get_nested


def run(
    signal: NormalizedSignal,
    protocol: Mapping[str, Any],
    config: Mapping[str, Any],
) -> CheckResult:
    del config
    reasons: list[str] = []
    details: dict[str, Any] = {
        "signal_protocol": signal.protocol_ref.to_dict(),
        "loaded_protocol": {
            "id": protocol.get("protocol_id"),
            "version": protocol.get("version"),
        },
    }

    if signal.protocol_ref.protocol_id != str(protocol.get("protocol_id")):
        reasons.append("PROTOCOL_VERSION_MISMATCH")
    if signal.protocol_ref.version != str(protocol.get("version")):
        reasons.append("PROTOCOL_VERSION_MISMATCH")

    target_muscle = get_nested(protocol, "task", "target_muscle")
    channel_muscles = sorted({channel.muscle for channel in signal.channels.values()})
    details["target_muscle"] = target_muscle
    details["channel_muscles"] = channel_muscles
    if target_muscle and str(target_muscle) not in channel_muscles:
        reasons.append("TARGET_MUSCLE_MISMATCH")

    required_parameter = get_nested(protocol, "task", "effort", "parameter")
    parameter_required = bool(
        get_nested(protocol, "task", "effort", "required_at_session_level", default=False)
    )
    session_parameters = signal.source_manifest.get("session_parameters", {})
    parameter_present = (
        isinstance(session_parameters, Mapping)
        and required_parameter is not None
        and required_parameter in session_parameters
    )
    details["required_session_parameter"] = required_parameter
    details["required_session_parameter_present"] = bool(parameter_present)
    if parameter_required and not parameter_present:
        reasons.append("REQUIRED_SESSION_PARAMETER_MISSING")

    reasons = list(dict.fromkeys(reasons))
    if reasons:
        return CheckResult(
            check_id="protocol_compatibility",
            status="fail",
            severity="critical",
            reason_codes=tuple(reasons),
            details=details,
        )
    return CheckResult(
        check_id="protocol_compatibility",
        status="pass",
        severity="critical",
        details=details,
    )
