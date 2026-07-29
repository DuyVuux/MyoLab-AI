"""Real EDA on GRABMyo v1.1.0 via wfdb streaming from PhysioNet.

Streams a stratified sample of records directly from PhysioNet
(no local archive download), computes per-channel statistics using
the OnlineStats Welford engine, and writes evidence to ZONE 2.

Features:
  - Retry logic (3 attempts with exponential backoff) for network errors
  - Single-pass streaming (no double-fetch)
  - Cross-day / cross-gesture audit
  - Resume from existing ledger via --resume

Governance:
  - No training — output training_allowed is always False.
  - No test signal access.

Usage:
  python3 scripts/data/run_grabmyo_real_eda.py \\
    --output-dir /path/to/zone2/evidence/day29 \\
    --max-records 120 \\
    --seed 292026
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

try:
    import wfdb
except ImportError:
    print('ERROR: wfdb library required. Install: pip install wfdb>=4.1', file=sys.stderr)
    sys.exit(1)


# ─── OnlineStats (self-contained) ────────────────────────────────────────

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
        if finite.size > 0:
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


# ─── GRABMyo constants ───────────────────────────────────────────────────

PHYSIONET_DB = 'grabmyo/1.1.0'
N_PARTICIPANTS = 43
N_SESSIONS = 3
N_GESTURES = 17
N_TRIALS = 7
EXPECTED_FS = 2048
EXPECTED_N_SIG = 32
EXPECTED_SIG_LEN = 10240

GESTURE_NAMES = {
    1: 'Lateral Prehension', 2: 'Thumb Adduction',
    3: 'Thumb and Little Finger Opposition',
    4: 'Thumb and Index Finger Opposition',
    5: 'Thumb and Index Finger Extension',
    6: 'Thumb and Little Finger Extension',
    7: 'Index and Middle Finger Extension',
    8: 'Little Finger Extension', 9: 'Index Finger Extension',
    10: 'Thumb Finger Extension', 11: 'Wrist Extension',
    12: 'Wrist Flexion', 13: 'Forearm Supination',
    14: 'Forearm Pronation', 15: 'Hand Open', 16: 'Hand Close',
    17: 'Rest',
}

MAX_RETRIES = 3
RETRY_BACKOFF = [2, 5, 10]  # seconds


# ─── Helpers ──────────────────────────────────────────────────────────────

def build_stratified_sample(max_records: int, seed: int) -> list[dict]:
    """Build a stratified sample covering all sessions and gestures."""
    import random
    rng = random.Random(seed)

    all_records = []
    for session in range(1, N_SESSIONS + 1):
        for participant in range(1, N_PARTICIPANTS + 1):
            for gesture in range(1, N_GESTURES + 1):
                for trial in range(1, N_TRIALS + 1):
                    all_records.append({
                        'session_id': session,
                        'subject_id': participant,
                        'gesture_id': gesture,
                        'trial_id': trial,
                    })

    groups: dict[tuple, list] = defaultdict(list)
    for r in all_records:
        groups[(r['session_id'], r['gesture_id'])].append(r)
    for rows in groups.values():
        rng.shuffle(rows)

    selected: list[dict] = []
    group_keys = sorted(groups.keys())
    idx = 0
    while len(selected) < max_records:
        made_progress = False
        for key in group_keys:
            rows = groups[key]
            if idx < len(rows) and len(selected) < max_records:
                selected.append(rows[idx])
                made_progress = True
        idx += 1
        if not made_progress:
            break
    return selected


def record_key(rec: dict) -> str:
    return (
        f"session{rec['session_id']}_participant{rec['subject_id']}"
        f"_gesture{rec['gesture_id']}_trial{rec['trial_id']}"
    )


def record_path(rec: dict) -> tuple[str, str]:
    s, p = rec['session_id'], rec['subject_id']
    name = record_key(rec)
    pn_dir = f'{PHYSIONET_DB}/Session{s}/session{s}_participant{p}'
    return name, pn_dir


def fetch_with_retry(name: str, pn_dir: str) -> Any:
    """Fetch a WFDB record with retry on network errors."""
    for attempt in range(MAX_RETRIES):
        try:
            return wfdb.rdrecord(name, pn_dir=pn_dir)
        except Exception as exc:
            err_str = str(exc).lower()
            is_network = any(kw in err_str for kw in [
                'connection', 'timeout', 'incomplete', 'chunked',
                'reset', 'broken', 'eof', 'ssl',
            ])
            if is_network and attempt < MAX_RETRIES - 1:
                wait = RETRY_BACKOFF[attempt]
                print(f'\n  [RETRY {attempt+1}/{MAX_RETRIES}] {name}: {exc} — waiting {wait}s', flush=True)
                time.sleep(wait)
            else:
                raise
    raise RuntimeError(f'Exhausted retries for {name}')  # pragma: no cover


def load_completed_keys(ledger_path: Path) -> set[str]:
    """Load already-completed record keys for resume."""
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
                    rn = row.get('record_name', '')
                    if rn:
                        done.add(rn)
            except json.JSONDecodeError:
                continue
    return done


# ─── Main ─────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(
        description='Real EDA on GRABMyo v1.1.0 via wfdb streaming',
    )
    ap.add_argument('--output-dir', required=True)
    ap.add_argument('--max-records', type=int, default=120)
    ap.add_argument('--seed', type=int, default=292026)
    ap.add_argument('--resume', action='store_true',
                    help='Skip records already PASS in existing ledger')
    args = ap.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = out_dir / 'grabmyo-eda-records.jsonl'

    # Resume support
    completed_keys: set[str] = set()
    if args.resume:
        completed_keys = load_completed_keys(ledger_path)
        if completed_keys:
            print(f'[RESUME] Found {len(completed_keys)} already-completed records')

    # Build stratified sample
    sample = build_stratified_sample(args.max_records, args.seed)
    print(f'[INFO] Stratified sample: {len(sample)} records')
    print(f'[INFO] Sessions: {sorted(set(r["session_id"] for r in sample))}')
    print(f'[INFO] Gestures: {sorted(set(r["gesture_id"] for r in sample))}')
    print(f'[INFO] Subjects: {len(set(r["subject_id"] for r in sample))} unique')

    # Aggregators
    global_stats: dict[str, OnlineStats] = {}
    per_gesture_stats: dict[int, dict[str, OnlineStats]] = {}
    per_session_stats: dict[int, dict[str, OnlineStats]] = {}

    completed = 0
    skipped = 0
    errors = 0
    network_retries = 0
    start_time = time.monotonic()

    open_mode = 'a' if args.resume else 'w'
    with ledger_path.open(open_mode, encoding='utf-8') as ledger:
        for i, rec in enumerate(sample):
            name = record_key(rec)

            # Resume: skip already done
            if name in completed_keys:
                skipped += 1
                continue

            rec_name, pn_dir = record_path(rec)
            try:
                record_obj = fetch_with_retry(rec_name, pn_dir)

                # Validate
                warnings = []
                if record_obj.fs != EXPECTED_FS:
                    warnings.append(f'UNEXPECTED_FS:{record_obj.fs}')
                if record_obj.n_sig != EXPECTED_N_SIG:
                    warnings.append(f'UNEXPECTED_N_SIG:{record_obj.n_sig}')
                if record_obj.sig_len != EXPECTED_SIG_LEN:
                    warnings.append(f'UNEXPECTED_SIG_LEN:{record_obj.sig_len}')

                signal = record_obj.p_signal
                sig_names = record_obj.sig_name or [
                    f'CH{ci+1:02d}' for ci in range(signal.shape[1])
                ]

                # Compute per-channel stats (single pass)
                channels = {}
                for ci, ch_name in enumerate(sig_names):
                    col = signal[:, ci]
                    s = OnlineStats()
                    s.update(col)
                    channels[ch_name] = s.finalize()

                    # Aggregate into global
                    if ch_name not in global_stats:
                        global_stats[ch_name] = OnlineStats()
                    global_stats[ch_name].update(col)

                    # Per-gesture
                    gid = rec['gesture_id']
                    if gid not in per_gesture_stats:
                        per_gesture_stats[gid] = {}
                    if ch_name not in per_gesture_stats[gid]:
                        per_gesture_stats[gid][ch_name] = OnlineStats()
                    per_gesture_stats[gid][ch_name].update(col)

                    # Per-session
                    sid = rec['session_id']
                    if sid not in per_session_stats:
                        per_session_stats[sid] = {}
                    if ch_name not in per_session_stats[sid]:
                        per_session_stats[sid][ch_name] = OnlineStats()
                    per_session_stats[sid][ch_name].update(col)

                row = {
                    'record_name': name,
                    'session_id': rec['session_id'],
                    'subject_id': rec['subject_id'],
                    'gesture_id': rec['gesture_id'],
                    'gesture_name': GESTURE_NAMES.get(rec['gesture_id'], 'Unknown'),
                    'trial_id': rec['trial_id'],
                    'fs': record_obj.fs,
                    'n_sig': record_obj.n_sig,
                    'sig_len': record_obj.sig_len,
                    'units': list(set(record_obj.units)),
                    'status': 'PASS',
                    'warnings': warnings,
                    'channels': channels,
                }
                ledger.write(json.dumps(row, ensure_ascii=False) + '\n')
                ledger.flush()
                completed += 1

                elapsed = time.monotonic() - start_time
                rate = completed / elapsed if elapsed > 0 else 0
                eta = (len(sample) - i - 1) / rate if rate > 0 else 0
                print(
                    f'\r  [{completed+skipped+errors}/{len(sample)}] '
                    f'{name} — PASS ({rate:.1f} rec/s, ETA {eta:.0f}s)',
                    end='', flush=True,
                )

            except Exception as exc:
                errors += 1
                err_row = {
                    'record_name': name,
                    'session_id': rec['session_id'],
                    'subject_id': rec['subject_id'],
                    'gesture_id': rec['gesture_id'],
                    'trial_id': rec['trial_id'],
                    'status': 'ERROR',
                    'error': str(exc),
                    'error_type': type(exc).__name__,
                }
                ledger.write(json.dumps(err_row, ensure_ascii=False) + '\n')
                ledger.flush()
                print(f'\n  [{completed+skipped+errors}/{len(sample)}] {name} — ERROR: {exc}', flush=True)

    print()
    elapsed_total = time.monotonic() - start_time

    # Finalize summaries
    global_summary = {ch: s.finalize() for ch, s in global_stats.items()}
    gesture_summary = {
        GESTURE_NAMES.get(gid, f'gesture_{gid}'): {
            ch: s.finalize() for ch, s in chs.items()
        }
        for gid, chs in sorted(per_gesture_stats.items())
    }
    session_summary = {
        f'session_{sid}': {
            ch: s.finalize() for ch, s in chs.items()
        }
        for sid, chs in sorted(per_session_stats.items())
    }

    sessions_covered = sorted(per_session_stats.keys())
    cross_day_audit = {
        'sessions_covered': sessions_covered,
        'sessions_expected': [1, 2, 3],
        'all_sessions_covered': sessions_covered == [1, 2, 3],
        'gestures_covered': sorted(per_gesture_stats.keys()),
        'all_gestures_covered': len(per_gesture_stats) == N_GESTURES,
    }

    summary = {
        'schema_version': 'grabmyo-real-eda-summary.v1',
        'dataset_id': 'GRABMYO_V1_1',
        'dataset_version': '1.1.0',
        'source': 'PhysioNet (wfdb streaming)',
        'access_method': 'wfdb.rdrecord (no local archive)',
        'sample_size': len(sample),
        'completed_records': completed,
        'skipped_resume': skipped,
        'error_records': errors,
        'elapsed_seconds': round(elapsed_total, 2),
        'records_per_second': round(completed / elapsed_total, 2) if elapsed_total > 0 else 0,
        'seed': args.seed,
        'cross_day_audit': cross_day_audit,
        'global_channel_statistics': global_summary,
        'status': 'PASS' if errors == 0 and completed > 0 else 'PARTIAL',
        'real_eda_executed': True,
        'test_set_opened': False,
        'test_signal_rows_read': 0,
        'training_allowed': False,
        'created_at': datetime.now(timezone.utc).isoformat(),
    }

    # Write outputs
    for fname, data in [
        ('grabmyo-eda-summary.json', summary),
        ('grabmyo-eda-per-gesture.json', gesture_summary),
        ('grabmyo-eda-per-session.json', session_summary),
    ]:
        (out_dir / fname).write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + '\n',
            encoding='utf-8',
        )

    print(f'\n===== GRABMyo Real EDA Summary =====')
    print(f'  Completed: {completed}/{len(sample)} records')
    print(f'  Skipped:   {skipped} (resume)')
    print(f'  Errors:    {errors}')
    print(f'  Elapsed:   {elapsed_total:.1f}s ({summary["records_per_second"]:.1f} rec/s)')
    print(f'  Cross-day: all sessions = {cross_day_audit["all_sessions_covered"]}')
    print(f'  Gestures:  {len(per_gesture_stats)}/{N_GESTURES}')
    print(f'  Status:    {summary["status"]}')
    print(f'\n  Output: {out_dir}/')

    return 0 if summary['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
