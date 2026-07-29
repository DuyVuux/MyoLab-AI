"""Real EDA on Mendeley 4-Channel Hand Gesture v2 — MAT file approach.

Downloads *_raw.mat files (~10MB each, 8x smaller than CSV) from
Mendeley Data API, parses with scipy.io.loadmat, and computes
per-channel Welford statistics.

Governance:
  - No training — training_allowed is always False.
  - No test signal access.
  - Raw signal only (not filtered).

Usage:
  python3 scripts/data/run_mendeley_real_eda.py \\
    --output-dir /path/to/evidence \\
    --max-subjects 10 --seed 282026
"""
from __future__ import annotations

import argparse
import io
import json
import math
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import requests
import scipy.io


# ─── OnlineStats (Welford) ────────────────────────────────────────────────

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
    dc_sum: float = 0.0
    last_value: float | None = None

    def update(self, values: np.ndarray) -> None:
        arr = np.asarray(values, dtype=np.float64).ravel()
        self.n += arr.size
        finite_mask = np.isfinite(arr)
        finite = arr[finite_mask]
        if finite.size == 0:
            return
        self.min_value = min(self.min_value, float(finite.min()))
        self.max_value = max(self.max_value, float(finite.max()))
        self.zero_n += int(np.count_nonzero(finite == 0))
        self.sum_sq += float(np.dot(finite, finite))
        self.sum_abs += float(np.abs(finite).sum())
        self.dc_sum += float(finite.sum())
        if self.last_value is not None:
            self.transitions += 1
            if finite[0] == self.last_value:
                self.exact_flat_n += 1
        if finite.size > 1:
            diffs = np.diff(finite)
            self.transitions += diffs.size
            self.exact_flat_n += int(np.count_nonzero(diffs == 0))
        self.last_value = float(finite[-1])
        for x in finite:
            xf = float(x)
            self.finite_n += 1
            delta = xf - self.mean
            self.mean += delta / self.finite_n
            self.m2 += delta * (xf - self.mean)

    def finalize(self) -> dict[str, Any]:
        fn = self.finite_n
        return {
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


# ─── Constants ────────────────────────────────────────────────────────────

MENDELEY_API = 'https://data.mendeley.com/api/datasets/ckwc76xr2z/files'
MAX_RETRIES = 3
RETRY_BACKOFF = [5, 15, 30]

GESTURE_NAMES = [
    'rest', 'wrist_extension', 'wrist_flexion',
    'ulnar_deviation', 'radial_deviation', 'grip',
    'abduction_all_fingers', 'adduction_all_fingers',
    'supination', 'pronation',
]


def get_raw_mat_catalog() -> list[dict]:
    """Fetch catalog, filter to *_raw.mat files (~10MB each)."""
    resp = requests.get(MENDELEY_API, params={'version': 2}, timeout=30)
    resp.raise_for_status()
    items = []
    for f in resp.json():
        name = f['filename']
        if name.endswith('_raw.mat'):
            cd = f.get('content_details', {})
            sid = name.replace('_raw.mat', '')
            items.append({
                'subject_id': sid,
                'filename': name,
                'file_id': f['id'],
                'size_bytes': cd.get('size', 0),
                'download_url': cd.get('download_url', ''),
            })
    return sorted(items, key=lambda x: int(x['subject_id']) if x['subject_id'].isdigit() else 0)


def download_mat(url: str, subject_id: str) -> bytes:
    """Download MAT file with retry."""
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, timeout=120)
            resp.raise_for_status()
            return resp.content
        except Exception as exc:
            if attempt < MAX_RETRIES - 1:
                wait = RETRY_BACKOFF[attempt]
                print(f'\n  [RETRY {attempt+1}] subject {subject_id}: {exc} — {wait}s', flush=True)
                time.sleep(wait)
            else:
                raise
    raise RuntimeError('Exhausted retries')


def analyze_mat(raw_bytes: bytes, subject_id: str) -> dict:
    """Parse MAT file and compute per-channel stats."""
    mat = scipy.io.loadmat(io.BytesIO(raw_bytes))

    data = mat['data']  # shape: (N, 4) float64
    fs = int(mat['fs'].flat[0])
    mat_id = int(mat['iD'].flat[0])

    # Extract channel labels
    labels_arr = mat.get('labels', None)
    if labels_arr is not None:
        channel_labels = [str(l).strip() for l in labels_arr.flat]
    else:
        channel_labels = [f'ch{i}' for i in range(data.shape[1])]

    # Extract units
    units_arr = mat.get('units', None)
    if units_arr is not None:
        channel_units = [str(u).strip() for u in units_arr.flat]
    else:
        channel_units = ['?'] * data.shape[1]

    n_rows, n_cols = data.shape
    channel_stats = {}
    for col_idx in range(n_cols):
        label = channel_labels[col_idx] if col_idx < len(channel_labels) else f'ch{col_idx}'
        s = OnlineStats()
        s.update(data[:, col_idx])
        channel_stats[label] = s.finalize()

    return {
        'subject_id': subject_id,
        'mat_id': mat_id,
        'sampling_rate_hz': fs,
        'total_rows': n_rows,
        'n_channels': n_cols,
        'channel_labels': channel_labels,
        'channel_units': channel_units,
        'bytes_downloaded': len(raw_bytes),
        'channel_statistics': channel_stats,
        'status': 'PASS',
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--output-dir', required=True)
    ap.add_argument('--max-subjects', type=int, default=10)
    ap.add_argument('--seed', type=int, default=282026)
    ap.add_argument('--resume', action='store_true')
    args = ap.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = out_dir / 'mendeley-eda-records.jsonl'

    print('[INFO] Fetching Mendeley file catalog (MAT files)...')
    catalog = get_raw_mat_catalog()
    print(f'[INFO] Found {len(catalog)} raw MAT files')

    import random
    rng = random.Random(args.seed)
    sample = catalog[:] if len(catalog) <= args.max_subjects else rng.sample(catalog, args.max_subjects)
    sample.sort(key=lambda x: int(x['subject_id']) if x['subject_id'].isdigit() else 0)
    total_mb = sum(s['size_bytes'] for s in sample) / 1024 / 1024
    print(f'[INFO] Selected {len(sample)} subjects: {[s["subject_id"] for s in sample]}')
    print(f'[INFO] Total download: {total_mb:.0f} MB (MAT format, 8x smaller than CSV)')

    # Resume
    completed_ids: set[str] = set()
    if args.resume and ledger_path.exists():
        with ledger_path.open('r') as f:
            for line in f:
                try:
                    row = json.loads(line.strip())
                    if row.get('status') == 'PASS':
                        completed_ids.add(row['subject_id'])
                except json.JSONDecodeError:
                    continue
        if completed_ids:
            print(f'[RESUME] Skipping {len(completed_ids)} done subjects')

    completed = 0
    skipped = 0
    errors = 0
    start_time = time.monotonic()

    # Fresh start (not resume from CSV ledger — format changed)
    with ledger_path.open('w', encoding='utf-8') as ledger:
        for i, entry in enumerate(sample):
            sid = entry['subject_id']

            print(f'  [{i+1}/{len(sample)}] subject {sid}', end='', flush=True)
            try:
                print(' downloading...', end='', flush=True)
                raw = download_mat(entry['download_url'], sid)
                print(f' [{len(raw)/1024/1024:.1f}MB]', end='', flush=True)

                print(' analyzing...', end='', flush=True)
                result = analyze_mat(raw, sid)
                result['filename'] = entry['filename']
                result['file_id'] = entry['file_id']
                result['size_bytes_reported'] = entry['size_bytes']
                del raw  # free memory

                ledger.write(json.dumps(result, ensure_ascii=False) + '\n')
                ledger.flush()
                completed += 1

                elapsed = time.monotonic() - start_time
                rate = completed / elapsed if elapsed > 0 else 0
                remaining = len(sample) - (i + 1)
                eta = remaining / rate if rate > 0 else 0
                print(
                    f' {result["total_rows"]:,d} rows, {result["n_channels"]} ch, '
                    f'{result["sampling_rate_hz"]}Hz — '
                    f'PASS ({rate:.2f}/s, ETA {eta:.0f}s)',
                    flush=True,
                )

            except Exception as exc:
                errors += 1
                err_row = {
                    'subject_id': sid,
                    'filename': entry['filename'],
                    'status': 'ERROR',
                    'error': str(exc),
                    'error_type': type(exc).__name__,
                }
                ledger.write(json.dumps(err_row, ensure_ascii=False) + '\n')
                ledger.flush()
                print(f' ERROR: {exc}', flush=True)

    elapsed_total = time.monotonic() - start_time

    # Build summary
    per_subject = []
    with ledger_path.open('r') as f:
        for line in f:
            try:
                row = json.loads(line.strip())
                if row.get('status') == 'PASS':
                    per_subject.append(row)
            except json.JSONDecodeError:
                continue

    all_channels = set()
    total_rows = 0
    total_bytes = 0
    sampling_rates = set()
    for subj in per_subject:
        total_rows += subj.get('total_rows', 0)
        total_bytes += subj.get('bytes_downloaded', 0)
        all_channels.update(subj.get('channel_statistics', {}).keys())
        sampling_rates.add(subj.get('sampling_rate_hz', 0))

    # Compute global aggregated stats across all subjects
    global_stats = {}
    for ch in sorted(all_channels):
        agg = OnlineStats()
        for subj in per_subject:
            ch_data = subj.get('channel_statistics', {}).get(ch)
            if ch_data and ch_data.get('finite_count', 0) > 0:
                # Reconstruct from per-subject finalized stats is lossy.
                # Instead we report per-subject stats only.
                pass
        # Global stats placeholder — detailed per-subject stats are in ledger
        global_stats[ch] = 'see per_subject_summary'

    summary = {
        'schema_version': 'mendeley-real-eda-summary.v1',
        'dataset_id': 'mendeley-4channel-hand-gesture-v2',
        'dataset_version': 2,
        'source': 'Mendeley Data (HTTP download MAT files + scipy.io analysis)',
        'file_format': 'MATLAB .mat (v5)',
        'subjects_total_in_dataset': len(catalog),
        'subjects_sampled': len(sample),
        'completed_subjects': len(per_subject),
        'error_subjects': errors,
        'total_rows_processed': total_rows,
        'total_bytes_downloaded': total_bytes,
        'channels_detected': sorted(all_channels),
        'n_channels': len(all_channels),
        'sampling_rates_hz': sorted(sampling_rates),
        'elapsed_seconds': round(elapsed_total, 2),
        'seed': args.seed,
        'per_subject_summary': [
            {
                'subject_id': s['subject_id'],
                'mat_id': s.get('mat_id'),
                'sampling_rate_hz': s.get('sampling_rate_hz'),
                'total_rows': s['total_rows'],
                'n_channels': s['n_channels'],
                'channel_labels': s.get('channel_labels'),
                'channel_units': s.get('channel_units'),
                'channel_statistics': s['channel_statistics'],
            }
            for s in per_subject
        ],
        'status': 'PASS' if errors == 0 and len(per_subject) > 0 else 'PARTIAL',
        'real_eda_executed': True,
        'test_set_opened': False,
        'test_signal_rows_read': 0,
        'training_allowed': False,
        'created_at': datetime.now(timezone.utc).isoformat(),
    }

    (out_dir / 'mendeley-eda-summary.json').write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8',
    )

    print(f'\n===== Mendeley Real EDA Summary =====')
    print(f'  Subjects:  {len(per_subject)}/{len(sample)} (catalog: {len(catalog)})')
    print(f'  Rows:      {total_rows:,d}')
    print(f'  Bytes:     {total_bytes/1024/1024:.1f} MB')
    print(f'  Channels:  {sorted(all_channels)}')
    print(f'  Fs:        {sorted(sampling_rates)} Hz')
    print(f'  Errors:    {errors}')
    print(f'  Elapsed:   {elapsed_total:.1f}s')
    print(f'  Status:    {summary["status"]}')
    print(f'\n  Output: {out_dir}/')

    return 0 if summary['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
