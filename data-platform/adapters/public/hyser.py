from __future__ import annotations
from pathlib import Path
import re
from .common import CanonicalPublicRecord
from .wfdb16 import read_wfdb16

_FOLDER = re.compile(r"subject(?P<subject>\d+)_session(?P<session>\d+)")

def adapt_hyser(header_path: Path, data_path: Path, subject_session_folder: str) -> CanonicalPublicRecord:
    rec = read_wfdb16(header_path, data_path)
    m = _FOLDER.fullmatch(subject_session_folder)
    if not m:
        raise ValueError('Hyser subject/session folder does not match verified naming contract')
    source_units = {s.unit for s in rec.channels}
    if source_units != {'V'}:
        raise ValueError(f'expected explicit V Hyser source unit, got {sorted(source_units)}')
    return CanonicalPublicRecord(
        dataset_id='HYSER_V2_0_0', dataset_version='2.0.0',
        source_file=data_path.name, source_sha256=rec.source_sha256,
        subject_id=f"hyser_subject_{int(m.group('subject')):02d}",
        session_id=f"hyser_session_{int(m.group('session'))}",
        fs_hz=rec.fs_hz, channel_names=tuple(s.channel_name for s in rec.channels),
        units=tuple('V' for _ in rec.channels),
        values=tuple(tuple(float(x) for x in row) for row in rec.physical),
        evidence_tier='PUBLIC_EXTERNAL', license_id='ODC-By-1.0',
        source_task_code=rec.record_name, canonical_task=None,
        task_reason='TASK_LABEL_FILE_NOT_CONSUMED_BY_THIS_RECORD_ADAPTER',
        unknown_metadata=('canonical_muscle_mapping','canonical_side_mapping','task_semantics'),
        transforms=(),
    )
