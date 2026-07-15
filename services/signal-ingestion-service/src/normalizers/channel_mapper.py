"""Map parsed generic-CSV columns into canonical channel objects."""

from __future__ import annotations

import numpy as np

from semg_core.io import NormalizedChannel

from .metadata_extractor import ChannelSpec
from .unit_normalizer import normalize_to_uV


def build_normalized_channel(
    spec: ChannelSpec,
    source_samples: np.ndarray,
) -> NormalizedChannel:
    return NormalizedChannel(
        channel_id=spec.channel_id,
        samples_uV=normalize_to_uV(source_samples, spec.unit),
        muscle=spec.muscle,
        side=spec.side,
        role=spec.role,
        source_column=spec.column,
        source_unit=spec.unit,
    )
