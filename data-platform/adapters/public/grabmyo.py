from __future__ import annotations
from pathlib import Path
import re
import numpy as np
from .common import CanonicalPublicRecord, TransformProvenance
from .wfdb16 import read_wfdb16

_NAME = re.compile(r"session(?P<session>\d+)_participant(?P<subject>\d+)_gesture(?P<gesture>\d+)_trial(?P<trial>\d+)")

def adapt_grabmyo(header_path: Path, data_path: Path) -> CanonicalPublicRecord:
    rec = read_wfdb16(header_path, data_path)
    m = _NAME.fullmatch(rec.record_name)
    if not m:
        raise ValueError('GRABMyo record name does not match verified naming contract')
    semg_idx = [i for i,s in enumerate(rec.channels) if not s.channel_name.startswith('U')]
    source_units = {rec.channels[i].unit for i in semg_idx}
    if source_units != {'mV'}:
        raise ValueError(f'expected explicit mV GRABMyo source unit, got {sorted(source_units)}')
    values_v = rec.physical[:, semg_idx] * 1e-3
    channels = tuple(rec.channels[i].channel_name for i in semg_idx)
    transforms = (TransformProvenance('multiply','mV','V',1e-3,'exact SI prefix conversion; explicit source header unit'),)
    return CanonicalPublicRecord(
        dataset_id='GRABMYO_V1_1_0', dataset_version='1.1.0',
        source_file=data_path.name, source_sha256=rec.source_sha256,
        subject_id=f"grabmyo_subject_{int(m.group('subject')):02d}",
        session_id=f"grabmyo_session_{int(m.group('session'))}",
        fs_hz=rec.fs_hz, channel_names=channels, units=tuple('V' for _ in channels),
        values=tuple(tuple(float(x) for x in row) for row in values_v),
        evidence_tier='PUBLIC_EXTERNAL', license_id='CC-BY-4.0',
        source_task_code=f"gesture{int(m.group('gesture'))}_trial{int(m.group('trial'))}",
        canonical_task=None,
        task_reason='GESTURE_CODE_PRESERVED_NO_SILENT_SEMANTIC_MAPPING',
        unknown_metadata=('canonical_muscle_mapping','canonical_side_mapping'),
        transforms=transforms,
    )
