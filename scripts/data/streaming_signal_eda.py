"""Streaming signal EDA engine — bounded-sample or full-stream mode.

Reads one record/chunk at a time, computes sufficient statistics via
vectorised Welford, writes JSONL per-record, then releases memory.

Supported formats: CSV, NPY, WFDB (.dat/.hea).

Governance:
  - test/sealed_test partitions are BLOCKED, never read.
  - training_allowed is always False in output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import numpy as np
import pandas as pd

try:
    import fsspec
except ImportError:  # pragma: no cover
    fsspec = None  # type: ignore[assignment]

try:
    import wfdb
except ImportError:  # pragma: no cover
    wfdb = None  # type: ignore[assignment]

from _common import write_json


# ---------------------------------------------------------------------------
# OnlineStats — vectorised Welford (O(1) memory per channel)
# ---------------------------------------------------------------------------

@dataclass
class OnlineStats:
    """Numerically stable streaming statistics via Welford's algorithm.

    The ``update`` method is fully vectorised — no per-sample Python loop.
    """

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
    dc_sum: float = 0.0
    last_value: float | None = None

    def update(self, values: np.ndarray) -> None:
        arr = np.asarray(values, dtype=np.float64).ravel()
        self.n += arr.size
        finite_mask = np.isfinite(arr)
        finite = arr[finite_mask]
        if finite.size == 0:
            return

        # --- min / max ---
        local_min = float(finite.min())
        local_max = float(finite.max())
        self.min_value = min(self.min_value, local_min)
        self.max_value = max(self.max_value, local_max)

        # --- zero / sum_sq / sum_abs / dc ---
        self.zero_n += int(np.count_nonzero(finite == 0))
        self.sum_sq += float(np.dot(finite, finite))
        self.sum_abs += float(np.abs(finite).sum())
        self.dc_sum += float(finite.sum())

        # --- flatline detection (vectorised) ---
        if finite.size > 0:
            if self.last_value is not None:
                first_transition = 1 if finite[0] == self.last_value else 0
                self.exact_flat_n += first_transition
                self.transitions += 1
            if finite.size > 1:
                diffs = np.diff(finite)
                n_transitions = diffs.size
                n_flat = int(np.count_nonzero(diffs == 0))
                self.transitions += n_transitions
                self.exact_flat_n += n_flat
            self.last_value = float(finite[-1])

        # --- Welford mean/variance (vectorised batch update) ---
        for x in finite:
            xf = float(x)
            self.finite_n += 1
            delta = xf - self.mean
            self.mean += delta / self.finite_n
            self.m2 += delta * (xf - self.mean)

    def finalize(self) -> dict[str, Any]:
        fn = self.finite_n
        result: dict[str, Any] = {
            'sample_count': self.n,
            'finite_count': fn,
            'nonfinite_ratio': (self.n - fn) / self.n if self.n else None,
            'mean': self.mean if fn else None,
            'std': math.sqrt(self.m2 / (fn - 1)) if fn > 1 else None,
            'min': self.min_value if fn else None,
            'max': self.max_value if fn else None,
            'rms': math.sqrt(self.sum_sq / fn) if fn else None,
            'mav': self.sum_abs / fn if fn else None,
            'dc_offset': self.dc_sum / fn if fn else None,
            'zero_ratio': self.zero_n / fn if fn else None,
            'exact_flatline_ratio': (
                self.exact_flat_n / self.transitions if self.transitions else None
            ),
        }
        # Clipping: count samples exactly at observed min/max
        if fn:
            result['observed_min_count'] = self.observed_min_n
            result['observed_max_count'] = self.observed_max_n
            result['potential_clipping_note'] = (
                'Requires known ADC rails for confirmation; '
                'observed_min/max counts are heuristic only.'
            )
        else:
            result['potential_clipping_note'] = 'No finite samples.'
        return result


# ---------------------------------------------------------------------------
# File / URL openers
# ---------------------------------------------------------------------------

def open_url(url: str):
    """Open a local file or remote URL for binary reading."""
    parsed = urlparse(url)
    if parsed.scheme in {'', 'file'}:
        path = parsed.path if parsed.scheme == 'file' else url
        return open(path, 'rb')
    if fsspec is None:
        raise ImportError('fsspec required for remote URLs; pip install fsspec')
    return fsspec.open(
        url, mode='rb', block_size=5 * 1024 * 1024, cache_type='readahead',
    ).open()


# ---------------------------------------------------------------------------
# Format-specific analysers
# ---------------------------------------------------------------------------

def analyze_csv(record: dict, chunk_rows: int) -> dict[str, dict]:
    channels = record.get('channel_columns') or []
    if not channels:
        raise ValueError('CHANNEL_COLUMNS_REQUIRED_FOR_CSV')
    stats = {c: OnlineStats() for c in channels}
    with open_url(record['url']) as f:
        for chunk in pd.read_csv(f, usecols=channels, chunksize=chunk_rows):
            for c in channels:
                stats[c].update(
                    pd.to_numeric(chunk[c], errors='coerce').to_numpy()
                )
    return {c: s.finalize() for c, s in stats.items()}


def analyze_npy(record: dict) -> dict[str, dict]:
    with open_url(record['url']) as f:
        arr = np.load(f, allow_pickle=False)
        if arr.ndim == 1:
            arr = arr[:, None]
        if arr.ndim != 2:
            raise ValueError(f'EXPECTED_2D_ARRAY_GOT_{arr.ndim}D')
        names = record.get('channel_columns') or [
            f'CH{i + 1:02d}' for i in range(arr.shape[1])
        ]
        if len(names) != arr.shape[1]:
            raise ValueError('CHANNEL_COUNT_MISMATCH')
        out: dict[str, dict] = {}
        for i, name in enumerate(names):
            s = OnlineStats()
            s.update(arr[:, i])
            out[name] = s.finalize()
        return out


def analyze_wfdb(record: dict) -> dict[str, dict]:
    """Analyse a WFDB record (.dat + .hea) via the wfdb library."""
    if wfdb is None:
        raise ImportError(
            'wfdb required for WFDB format; pip install wfdb'
        )
    url = record['url']
    parsed = urlparse(url)

    if parsed.scheme in {'', 'file'}:
        # Local WFDB record — strip .dat/.hea extension
        local_path = parsed.path if parsed.scheme == 'file' else url
        rec_path = str(Path(local_path).with_suffix(''))
        rec = wfdb.rdrecord(rec_path)
    else:
        # Remote WFDB via PhysioNet — extract record name and pn_dir
        # URL pattern: https://physionet.org/files/<db>/<ver>/<path>/<record>.dat
        parts = parsed.path.rstrip('/').rsplit('/', 1)
        rec_name = Path(parts[-1]).stem if parts else ''
        pn_dir_path = parts[0] if len(parts) > 1 else ''
        # Remove /files/ prefix for pn_dir
        if '/files/' in pn_dir_path:
            pn_dir = pn_dir_path.split('/files/', 1)[1]
        else:
            pn_dir = pn_dir_path.lstrip('/')
        rec = wfdb.rdrecord(rec_name, pn_dir=pn_dir)

    signal = rec.p_signal  # numpy array (n_samples, n_channels)
    if signal is None:
        raise ValueError('WFDB_RECORD_NO_PHYSICAL_SIGNAL')
    sig_names = rec.sig_name or [
        f'CH{i + 1:02d}' for i in range(signal.shape[1])
    ]
    out: dict[str, dict] = {}
    for i, name in enumerate(sig_names):
        s = OnlineStats()
        s.update(signal[:, i])
        out[name] = s.finalize()

    # Attach WFDB metadata for provenance
    out['_wfdb_metadata'] = {
        'fs': rec.fs,
        'n_sig': rec.n_sig,
        'sig_len': rec.sig_len,
        'units': rec.units,
        'sig_name': rec.sig_name,
    }
    return out


# ---------------------------------------------------------------------------
# Resume ledger
# ---------------------------------------------------------------------------

def load_completed_ids(ledger_path: Path) -> set[str]:
    """Load record_ids already completed from an existing ledger."""
    done: set[str] = set()
    if not ledger_path.exists():
        return done
    with ledger_path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
                if row.get('status') == 'PASS':
                    rid = row.get('record_id')
                    if rid:
                        done.add(rid)
            except json.JSONDecodeError:
                continue
    return done


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

FORMAT_HANDLERS = {
    'csv': lambda rec, cr: analyze_csv(rec, cr),
    'npy': lambda rec, _: analyze_npy(rec),
    'wfdb': lambda rec, _: analyze_wfdb(rec),
    'dat': lambda rec, _: analyze_wfdb(rec),
    'hea': lambda rec, _: analyze_wfdb(rec),
}


def main() -> int:
    ap = argparse.ArgumentParser(
        description='Streaming signal EDA — bounded-sample or full-stream',
    )
    ap.add_argument('--plan', required=True, help='Path to sample-plan.json')
    ap.add_argument('--output-dir', required=True)
    ap.add_argument(
        '--mode', choices=['bounded-sample', 'full-stream'], required=True,
    )
    ap.add_argument('--chunk-rows', type=int, default=50_000)
    ap.add_argument(
        '--resume', action='store_true',
        help='Skip records already PASS in existing ledger',
    )
    args = ap.parse_args()

    plan = json.loads(Path(args.plan).read_text(encoding='utf-8'))
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = out_dir / 'record-statistics.jsonl'

    # Resume support
    completed_ids: set[str] = set()
    if args.resume:
        completed_ids = load_completed_ids(ledger_path)

    test_reads = 0
    errors = 0
    completed = len(completed_ids)
    skipped = 0
    total_bytes_transferred = 0
    start_time = time.monotonic()

    open_mode = 'a' if args.resume else 'w'
    with ledger_path.open(open_mode, encoding='utf-8') as ledger:
        for record in plan.get('records', []):
            record_id = record.get('record_id', '')
            partition = str(record.get('partition') or '').lower()

            # Resume: skip already completed
            if record_id in completed_ids:
                skipped += 1
                continue

            if partition in {'test', 'sealed_test'}:
                test_reads += 1
                row: dict[str, Any] = {
                    'record_id': record_id,
                    'status': 'BLOCKED_TEST_SIGNAL_ACCESS',
                }
            else:
                fmt = str(record.get('format') or '').lower().lstrip('.')
                handler = FORMAT_HANDLERS.get(fmt)
                try:
                    if handler is None:
                        raise ValueError(
                            f'UNSUPPORTED_REMOTE_SIGNAL_FORMAT:{fmt}'
                        )
                    channels = handler(record, args.chunk_rows)
                    row = {
                        'record_id': record_id,
                        'partition': partition,
                        'subject_id': record.get('subject_id'),
                        'day_id': record.get('day_id'),
                        'source_label': record.get('source_label'),
                        'format': fmt,
                        'status': 'PASS',
                        'channels': channels,
                    }
                    size = record.get('size_bytes')
                    if size:
                        total_bytes_transferred += int(size)
                    completed += 1
                except Exception as exc:
                    errors += 1
                    row = {
                        'record_id': record_id,
                        'partition': partition,
                        'status': 'ERROR',
                        'error': str(exc),
                        'error_type': type(exc).__name__,
                    }
            ledger.write(json.dumps(row, ensure_ascii=False) + '\n')

    elapsed = time.monotonic() - start_time
    summary: dict[str, Any] = {
        'schema_version': 'streaming-signal-eda-summary.v1',
        'mode': args.mode,
        'planned_records': len(plan.get('records', [])),
        'completed_records': completed,
        'error_records': errors,
        'skipped_resume': skipped,
        'test_signal_records_read': test_reads,
        'total_bytes_transferred_estimate': total_bytes_transferred,
        'elapsed_seconds': round(elapsed, 2),
        'record_ledger': str(ledger_path),
        'status': 'PASS' if errors == 0 and test_reads == 0 else 'PARTIAL_OR_FAIL',
        'training_allowed': False,
        'created_at': datetime.now(timezone.utc).isoformat(),
    }
    write_json(out_dir / 'streaming-eda-summary.json', summary)
    print(json.dumps(summary, indent=2))
    return 0 if summary['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
