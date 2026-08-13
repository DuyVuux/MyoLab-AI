from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
import numpy as np

_GAIN_RE = re.compile(r"^(?P<gain>[0-9eE+.-]+)(?:\((?P<baseline>-?\d+)\))?/(?P<unit>\S+)$")

@dataclass(frozen=True)
class ChannelSpec:
    file_name: str
    gain: float
    baseline: int
    unit: str
    channel_name: str

@dataclass(frozen=True)
class WFDB16Record:
    record_name: str
    fs_hz: float
    n_samples: int
    channels: tuple[ChannelSpec, ...]
    digital: np.ndarray
    physical: np.ndarray
    source_sha256: str

class WFDBContractError(ValueError):
    pass

def parse_header_text(text: str) -> tuple[str, float, int, tuple[ChannelSpec, ...]]:
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.startswith('#')]
    if not lines:
        raise WFDBContractError('empty WFDB header')
    first = lines[0].split()
    if len(first) < 4:
        raise WFDBContractError('WFDB first line requires record, signal count, Fs, sample count')
    name, n_sig, fs, n_samples = first[0], int(first[1]), float(first[2]), int(first[3])
    if fs <= 0 or n_samples <= 0 or n_sig <= 0:
        raise WFDBContractError('invalid count or sampling rate')
    if len(lines[1:]) != n_sig:
        raise WFDBContractError('signal-line count mismatch')
    specs = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) < 3:
            raise WFDBContractError('malformed signal line')
        m = _GAIN_RE.match(parts[2])
        if not m:
            raise WFDBContractError(f'unsupported gain/unit token: {parts[2]}')
        specs.append(ChannelSpec(
            file_name=parts[0],
            gain=float(m.group('gain')),
            baseline=int(m.group('baseline') or '0'),
            unit=m.group('unit'),
            channel_name=parts[-1],
        ))
    return name, fs, n_samples, tuple(specs)

def read_wfdb16(header_path: Path, data_path: Path) -> WFDB16Record:
    name, fs, n_samples, specs = parse_header_text(header_path.read_text(encoding='utf-8'))
    raw = data_path.read_bytes()
    source_sha = hashlib.sha256(raw).hexdigest()
    digital = np.frombuffer(raw, dtype='<i2')
    expected = n_samples * len(specs)
    if digital.size != expected:
        raise WFDBContractError(f'binary sample count mismatch: expected {expected}, got {digital.size}')
    digital = digital.reshape(n_samples, len(specs)).copy()
    physical = np.empty_like(digital, dtype=np.float64)
    for idx, spec in enumerate(specs):
        physical[:, idx] = (digital[:, idx].astype(np.float64) - spec.baseline) / spec.gain
    return WFDB16Record(name, fs, n_samples, specs, digital, physical, source_sha)
