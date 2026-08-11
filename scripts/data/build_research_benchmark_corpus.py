"""DAY33 deterministic research benchmark corpus builder.

The builder creates only synthetic known-truth fixtures inside the repository. Public
raw datasets are registered by metadata and must live outside the repository. It uses
DAY22 WindowIdentity and preserves the DAY32 evidence-tier boundary.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from decimal import Decimal
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import yaml

try:
    from semg_core.qc_windowing import (
        CanonicalChannelTimeline,
        WindowingProfile,
        build_window_identities,
    )
except ImportError as exc:  # pragma: no cover - dependency boundary
    raise RuntimeError(
        "DAY33 requires live DAY22 semg_core.qc_windowing contract"
    ) from exc


BUILDER_VERSION = "day33-corpus-builder.v0.1.0"
GENERATOR_VERSION = "day33-synthetic-factory.v0.1.0"
DEVELOPMENT_SCENARIOS = (
    "CLEAN",
    "MISSING",
    "ZERO_DROPOUT",
    "FLATLINE",
    "CLIPPING",
    "BASELINE_NOISE",
    "POWERLINE_50HZ",
    "MOTION_DRIFT",
    "MOTION_TRANSIENT",
    "SYNTHETIC_LOW_AMPLITUDE_STRESS",
    "TIMESTAMP_DUPLICATE",
    "TIMESTAMP_NON_MONOTONIC",
)
LOCKED_SCENARIOS = (
    "MISSING",
    "CLIPPING",
    "POWERLINE_50HZ",
    "MOTION_TRANSIENT",
    "SYNTHETIC_LOW_AMPLITUDE_STRESS",
    "TIMESTAMP_NON_MONOTONIC",
)
FORBIDDEN_PATHOLOGY_TOKENS = (
    "stroke",
    "paresis",
    "paralysis",
    "atrophy",
    "diagnosis",
)


@dataclass(frozen=True)
class SyntheticFixture:
    samples: np.ndarray
    time_seconds: np.ndarray
    truth_class: str
    transform_chain: tuple[str, ...]


def _base_signal(seed: int, fs: int, n: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    t = np.arange(n, dtype=float) / float(fs)
    x = 0.12 * np.sin(2.0 * np.pi * 80.0 * t)
    x += 0.04 * np.sin(2.0 * np.pi * 120.0 * t)
    x += rng.normal(0.0, 0.01, n)
    return x.astype(np.float64), t.astype(np.float64)


def build_fixture(
    scenario: str,
    *,
    seed: int,
    fs: int = 2000,
    n: int = 2000,
) -> SyntheticFixture:
    samples, time_seconds = _base_signal(seed, fs, n)
    transform = ["DAY33_BASE_SYNTHETIC_SIGNAL"]
    truth = "NO_INJECTED_ARTIFACT"
    a, b = n // 3, n // 3 + max(20, n // 10)
    if scenario == "CLEAN":
        pass
    elif scenario == "MISSING":
        samples[a:b] = np.nan
        truth = "MISSING_INJECTED"
        transform.append("INJECT_NAN_MISSING_SEGMENT")
    elif scenario == "ZERO_DROPOUT":
        samples[a:b] = 0.0
        truth = "ZERO_DROPOUT_INJECTED"
        transform.append("INJECT_ZERO_DROPOUT_SEGMENT")
    elif scenario == "FLATLINE":
        samples[a:b] = 0.015
        truth = "FLATLINE_INJECTED"
        transform.append("INJECT_CONSTANT_PLATEAU")
    elif scenario == "CLIPPING":
        samples[a:b] = np.clip(samples[a:b] * 30.0, -0.5, 0.5)
        truth = "CLIPPING_INJECTED"
        transform.append("INJECT_RAIL_CLIPPING")
    elif scenario == "BASELINE_NOISE":
        rng = np.random.default_rng(seed + 3300)
        samples = samples + rng.normal(0.0, 0.12, n)
        truth = "BASELINE_NOISE_INJECTED"
        transform.append("INJECT_BROADBAND_BASELINE_NOISE")
    elif scenario == "POWERLINE_50HZ":
        samples = samples + 0.30 * np.sin(2.0 * np.pi * 50.0 * time_seconds)
        truth = "POWERLINE_50HZ_INJECTED"
        transform.append("ADD_50HZ_SINUSOID")
    elif scenario == "MOTION_DRIFT":
        samples = samples + 0.50 * np.sin(2.0 * np.pi * 2.0 * time_seconds)
        truth = "LOW_FREQUENCY_DRIFT_INJECTED"
        transform.append("ADD_2HZ_BASELINE_DRIFT")
    elif scenario == "MOTION_TRANSIENT":
        c = n // 2
        samples[c:c + 20] += np.linspace(0.0, 2.0, 20)
        truth = "MOVEMENT_TRANSIENT_INJECTED"
        transform.append("ADD_HIGH_AMPLITUDE_TRANSIENT")
    elif scenario == "SYNTHETIC_LOW_AMPLITUDE_STRESS":
        samples = samples * 0.10
        truth = "LOW_AMPLITUDE_ENGINEERING_STRESS"
        transform.append("SCALE_AMPLITUDE_0_10_NON_PATHOLOGY")
    elif scenario == "TIMESTAMP_DUPLICATE":
        time_seconds = time_seconds.copy()
        time_seconds[a] = time_seconds[a - 1]
        truth = "TIMESTAMP_DUPLICATE_INJECTED"
        transform.append("DUPLICATE_RAW_TIMESTAMP")
    elif scenario == "TIMESTAMP_NON_MONOTONIC":
        time_seconds = time_seconds.copy()
        time_seconds[a] = time_seconds[a - 1] - 1.0 / fs
        truth = "TIMESTAMP_NON_MONOTONIC_INJECTED"
        transform.append("REVERSE_ONE_RAW_TIMESTAMP_STEP")
    else:
        raise ValueError(f"unsupported scenario: {scenario}")
    return SyntheticFixture(samples, time_seconds, truth, tuple(transform))


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _source_id(samples: np.ndarray, times: np.ndarray) -> str:
    payload = samples.tobytes() + times.tobytes()
    return "src_sha256_" + _sha256_bytes(payload)


def _window_for_fixture(
    source_id: str,
    seed: int,
    fs: int,
    n: int,
):
    profile = WindowingProfile(
        profile_id="day33-research-corpus-250ms",
        version="0.1.0",
        requested_duration_seconds=Decimal("0.25"),
        requested_step_seconds=Decimal("0.25"),
        rounding_policy="HALF_UP",
        boundary_policy="DROP_PARTIAL",
        context_before_seconds=Decimal("0.25"),
        context_after_seconds=Decimal("0.25"),
        context_boundary_policy="CLIP_TO_SIGNAL",
    )
    timeline = CanonicalChannelTimeline(
        session_id=f"day33_syn_session_{seed}",
        channel_id="channel_semg_01",
        source_id=source_id,
        sample_count=n,
        sampling_rate_hz=Decimal(str(fs)),
        protocol_context_ref="protocol_day33_synthetic_challenge",
        domain_context_ref="domain_day33_synthetic_research",
    )
    windows = build_window_identities(timeline, profile)
    if len(windows) < 2:
        raise RuntimeError("synthetic fixture too short for contextual window")
    return windows[len(windows) // 2]


def _item_id(
    partition: str,
    seed: int,
    source_id: str,
    window_id: str,
) -> str:
    payload = json.dumps(
        {
            "partition": partition,
            "seed": seed,
            "source_id": source_id,
            "window_id": window_id,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return "rbw_sha256_" + hashlib.sha256(payload).hexdigest()


def _truth_commitment(item_id: str, scenario: str, truth_class: str) -> str:
    payload = json.dumps(
        {
            "item_id": item_id,
            "scenario": scenario,
            "truth_class": truth_class,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def _window_context(window: Any) -> dict[str, Any]:
    return {
        "window_id": window.window_id,
        "session_id": window.session_id,
        "channel_id": window.channel_id,
        "source_id": window.source_id,
        "start_sample": window.start_sample,
        "end_sample_exclusive": window.end_sample_exclusive,
        "context_start_sample": window.context_start_sample,
        "context_end_sample_exclusive": window.context_end_sample_exclusive,
        "sampling_rate_hz": float(window.sampling_rate_hz),
        "windowing_profile_fingerprint": window.windowing_profile_fingerprint,
        "annotation_unit_type": window.annotation_unit_type,
    }


def _validate_no_pathology_claim(item: dict[str, Any]) -> None:
    serialized = json.dumps(item, sort_keys=True).lower()
    if any(token in serialized for token in FORBIDDEN_PATHOLOGY_TOKENS):
        raise ValueError("synthetic fixture contains forbidden pathology/diagnosis claim")


def _public_sources(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    sources = []
    for dataset in catalog["datasets"]:
        if not dataset.get("corpus_eligible"):
            continue
        if dataset.get("license_status") != "VERIFIED":
            raise ValueError(
                f"corpus-eligible dataset {dataset['dataset_id']} lacks verified license"
            )
        if dataset.get("raw_payload_in_repo") is not False:
            raise ValueError("public raw payload must not be committed")
        sources.append(
            {
                "dataset_id": dataset["dataset_id"],
                "license_status": "VERIFIED",
                "acquisition_status": dataset["acquisition_status"],
                "raw_payload_in_repo": False,
            }
        )
    if not sources:
        raise ValueError("at least one verified public source is required")
    return sources


def build_corpus(catalog_path: Path, output_root: Path) -> dict[str, Any]:
    catalog = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    public_sources = _public_sources(catalog)
    signal_root = output_root / "signals"
    signal_root.mkdir(parents=True, exist_ok=True)
    items: list[dict[str, Any]] = []
    commitments: list[dict[str, str]] = []
    seed_sets: dict[str, set[int]] = {
        "benchmark-development": set(),
        "benchmark-locked": set(),
    }
    specs = []
    for index, scenario in enumerate(DEVELOPMENT_SCENARIOS):
        specs.append(("benchmark-development", scenario, 33000 + index))
    for index, scenario in enumerate(LOCKED_SCENARIOS):
        specs.append(("benchmark-locked", scenario, 33900 + index))
    for partition, scenario, seed in specs:
        seed_sets[partition].add(seed)
        fixture = build_fixture(scenario, seed=seed)
        source_id = _source_id(fixture.samples, fixture.time_seconds)
        window = _window_for_fixture(source_id, seed, 2000, fixture.samples.size)
        item_id = _item_id(partition, seed, source_id, window.window_id)
        signal_name = f"{item_id}.npz"
        signal_path = signal_root / signal_name
        np.savez_compressed(
            signal_path,
            samples=fixture.samples,
            time_seconds=fixture.time_seconds,
        )
        signal_sha = _sha256_bytes(signal_path.read_bytes())
        synthetic_truth = None
        if partition == "benchmark-development":
            synthetic_truth = {
                "scenario": scenario,
                "truth_class": fixture.truth_class,
                "clinical_truth_claim": False,
            }
        else:
            commitments.append(
                {
                    "item_id": item_id,
                    "truth_commitment_sha256": _truth_commitment(
                        item_id,
                        scenario,
                        fixture.truth_class,
                    ),
                }
            )
        item = {
            "item_id": item_id,
            "partition": partition,
            "evidence_tier": "SYNTHETIC_KNOWN_TRUTH",
            "source_context": {
                "source_class": "SYNTHETIC_FIXTURE",
                "dataset_id": "DAY33_SYNTHETIC_CORPUS",
                "license_status": "NOT_APPLICABLE",
                "clinical_evidence": False,
                "direct_identifiers_present": False,
            },
            "window_context": _window_context(window),
            "signal_artifact": {
                "relative_path": f"signals/{signal_name}",
                "sha256": signal_sha,
                "raw_patient_data": False,
            },
            "synthetic_truth": synthetic_truth,
            "claim_scope": "RESEARCH_ONLY",
            "provenance": {
                "seed": seed,
                "generator_version": GENERATOR_VERSION,
                "transform_chain": list(fixture.transform_chain),
            },
        }
        _validate_no_pathology_claim(item)
        items.append(item)
    if seed_sets["benchmark-development"] & seed_sets["benchmark-locked"]:
        raise RuntimeError("development and locked partitions share seeds")
    manifest = {
        "schema_version": "research-benchmark-corpus.v0.1",
        "claim_scope": "RESEARCH_ONLY",
        "project_mode": "INDEPENDENT_RESEARCH_PORTFOLIO",
        "public_sources": public_sources,
        "partition_policy": {
            "development_partition": "benchmark-development",
            "locked_partition": "benchmark-locked",
            "locked_truth_visible_to_day33": False,
            "partition_seed_overlap_forbidden": True,
        },
        "items": items,
        "locked_truth_commitments": commitments,
        "provenance": {
            "builder_version": BUILDER_VERSION,
            "catalog_version": "public-semg-catalog.v0.1",
            "day32_contract_version": "qc-annotation-research.v0.2",
            "window_identity_contract": "QC_WINDOW_WITH_CONTEXT",
            "clinical_evidence": False,
        },
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "research-benchmark-corpus-v0.1.manifest.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False),
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    manifest = build_corpus(args.catalog, args.output_root)
    print(
        json.dumps(
            {
                "status": "PASS",
                "items": len(manifest["items"]),
                "public_sources": len(manifest["public_sources"]),
                "locked_commitments": len(manifest["locked_truth_commitments"]),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
