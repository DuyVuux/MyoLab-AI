#!/usr/bin/env python3
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import random
import sys
import time
import tracemalloc
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "data"))

from day30.normalization import remove_dc_mean
from day30.sample_rate import resample_polyphase
from day30.storage_contract import validate_window_rows
from day30.windowing import build_window_rows


def _record(index: int, sampling_rate: int, n_samples: int) -> dict:
    return {
        "dataset_id": "day30-stress-source",
        "record_id": f"record-{index}",
        "subject_id": f"subject-{index}",
        "day_id": "day-1",
        "session_id": "session-1",
        "repetition_id": "rep-1",
        "canonical_label": "rest",
        "partition": "train",
        "signal_path": f"/zone2/train/record-{index}.signal",
        "source_file_sha256": f"{index:064x}",
        "split_version": "day30-stress-split-v1",
        "label_mapping_version": "day30-stress-labels-v1",
        "sampling_rate_hz": sampling_rate,
        "n_samples": n_samples,
    }


def run_stress(records: int) -> dict:
    if records <= 0:
        raise ValueError("records must be positive")
    rng = random.Random(30)
    started = time.perf_counter()
    tracemalloc.start()
    rows: list[dict] = []
    for index in range(records):
        sampling_rate = rng.choice((2000, 2048))
        n_samples = rng.randint(sampling_rate, sampling_rate * 3)
        generated = build_window_rows(
            _record(index, sampling_rate, n_samples),
            200,
            100,
            "day30-stress-channels-v1",
            "day30-stress-preprocessing-v1",
        )
        if any(row["end_sample_exclusive"] > n_samples for row in generated):
            raise AssertionError("generated window exceeded its record")
        rows.extend(generated)
    validation = validate_window_rows(rows)

    digest = sha256()
    for row in rows:
        digest.update(row["window_id"].encode("ascii"))
        digest.update(b"\n")
    window_id_digest = digest.hexdigest()

    attacks = [
        ("test", "/zone2/test/a.signal"),
        ("sealed_test", "/zone2/data/a.signal"),
        ("outer_test", "/zone2/data/a.signal"),
        ("validation", "/zone2/sealed-test/a.signal"),
        ("validation", "/zone2/outer_test/a.signal"),
        ("unknown", "/zone2/data/a.signal"),
    ]
    blocked = 0
    for index, (partition, signal_path) in enumerate(attacks, start=records):
        attack = _record(index, 2000, 1000)
        attack.update({"partition": partition, "signal_path": signal_path})
        try:
            build_window_rows(attack, 200, 100, "c", "p")
        except PermissionError:
            blocked += 1

    baseline_row = rows[0]
    storage_mutations = [
        {"sampling_rate_hz": float("nan")},
        {"source_file_sha256": "not-a-hash"},
        {"signal_path": "/zone2/sealed-test/a.signal"},
        {"canonical_label": "unregistered_gesture"},
        {"window_id": "not-a-window-id"},
        {"window_ms": 0},
        {"hop_ms": 0},
        {"start_sample": 0.5},
    ]
    storage_mutation_attacks_blocked = 0
    for mutation in storage_mutations:
        candidate = dict(baseline_row)
        candidate.update(mutation)
        if not validate_window_rows([candidate])["pass"]:
            storage_mutation_attacks_blocked += 1
    if not validate_window_rows([baseline_row, dict(baseline_row)])["pass"]:
        storage_mutation_attacks_blocked += 1
    storage_mutation_attack_count = len(storage_mutations) + 1

    collision_record = _record(records + len(attacks), 2000, 1000)
    collision_record.update(
        {
            "dataset_id": "day30-stress-other-source",
            "subject_id": baseline_row["subject_id"],
            "partition": "validation",
            "signal_path": "/zone2/validation/collision.signal",
        }
    )
    collision_rows = build_window_rows(
        collision_record,
        200,
        100,
        "day30-stress-channels-v1",
        "day30-stress-preprocessing-v1",
    )
    cross_dataset_subject_collision_false_positive = not validate_window_rows(
        [baseline_row, collision_rows[0]]
    )["pass"]

    signal = rng.random() * np.ones((2048, 4), dtype=float)
    signal += np.linspace(-1.0, 1.0, 2048)[:, None]
    dc_removed = remove_dc_mean(signal, axis=0)
    resampled = resample_polyphase(dc_removed, 2048, 2000, axis=0)
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    elapsed = time.perf_counter() - started
    pass_result = (
        validation["pass"]
        and blocked == len(attacks)
        and storage_mutation_attacks_blocked == storage_mutation_attack_count
        and not cross_dataset_subject_collision_false_positive
        and resampled.shape == (2000, 4)
        and bool(np.isfinite(resampled).all())
        and peak_bytes < 256 * 1024 * 1024
        and elapsed < 30.0
    )
    return {
        "schema_version": "day30-stress-test.v1",
        "seed": 30,
        "input_records": records,
        "generated_windows": len(rows),
        "window_id_digest_sha256": window_id_digest,
        "window_validation": validation,
        "forbidden_partition_attacks": len(attacks),
        "forbidden_partition_attacks_blocked": blocked,
        "storage_mutation_attacks": storage_mutation_attack_count,
        "storage_mutation_attacks_blocked": storage_mutation_attacks_blocked,
        "cross_dataset_subject_collision_false_positive": cross_dataset_subject_collision_false_positive,
        "resampled_shape": list(resampled.shape),
        "finite_signal_output": bool(np.isfinite(resampled).all()),
        "elapsed_seconds": round(elapsed, 6),
        "peak_memory_mib": round(peak_bytes / (1024 * 1024), 3),
        "thresholds": {
            "max_elapsed_seconds": 30.0,
            "max_peak_memory_mib": 256.0,
        },
        "training_executed": False,
        "test_signal_rows_read": 0,
        "pass": pass_result,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=int, default=5_000)
    parser.add_argument(
        "--output",
        default="qa-validation/evidence/day30/day30-stress-test.json",
    )
    args = parser.parse_args()
    try:
        result = run_stress(args.records)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["pass"] else 2
    except (OSError, ValueError, TypeError, AssertionError) as error:
        print(f"day30 stress test failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
