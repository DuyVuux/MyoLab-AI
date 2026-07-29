from __future__ import annotations

import random
import sys
import time
import tracemalloc
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core" / "data"))
sys.path.insert(0, str(ROOT / "scripts" / "dev"))

from day30.storage_contract import validate_window_rows
from day30.windowing import build_window_rows
from stress_test_day30 import run_stress


def test_large_window_index_is_deterministic_and_bounded() -> None:
    rng = random.Random(30)
    rows: list[dict] = []
    started = time.perf_counter()
    tracemalloc.start()
    for index in range(1_000):
        sampling_rate = rng.choice((2000, 2048))
        n_samples = rng.randint(sampling_rate, sampling_rate * 3)
        record = {
            "dataset_id": "stress-source",
            "record_id": f"record-{index}",
            "subject_id": f"subject-{index}",
            "day_id": "day-1",
            "session_id": "session-1",
            "repetition_id": "rep-1",
            "canonical_label": "rest",
            "partition": "train",
            "signal_path": f"/zone2/train/record-{index}.datx",
            "source_file_sha256": f"{index:064x}",
            "split_version": "stress-split-v1",
            "label_mapping_version": "stress-labels-v1",
            "sampling_rate_hz": sampling_rate,
            "n_samples": n_samples,
        }
        generated = build_window_rows(record, 200, 100, "stress-c", "stress-p")
        assert all(row["end_sample_exclusive"] <= n_samples for row in generated)
        rows.extend(generated)
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    elapsed_seconds = time.perf_counter() - started

    validation = validate_window_rows(rows)
    assert validation["pass"] is True
    assert validation["row_count"] >= 15_000
    assert elapsed_seconds < 10.0
    assert peak_bytes < 256 * 1024 * 1024


def test_stress_runner_is_reproducible_and_blocks_storage_mutations() -> None:
    first = run_stress(64)
    second = run_stress(64)

    assert first["pass"] is True
    assert first["window_id_digest_sha256"] == second["window_id_digest_sha256"]
    assert first["generated_windows"] == second["generated_windows"]
    assert first["forbidden_partition_attacks_blocked"] == first[
        "forbidden_partition_attacks"
    ]
    assert first["storage_mutation_attacks_blocked"] == first[
        "storage_mutation_attacks"
    ]
    assert first["cross_dataset_subject_collision_false_positive"] is False
