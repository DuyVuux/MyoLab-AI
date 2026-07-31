#!/usr/bin/env python3
"""Quick local test: run ETL pipeline on cached MAT files (9 subjects).

This verifies the full pipeline end-to-end without downloading from Mendeley.
Uses the 9 MAT files cached in myolab-ai-data from the Day 28 EDA run.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import scipy.io

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "semg-core"))
sys.path.insert(0, str(ROOT / "ai-core" / "data"))
sys.path.insert(0, str(ROOT / "ai-core" / "modeling"))
sys.path.insert(0, str(ROOT / "scripts" / "data"))

DATA_ROOT = Path("/home/duyvd9/massive/projects/semg-fatigue/myolab-ai-data")
CACHE_DIR = DATA_ROOT / "external" / "mendeley-4channel-hand-gesture-v2" / "cache" / "downloads"
OUTPUT_DIR = DATA_ROOT / "external" / "mendeley-4channel-hand-gesture-v2" / "derived"

GESTURE_NAMES = [
    "rest", "wrist_extension", "wrist_flexion",
    "ulnar_deviation", "radial_deviation", "grip",
    "abduction_all_fingers", "adduction_all_fingers",
    "supination", "pronation",
]

LABEL_MAP = {
    "rest": "rest",
    "wrist_extension": "wrist_extension",
    "wrist_flexion": "wrist_flexion",
    "grip": "hand_close",
}

PRIMARY_CHANNELS = ("EMG_Raw_CH1", "EMG_RAW_CH2", "EMG_RAW_CH3")
WINDOW_MS = 200
HOP_MS = 100


def main() -> int:
    # ── Step 0: Find cached MAT files ──
    mat_files = sorted(CACHE_DIR.glob("*_raw.mat"))
    if not mat_files:
        print(f"ERROR: No cached MAT files in {CACHE_DIR}")
        return 1
    print(f"[Step 0] Found {len(mat_files)} cached MAT files")

    # ── Step 1: Parse MAT files → save as NPY ──
    acquired_dir = OUTPUT_DIR / "acquired"
    acquired_dir.mkdir(parents=True, exist_ok=True)
    records = []

    for mat_path in mat_files:
        sid = mat_path.stem.replace("_raw", "")
        print(f"  Parsing subject {sid}...", end=" ", flush=True)
        raw_bytes = mat_path.read_bytes()
        mat = scipy.io.loadmat(io.BytesIO(raw_bytes))
        data = mat["data"]
        fs = int(mat["fs"].flat[0])
        n_total, n_ch = data.shape
        samples_per_gesture = n_total // len(GESTURE_NAMES)

        for g_idx, gesture_name in enumerate(GESTURE_NAMES):
            canonical = LABEL_MAP.get(gesture_name)
            if canonical is None:
                continue
            start = g_idx * samples_per_gesture
            end = (g_idx + 1) * samples_per_gesture
            gesture_signal = data[start:end, :].astype(np.float64)

            record_id = f"mendeley-{sid}-{gesture_name}"
            signal_path = acquired_dir / "train" / f"{record_id}.npy"
            signal_path.parent.mkdir(parents=True, exist_ok=True)
            np.save(signal_path, gesture_signal)
            signal_sha = hashlib.sha256(signal_path.read_bytes()).hexdigest()

            records.append({
                "dataset_id": "mendeley-4channel-hand-gesture-v2",
                "record_id": record_id,
                "subject_id": f"mendeley-S{sid}",
                "day_id": "day-1",
                "session_id": "session-1",
                "repetition_id": f"S{sid}-{gesture_name}-R0",
                "canonical_label": canonical,
                "partition": "train",
                "signal_path": str(signal_path),
                "source_file_sha256": signal_sha,
                "split_version": "day30-mendeley-real-v1",
                "label_mapping_version": "MENDELEY_4CH_GESTURE.taskA.v0.1",
                "sampling_rate_hz": fs,
                "n_samples": gesture_signal.shape[0],
            })
        print(f"{n_total:,} rows, {fs}Hz", flush=True)
    del raw_bytes

    # ── Step 2: Train/validation split ──
    from sklearn.model_selection import StratifiedGroupKFold

    all_subjects = sorted(set(r["subject_id"] for r in records))
    y_arr = np.array([r["canonical_label"] for r in records])
    g_arr = np.array([r["subject_id"] for r in records])

    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=3001)
    dummy_X = np.zeros((len(records), 1))
    for fold_idx, (train_idx, val_idx) in enumerate(splitter.split(dummy_X, y_arr, g_arr)):
        if fold_idx == 0:
            val_subjects = set(g_arr[val_idx])
            break

    for r in records:
        if r["subject_id"] in val_subjects:
            r["partition"] = "validation"
            old = Path(r["signal_path"])
            new_path = acquired_dir / "validation" / old.name
            new_path.parent.mkdir(parents=True, exist_ok=True)
            if old.exists():
                old.rename(new_path)
                r["signal_path"] = str(new_path)
                r["source_file_sha256"] = hashlib.sha256(new_path.read_bytes()).hexdigest()

    train_n = sum(1 for r in records if r["partition"] == "train")
    val_n = sum(1 for r in records if r["partition"] == "validation")
    print(f"[Step 2] Split: {train_n} train, {val_n} validation, {len(all_subjects)} subjects")

    # ── Step 3: Build window index ──
    from day30.windowing import build_window_rows

    window_rows = []
    for r in records:
        try:
            rows = build_window_rows(
                r, WINDOW_MS, HOP_MS,
                "mendeley-ch123-primary-v1", "per-record-channel-mean-v1",
            )
            window_rows.extend(rows)
        except Exception as exc:
            print(f"  ⚠️ Windowing failed for {r['record_id']}: {exc}")

    print(f"[Step 3] Windows: {len(window_rows)}")

    # ── Step 4: Feature extraction ──
    from semg_core.day31_features import extract_feature_set_14, FEATURE_ORDER

    feature_rows = []
    errors = 0
    t0 = time.monotonic()
    for w_idx, w in enumerate(window_rows):
        if (w_idx + 1) % 1000 == 0:
            print(f"  [{w_idx+1}/{len(window_rows)}]", flush=True)
        try:
            signal_path = Path(w["signal_path"])
            full_signal = np.load(signal_path, allow_pickle=False)
            start = int(w["start_sample"])
            end = int(w["end_sample_exclusive"])
            window_signal = full_signal[start:end, :]
            fs = float(w["sampling_rate_hz"])

            for ch_idx, ch_id in enumerate(PRIMARY_CHANNELS):
                ch_signal = window_signal[:, ch_idx] - np.mean(window_signal[:, ch_idx])
                result = extract_feature_set_14(ch_signal, fs)
                row = {
                    "subject_id": w["subject_id"],
                    "record_id": w["record_id"],
                    "window_id": w["window_id"],
                    "channel_id": ch_id,
                    "canonical_label": w["canonical_label"],
                    "partition": w["partition"],
                    "repetition_id": w.get("repetition_id", w["record_id"]),
                }
                row.update(result.features)
                feature_rows.append(row)
        except Exception:
            errors += 1

    elapsed = time.monotonic() - t0
    print(f"[Step 4] Features: {len(feature_rows)} rows, {errors} errors, {elapsed:.1f}s")

    # ── Step 5: Pivot to wide matrix ──
    window_features = defaultdict(dict)
    window_meta = {}
    for row in feature_rows:
        wid = row["window_id"]
        ch_id = row["channel_id"]
        if wid not in window_meta:
            window_meta[wid] = {
                "subject_id": row["subject_id"],
                "canonical_label": row["canonical_label"],
                "partition": row["partition"],
                "record_id": row["record_id"],
                "repetition_id": row.get("repetition_id", row["record_id"]),
            }
        for feat in FEATURE_ORDER:
            window_features[wid][f"{ch_id}__{feat}"] = row[feat]

    feature_columns = []
    for ch_id in PRIMARY_CHANNELS:
        for feat in FEATURE_ORDER:
            feature_columns.append(f"{ch_id}__{feat}")

    n_feats = len(feature_columns)
    X_list, y_list, g_list, rep_list, split_list = [], [], [], [], []
    for wid in sorted(window_features):
        if len(window_features[wid]) != n_feats:
            continue
        X_list.append([window_features[wid].get(c, np.nan) for c in feature_columns])
        m = window_meta[wid]
        y_list.append(m["canonical_label"])
        g_list.append(m["subject_id"])
        rep_list.append(m.get("repetition_id", m["record_id"]))
        split_list.append(m["partition"])

    X = np.nan_to_num(np.array(X_list, dtype=np.float64), nan=0.0)
    y = np.array(y_list)
    groups = np.array(g_list)

    print(f"[Step 5] Matrix: X={X.shape}, y={y.shape}, "
          f"subjects={len(np.unique(groups))}, "
          f"classes={dict(zip(*np.unique(y, return_counts=True)))}")

    # ── Step 6: Save .npz ──
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "day31-features-mendeley-real.npz"
    np.savez_compressed(
        out_path,
        X=X, y=y, groups=groups,
        repetition_ids=np.array(rep_list),
        dataset_ids=np.full(len(y), "mendeley-4channel-hand-gesture-v2"),
        split_names=np.array(split_list),
        feature_columns=np.array(feature_columns),
    )
    sz = out_path.stat().st_size / 1024 / 1024
    print(f"[Step 6] Saved: {out_path} ({sz:.2f} MB)")

    # ── Step 7: Run Day 32 baselines ──
    from day32.model_factory import build_core_models, build_optional_models, CORE_MODEL_IDS, OPTIONAL_MODEL_IDS
    from day32.grouped_cv import make_grouped_folds
    from day32.core_gate import decide_core_gate
    from sklearn.metrics import f1_score, balanced_accuracy_score

    folds = make_grouped_folds(y, groups, n_splits=5, seed=3201)
    print(f"[Step 7] Running {len(CORE_MODEL_IDS)} core + {len(OPTIONAL_MODEL_IDS)} optional models × {len(folds)} folds")

    all_results = []
    for model_id in list(CORE_MODEL_IDS) + list(OPTIONAL_MODEL_IDS):
        is_core = model_id in CORE_MODEL_IDS
        factory = build_core_models if is_core else build_optional_models
        f1s, accs = [], []
        for fold in folds:
            ti = np.array(fold["train_indices"])
            vi = np.array(fold["validation_indices"])
            model = factory()[model_id]
            try:
                model.fit(X[ti], y[ti])
                pred = model.predict(X[vi])
                f1s.append(float(f1_score(y[vi], pred, average="macro", zero_division=0)))
                accs.append(float(balanced_accuracy_score(y[vi], pred)))
            except Exception as exc:
                print(f"  ⚠️ {model_id} fold {fold['fold_id']}: {exc}")

        mean_f1 = np.mean(f1s) if f1s else 0.0
        std_f1 = np.std(f1s) if f1s else 0.0
        mean_acc = np.mean(accs) if accs else 0.0
        tier = "⭐" if is_core else "🔸"
        print(f"  {tier} {model_id:<25} F1={mean_f1:.4f}±{std_f1:.4f}  BA={mean_acc:.4f}")
        all_results.append({
            "model_id": model_id,
            "mean_macro_f1": float(mean_f1),
            "std_macro_f1": float(std_f1),
            "mean_balanced_accuracy": float(mean_acc),
            "tier": "core" if is_core else "optional",
        })

    # Sort by F1
    all_results.sort(key=lambda r: r["mean_macro_f1"], reverse=True)
    print(f"\n{'='*60}")
    print("  🏆 LEADERBOARD")
    print(f"{'='*60}")
    for rank, r in enumerate(all_results, 1):
        print(f"  #{rank} {r['model_id']}: F1={r['mean_macro_f1']:.4f}")

    # Save evidence
    evidence = {
        "schema_version": "day32-real-baseline-evidence.v1",
        "scope": "MENDELEY_REAL_DATA_9SUBJECTS",
        "matrix_shape": list(X.shape),
        "n_subjects": int(len(np.unique(groups))),
        "n_classes": int(len(np.unique(y))),
        "leaderboard": all_results,
        "sealed_test_rows_read": 0,
        "pooled_training_executed": False,
    }
    evidence_path = ROOT / "qa-validation" / "evidence" / "day32" / "day32-real-baseline-evidence.json"
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"\n✅ Evidence: {evidence_path}")
    print(f"✅ Matrix: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
