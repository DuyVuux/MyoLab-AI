from __future__ import annotations

from typing import Any


def assess_feature_eligibility(evidence: dict[str, Any]) -> dict[str, Any]:
    amplitude = all(
        evidence.get(key) is True
        for key in ["signal_loadable", "unit_verified", "channel_mapping_verified"]
    )
    time_domain = amplitude and evidence.get("sampling_rate_verified") is True
    frequency = time_domain and all(
        evidence.get(key) is True
        for key in ["raw_or_near_raw_verified", "prior_filtering_known", "window_policy_locked"]
    )
    inter_channel = time_domain and evidence.get("channel_order_verified") is True

    return {
        "F0_amplitude_sanity": {"eligible": amplitude},
        "F1_sparse_classical_core": {"eligible": time_domain},
        "F2_frequency_extension": {"eligible": frequency},
        "F3_fatigue_context": {
            "eligible": False,
            "reason": "GRABMyo multi-day structure is not an independent fatigue label",
        },
        "F4_inter_channel": {"eligible": inter_channel},
        "MFCV": {
            "eligible": False,
            "reason": "Electrode geometry/IED/propagation eligibility not established by Day29",
        },
    }
