from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import urlparse

import fsspec
import numpy as np
import pandas as pd

from _common import write_json


@dataclass
class OnlineStats:
    n: int = 0
    finite_n: int = 0
    mean: float = 0.0
    m2: float = 0.0
    sum_sq: float = 0.0
    sum_abs: float = 0.0
    min_value: float = math.inf
    max_value: float = -math.inf
    zero_n: int = 0
    exact_flat_n: int = 0
    transitions: int = 0
    observed_min_n: int = 0
    observed_max_n: int = 0
    last_value: float | None = None

    def update(self, values: np.ndarray) -> None:
        arr = np.asarray(values, dtype=np.float64).reshape(-1)
        self.n += arr.size
        finite = arr[np.isfinite(arr)]
        if finite.size == 0:
            return
        local_min = float(np.min(finite))
        local_max = float(np.max(finite))
        self.min_value = min(self.min_value, local_min)
        self.max_value = max(self.max_value, local_max)
        self.zero_n += int(np.count_nonzero(finite == 0))
        self.sum_sq += float(np.dot(finite, finite))
        self.sum_abs += float(np.abs(finite).sum())
        for x in finite:
            self.finite_n += 1
            delta = float(x) - self.mean
            self.mean += delta / self.finite_n
            self.m2 += delta * (float(x) - self.mean)
            if self.last_value is not None:
                self.transitions += 1
                if float(x) == self.last_value:
                    self.exact_flat_n += 1
            self.last_value = float(x)

    def finalize(self) -> dict:
        finite_n = self.finite_n
        return {
            'sample_count': self.n,
            'finite_count': finite_n,
            'nonfinite_ratio': (self.n - finite_n) / self.n if self.n else None,
            'mean': self.mean if finite_n else None,
            'std': math.sqrt(self.m2 / (finite_n - 1)) if finite_n > 1 else None,
            'min': self.min_value if finite_n else None,
            'max': self.max_value if finite_n else None,
            'rms': math.sqrt(self.sum_sq / finite_n) if finite_n else None,
            'mav': self.sum_abs / finite_n if finite_n else None,
            'zero_ratio': self.zero_n / finite_n if finite_n else None,
            'exact_flatline_ratio': self.exact_flat_n / self.transitions if self.transitions else None,
            'potential_clipping_ratio': None,
            'potential_clipping_note': 'Requires a second pass or known ADC rails; not inferred from magnitude.',
        }


def open_url(url: str):
    parsed = urlparse(url)
    if parsed.scheme in {'', 'file'}:
        path = parsed.path if parsed.scheme == 'file' else url
        return open(path, 'rb')
    return fsspec.open(url, mode='rb', block_size=5 * 1024 * 1024, cache_type='readahead').open()


def analyze_csv(record: dict, chunk_rows: int) -> dict:
    channels = record.get('channel_columns') or []
    if not channels:
        raise ValueError('CHANNEL_COLUMNS_REQUIRED_FOR_CSV')
    stats = {c: OnlineStats() for c in channels}
    with open_url(record['url']) as f:
        for chunk in pd.read_csv(f, usecols=channels, chunksize=chunk_rows):
            for c in channels:
                stats[c].update(pd.to_numeric(chunk[c], errors='coerce').to_numpy())
    return {c: s.finalize() for c, s in stats.items()}


def analyze_npy(record: dict) -> dict:
    with open_url(record['url']) as f:
        arr = np.load(f, allow_pickle=False)
        if arr.ndim == 1:
            arr = arr[:, None]
        if arr.ndim != 2:
            raise ValueError(f'EXPECTED_2D_ARRAY_GOT_{arr.ndim}D')
        names = record.get('channel_columns') or [f'CH{i+1:02d}' for i in range(arr.shape[1])]
        if len(names) != arr.shape[1]:
            raise ValueError('CHANNEL_COUNT_MISMATCH')
        out = {}
        for i, name in enumerate(names):
            s = OnlineStats(); s.update(arr[:, i]); out[name] = s.finalize()
        return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--plan', required=True)
    ap.add_argument('--output-dir', required=True)
    ap.add_argument('--mode', choices=['bounded-sample', 'full-stream'], required=True)
    ap.add_argument('--chunk-rows', type=int, default=50000)
    args = ap.parse_args()

    plan = json.loads(Path(args.plan).read_text(encoding='utf-8'))
    out_dir = Path(args.output_dir); out_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = out_dir / 'record-statistics.jsonl'
    test_reads = 0
    errors = 0
    completed = 0

    with ledger_path.open('w', encoding='utf-8') as ledger:
        for record in plan.get('records', []):
            partition = str(record.get('partition') or '').lower()
            if partition in {'test', 'sealed_test'}:
                test_reads += 1
                row = {'record_id': record.get('record_id'), 'status': 'BLOCKED_TEST_SIGNAL_ACCESS'}
            else:
                fmt = str(record.get('format') or '').lower().lstrip('.')
                try:
                    if fmt == 'csv':
                        channels = analyze_csv(record, args.chunk_rows)
                    elif fmt == 'npy':
                        channels = analyze_npy(record)
                    else:
                        raise ValueError(f'UNSUPPORTED_REMOTE_SIGNAL_FORMAT:{fmt}')
                    row = {
                        'record_id': record.get('record_id'),
                        'partition': partition,
                        'subject_id': record.get('subject_id'),
                        'day_id': record.get('day_id'),
                        'source_label': record.get('source_label'),
                        'status': 'PASS',
                        'channels': channels,
                    }
                    completed += 1
                except Exception as exc:  # fail per-record, preserve evidence
                    errors += 1
                    row = {'record_id': record.get('record_id'), 'partition': partition, 'status': 'ERROR', 'error': str(exc)}
            ledger.write(json.dumps(row, ensure_ascii=False) + '\n')

    summary = {
        'schema_version': 'streaming-signal-eda-summary.v1',
        'mode': args.mode,
        'planned_records': len(plan.get('records', [])),
        'completed_records': completed,
        'error_records': errors,
        'test_signal_records_read': test_reads,
        'record_ledger': str(ledger_path),
        'status': 'PASS' if errors == 0 and test_reads == 0 else 'PARTIAL_OR_FAIL',
        'training_allowed': False,
    }
    write_json(out_dir / 'streaming-eda-summary.json', summary)
    print(summary)
    return 0 if summary['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
