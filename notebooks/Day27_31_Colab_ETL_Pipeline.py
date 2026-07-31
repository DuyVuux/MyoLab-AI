# %% [markdown]
# # 🧪 MyoLab-AI — Colab ETL Pipeline (Day 27→31)
#
# **Mục tiêu:** Tải dữ liệu thô Mendeley 4-Channel Hand Gesture v2 từ API,
# trích xuất đặc trưng (14 features × 3 channels × N windows), và xuất ra
# file `.npz` nhỏ gọn (~50-100 MB) để chạy Day 32 Baseline Modeling trên máy local.
#
# **Kiến trúc 2-Zone:**
# - Zone 1 (Code): Repo GitHub `MyoLab-AI` → clone về Colab
# - Zone 2 (Data): Tải tạm vào `/content/data/` trên Colab, KHÔNG lưu vào Drive
#
# **Quy trình:**
# 1. Clone repo & cài dependencies
# 2. Tải raw MAT files từ Mendeley API
# 3. Parse MAT → numpy, sinh metadata-index.csv
# 4. Build window index (Day 30)
# 5. Extract Feature Set 14 (Day 31)
# 6. Pivot to wide matrix `.npz` (Day 32 input)
# 7. Download `.npz` về máy local
#
# > ⚠️ **Governance:** `training_allowed=False` trong notebook này.
# > Notebook chỉ thực hiện ETL (Extract-Transform-Load), KHÔNG train model.

# %% [markdown]
# ## 0. Setup & Clone Repo

# %%
# === CELL 0: Environment Setup ===
import subprocess
import sys
import os

# Detect Colab
IN_COLAB = 'google.colab' in sys.modules if 'google.colab' in dir() else False
try:
    import google.colab
    IN_COLAB = True
except ImportError:
    IN_COLAB = False

print(f"Running in Colab: {IN_COLAB}")

# Config — EDIT THESE IF NEEDED
GITHUB_REPO = "https://github.com/DuyVuux/MyoLab-AI.git"
BRANCH = "day32"
DATA_DIR = "/content/data" if IN_COLAB else "./data_temp"
REPO_DIR = "/content/MyoLab-AI" if IN_COLAB else "."
MAX_SUBJECTS = 30  # Set to smaller number (e.g., 3) for testing

# %%
# === CELL 1: Clone repo (Colab only) ===
if IN_COLAB:
    if not os.path.exists(REPO_DIR):
        subprocess.run(
            ["git", "clone", "--branch", BRANCH, "--depth", "1", GITHUB_REPO, REPO_DIR],
            check=True,
        )
        print(f"✅ Cloned {GITHUB_REPO} branch={BRANCH}")
    else:
        print(f"ℹ️ Repo already exists at {REPO_DIR}")

    # Install dependencies
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q",
         "numpy", "scipy", "scikit-learn", "requests", "pyyaml"],
        check=True,
    )
    print("✅ Dependencies installed")

# %%
# === CELL 2: Add repo packages to Python path ===
sys.path.insert(0, os.path.join(REPO_DIR, "packages", "semg-core"))
sys.path.insert(0, os.path.join(REPO_DIR, "ai-core", "data"))
sys.path.insert(0, os.path.join(REPO_DIR, "ai-core", "modeling"))

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "acquired"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "evidence"), exist_ok=True)
print(f"✅ Python path configured, DATA_DIR={DATA_DIR}")

# %% [markdown]
# ## 1. Download Mendeley Raw Data (Day 27 — Ingestion)
#
# Sử dụng logic từ `scripts/data/run_mendeley_real_eda.py`:
# - API endpoint: `https://data.mendeley.com/api/datasets/ckwc76xr2z/files`
# - Chỉ tải `*_raw.mat` (~10MB/file, nhỏ hơn CSV 8 lần)
# - Mỗi file chứa: `data` (N×4 float64), `fs` (sampling rate), `iD` (subject ID)

# %%
# === CELL 3: Download MAT files from Mendeley API ===
import io
import json
import time
import hashlib
from pathlib import Path

import numpy as np
import requests
import scipy.io

MENDELEY_API = "https://data.mendeley.com/api/datasets/ckwc76xr2z/files"
MAX_RETRIES = 3
RETRY_BACKOFF = [5, 15, 30]

# Label mapping from repo: data-platform/manifests/.../label-dictionary.yaml
# 10 gestures per subject, only 4 core labels for Task A
GESTURE_NAMES = [
    "rest", "wrist_extension", "wrist_flexion",
    "ulnar_deviation", "radial_deviation", "grip",
    "abduction_all_fingers", "adduction_all_fingers",
    "supination", "pronation",
]

# Core label mapping (from label-dictionary.yaml)
LABEL_MAP = {
    "rest": "rest",
    "wrist_extension": "wrist_extension",
    "wrist_flexion": "wrist_flexion",
    "grip": "hand_close",
    # Non-core → excluded
    "ulnar_deviation": None,
    "radial_deviation": None,
    "abduction_all_fingers": None,
    "adduction_all_fingers": None,
    "supination": None,
    "pronation": None,
}

CORE_LABELS = {"rest", "hand_close", "wrist_flexion", "wrist_extension"}


def get_raw_mat_catalog():
    """Fetch catalog, filter to *_raw.mat files (~10MB each).
    Reuses logic from scripts/data/run_mendeley_real_eda.py
    """
    resp = requests.get(MENDELEY_API, params={"version": 2}, timeout=30)
    resp.raise_for_status()
    items = []
    for f in resp.json():
        name = f["filename"]
        if name.endswith("_raw.mat"):
            cd = f.get("content_details", {})
            sid = name.replace("_raw.mat", "")
            items.append({
                "subject_id": sid,
                "filename": name,
                "file_id": f["id"],
                "size_bytes": cd.get("size", 0),
                "download_url": cd.get("download_url", ""),
            })
    return sorted(items, key=lambda x: int(x["subject_id"]) if x["subject_id"].isdigit() else 0)


def download_mat(url, subject_id):
    """Download MAT file with retry. From run_mendeley_real_eda.py"""
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, timeout=120)
            resp.raise_for_status()
            return resp.content
        except Exception as exc:
            if attempt < MAX_RETRIES - 1:
                wait = RETRY_BACKOFF[attempt]
                print(f"\n  [RETRY {attempt+1}] subject {subject_id}: {exc} — {wait}s", flush=True)
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Exhausted retries")


print("[INFO] Fetching Mendeley file catalog...")
catalog = get_raw_mat_catalog()
print(f"[INFO] Found {len(catalog)} raw MAT files in dataset")

import random
rng = random.Random(282026)
sample = catalog[:] if len(catalog) <= MAX_SUBJECTS else rng.sample(catalog, MAX_SUBJECTS)
sample.sort(key=lambda x: int(x["subject_id"]) if x["subject_id"].isdigit() else 0)
total_mb = sum(s["size_bytes"] for s in sample) / 1024 / 1024
print(f"[INFO] Will download {len(sample)} subjects: {[s['subject_id'] for s in sample]}")
print(f"[INFO] Estimated total: {total_mb:.0f} MB")

# %%
# === CELL 4: Download & Parse MAT files, build per-gesture NPY signals ===
acquired_dir = Path(DATA_DIR) / "acquired"
evidence_dir = Path(DATA_DIR) / "evidence"

# Channel labels from the Mendeley dataset (confirmed by EDA Day 28)
CHANNEL_IDS = ("EMG_Raw_CH1", "EMG_RAW_CH2", "EMG_RAW_CH3", "EMG_RAW_CH4")
# Primary channel policy: use channels 1,2,3 (index 0,1,2)
PRIMARY_CHANNELS = ("EMG_Raw_CH1", "EMG_RAW_CH2", "EMG_RAW_CH3")

records = []  # metadata-index rows
download_errors = []
start_time = time.monotonic()

for i, entry in enumerate(sample):
    sid = entry["subject_id"]
    mat_path = acquired_dir / f"{sid}_raw.mat"

    print(f"  [{i+1}/{len(sample)}] subject {sid}", end="", flush=True)

    # Check if already cached (either in Colab temp or external data dir)
    cache_path = Path(DATA_DIR) / "cache" / f"{sid}_raw.mat"
    if mat_path.exists():
        print(" [cached]", end="", flush=True)
        raw_bytes = mat_path.read_bytes()
    elif cache_path.exists():
        print(" [cache-hit]", end="", flush=True)
        raw_bytes = cache_path.read_bytes()
        mat_path.write_bytes(raw_bytes)
    else:
        try:
            print(" downloading...", end="", flush=True)
            raw_bytes = download_mat(entry["download_url"], sid)
            mat_path.write_bytes(raw_bytes)
            print(f" [{len(raw_bytes)/1024/1024:.1f}MB]", end="", flush=True)
        except Exception as exc:
            download_errors.append({"subject_id": sid, "error": str(exc)})
            print(f" ERROR: {exc}", flush=True)
            continue

    # Parse MAT file (logic from run_mendeley_real_eda.py → analyze_mat)
    try:
        mat = scipy.io.loadmat(io.BytesIO(raw_bytes))
        data = mat["data"]  # shape: (N_total, 4) — all gestures concatenated
        fs = int(mat["fs"].flat[0])
        mat_id = int(mat["iD"].flat[0])

        # Each subject has 10 gestures × (N_samples/10) samples per gesture
        # The data is organized as: [gesture_0_samples, gesture_1_samples, ...]
        n_total, n_channels = data.shape
        samples_per_gesture = n_total // len(GESTURE_NAMES)

        file_sha256 = hashlib.sha256(raw_bytes).hexdigest()

        # Save each gesture as a separate .npy file for windowing
        for g_idx, gesture_name in enumerate(GESTURE_NAMES):
            canonical = LABEL_MAP.get(gesture_name)
            if canonical is None:
                continue  # Skip non-core gestures

            start_sample = g_idx * samples_per_gesture
            end_sample = (g_idx + 1) * samples_per_gesture
            gesture_signal = data[start_sample:end_sample, :]  # (samples, 4)

            # Save as NPY (canonical signal format for CanonicalWindowReader)
            record_id = f"mendeley-{sid}-{gesture_name}"
            signal_filename = f"{record_id}.npy"
            signal_path = acquired_dir / "train" / signal_filename
            signal_path.parent.mkdir(parents=True, exist_ok=True)
            np.save(signal_path, gesture_signal.astype(np.float64))

            # Compute SHA-256 of the saved signal file
            signal_sha256 = hashlib.sha256(signal_path.read_bytes()).hexdigest()

            records.append({
                "dataset_id": "mendeley-4channel-hand-gesture-v2",
                "record_id": record_id,
                "subject_id": f"mendeley-S{sid}",
                "day_id": "day-1",
                "session_id": "session-1",
                "repetition_id": f"S{sid}-{gesture_name}-R0",
                "canonical_label": canonical,
                "partition": "train",  # All as train for now; split later
                "signal_path": str(signal_path.relative_to(Path(DATA_DIR))),
                "source_file_sha256": signal_sha256,
                "split_version": "day30-mendeley-real-v1",
                "label_mapping_version": "MENDELEY_4CH_GESTURE.taskA.v0.1",
                "sampling_rate_hz": fs,
                "n_samples": gesture_signal.shape[0],
                "n_channels": n_channels,
                "original_mat_sha256": file_sha256,
            })

        elapsed = time.monotonic() - start_time
        print(f" ✅ {n_total:,} rows, {n_channels}ch, {fs}Hz, {samples_per_gesture} samples/gesture", flush=True)

    except Exception as exc:
        download_errors.append({"subject_id": sid, "error": str(exc)})
        print(f" PARSE ERROR: {exc}", flush=True)

del raw_bytes  # Free memory immediately

elapsed_total = time.monotonic() - start_time
print(f"\n{'='*60}")
print(f"  Total records: {len(records)}")
print(f"  Unique subjects: {len(set(r['subject_id'] for r in records))}")
print(f"  Label distribution: {dict(sorted(dict(zip(*np.unique([r['canonical_label'] for r in records], return_counts=True))).items()))}")
print(f"  Download errors: {len(download_errors)}")
print(f"  Elapsed: {elapsed_total:.1f}s")

# %% [markdown]
# ## 2. Subject-level Train/Validation Split (Day 30 — Harmonization)
#
# Thực hiện chia dữ liệu theo subject (không theo record) để tránh data leakage.
# Sử dụng logic tương tự `day27_build_group_split.py`.

# %%
# === CELL 5: Build subject-level train/validation split ===
from sklearn.model_selection import StratifiedGroupKFold

all_subjects = sorted(set(r["subject_id"] for r in records))
all_labels = [r["canonical_label"] for r in records]
all_groups = [r["subject_id"] for r in records]

print(f"Total subjects: {len(all_subjects)}")
print(f"Total records: {len(records)}")

# Use StratifiedGroupKFold to create train/validation split
# 80% train, 20% validation (5-fold, take first fold)
if len(all_subjects) >= 5:
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=3001)
    dummy_X = np.zeros((len(records), 1))
    y = np.array(all_labels)
    groups = np.array(all_groups)

    for fold_idx, (train_idx, val_idx) in enumerate(splitter.split(dummy_X, y, groups)):
        if fold_idx == 0:
            train_subjects = set(groups[train_idx])
            val_subjects = set(groups[val_idx])
            break

    # Verify no leakage
    assert len(train_subjects & val_subjects) == 0, "LEAKAGE DETECTED!"
    print(f"Train subjects ({len(train_subjects)}): {sorted(train_subjects)}")
    print(f"Validation subjects ({len(val_subjects)}): {sorted(val_subjects)}")
else:
    # Fallback for very small datasets: use all as train
    train_subjects = set(all_subjects)
    val_subjects = set()
    print("⚠️ Too few subjects for proper split, using all as train")

# Update records with partition assignment
for record in records:
    if record["subject_id"] in val_subjects:
        record["partition"] = "validation"
        # Move signal file to validation directory
        old_path = Path(DATA_DIR) / record["signal_path"]
        new_path = Path(DATA_DIR) / "acquired" / "validation" / old_path.name
        new_path.parent.mkdir(parents=True, exist_ok=True)
        if old_path.exists():
            old_path.rename(new_path)
            record["signal_path"] = str(new_path.relative_to(Path(DATA_DIR)))
            # Recompute SHA-256 after move
            record["source_file_sha256"] = hashlib.sha256(new_path.read_bytes()).hexdigest()

# Save metadata-index.csv (same format as qa-validation/fixtures/day30/metadata-index.fixture.csv)
import csv

metadata_index_path = Path(DATA_DIR) / "metadata-index-mendeley-real.csv"
fieldnames = [
    "dataset_id", "record_id", "subject_id", "day_id", "session_id",
    "repetition_id", "canonical_label", "partition", "signal_path",
    "source_file_sha256", "split_version", "label_mapping_version",
    "sampling_rate_hz", "n_samples",
]
with metadata_index_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(records)

print(f"\n✅ Saved metadata-index: {metadata_index_path}")
print(f"   Train: {sum(1 for r in records if r['partition'] == 'train')} records")
print(f"   Validation: {sum(1 for r in records if r['partition'] == 'validation')} records")

# %% [markdown]
# ## 3. Build Window Index (Day 30 — Windowing)
#
# Tạo cửa sổ trượt (sliding windows) từ metadata-index.
# Sử dụng logic từ `ai-core/data/day30/windowing.py` → `build_window_rows()`.

# %%
# === CELL 6: Build window index ===
# Import windowing from repo (already in sys.path)
from day30.windowing import build_window_rows
from day30.storage_contract import validate_window_rows

WINDOW_MS = 200  # 200ms window (matches day30 config)
HOP_MS = 100     # 100ms hop (50% overlap)
CHANNEL_POLICY_ID = "mendeley-ch123-primary-v1"
PREPROCESSING_POLICY_ID = "per-record-channel-mean-v1"

window_rows = []
for record in records:
    try:
        rows = build_window_rows(
            record,
            WINDOW_MS,
            HOP_MS,
            CHANNEL_POLICY_ID,
            PREPROCESSING_POLICY_ID,
        )
        window_rows.extend(rows)
    except Exception as exc:
        print(f"  ⚠️ Windowing failed for {record['record_id']}: {exc}")

validation = validate_window_rows(window_rows)
print(f"\n{'='*60}")
print(f"  Window index: {len(window_rows)} windows")
print(f"  Validation: {'✅ PASS' if validation['pass'] else '❌ FAIL'}")
print(f"  Train windows: {sum(1 for w in window_rows if w['partition'] == 'train')}")
print(f"  Validation windows: {sum(1 for w in window_rows if w['partition'] == 'validation')}")

# Save window index JSON
window_index_path = Path(DATA_DIR) / "day30-window-index-mendeley-real.json"
window_index_path.write_text(
    json.dumps({"validation": validation, "rows": window_rows}, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)
print(f"  Saved: {window_index_path}")

# %% [markdown]
# ## 4. Feature Extraction (Day 31 — Feature Set 14)
#
# Trích xuất 14 đặc trưng từ mỗi cửa sổ × mỗi kênh EMG.
# Sử dụng logic từ `packages/semg-core/semg_core/day31_features/feature_set_14_v1.py`.
#
# **14 features:**
# - Time domain (8): RMS, MAV, Skewness, Kurtosis, Max, Min, STD, Mean
# - Spectral domain (6): Min/Max/STD Power, MDF, MNF, Spectral Entropy

# %%
# === CELL 7: Extract Feature Set 14 ===
from semg_core.day31_features import extract_feature_set_14, FEATURE_ORDER

print(f"Feature Set 14 ({len(FEATURE_ORDER)} features):")
for i, f_name in enumerate(FEATURE_ORDER):
    print(f"  [{i+1:2d}] {f_name}")

feature_rows = []
errors = []
total_windows = len(window_rows)

print(f"\nExtracting features from {total_windows} windows × {len(PRIMARY_CHANNELS)} channels...")
start_time = time.monotonic()

for w_idx, window in enumerate(window_rows):
    if (w_idx + 1) % 500 == 0 or w_idx == 0:
        elapsed = time.monotonic() - start_time
        rate = (w_idx + 1) / elapsed if elapsed > 0 else 0
        eta = (total_windows - w_idx - 1) / rate if rate > 0 else 0
        print(f"  [{w_idx+1}/{total_windows}] {rate:.1f} win/s, ETA {eta:.0f}s", flush=True)

    try:
        # Load signal from NPY file
        signal_path = Path(DATA_DIR) / window["signal_path"]
        if not signal_path.exists():
            errors.append({"window_id": window["window_id"], "error": f"File not found: {signal_path}"})
            continue

        full_signal = np.load(signal_path, allow_pickle=False)  # (N, 4)
        start = int(window["start_sample"])
        end = int(window["end_sample_exclusive"])
        window_signal = full_signal[start:end, :]  # (window_samples, 4)

        fs = float(window["sampling_rate_hz"])

        # Extract features for each primary channel (indices 0, 1, 2)
        for ch_idx, ch_id in enumerate(PRIMARY_CHANNELS):
            channel_signal = window_signal[:, ch_idx]

            # DC removal (per-record-channel-mean-v1 preprocessing policy)
            channel_signal = channel_signal - np.mean(channel_signal)

            result = extract_feature_set_14(channel_signal, fs)

            feature_row = {
                "dataset_id": window["dataset_id"],
                "dataset_view_id": "mendeley_core4_primary_v1",
                "split_name": window["partition"],
                "subject_id": window["subject_id"],
                "record_id": window["record_id"],
                "window_id": window["window_id"],
                "channel_id": ch_id,
                "canonical_label": window["canonical_label"],
                "sampling_rate_hz": fs,
                "window_ms": window["window_ms"],
                "hop_ms": window["hop_ms"],
                "preprocessing_policy_id": window["preprocessing_policy_id"],
                "channel_policy_id": window["channel_policy_id"],
                "qc_flags": result.qc_flags,
            }
            # Add all 14 features
            feature_row.update(result.features)
            feature_rows.append(feature_row)

    except Exception as exc:
        errors.append({"window_id": window.get("window_id", "?"), "error": str(exc)})

elapsed_total = time.monotonic() - start_time
print(f"\n{'='*60}")
print(f"  Feature rows extracted: {len(feature_rows)}")
print(f"  Errors: {len(errors)}")
print(f"  Elapsed: {elapsed_total:.1f}s")
if errors:
    print(f"  First 5 errors: {errors[:5]}")

# %% [markdown]
# ## 5. Pivot to Wide Matrix (Day 32 Input Format)
#
# Chuyển đổi từ long-format (1 row per window-channel) sang wide-format
# (1 row per window, features of all channels concatenated).
# Đây chính là format `.npz` mà `day32_run_core_baselines.py` cần.

# %%
# === CELL 8: Pivot to wide matrix ===
from collections import defaultdict

# Group feature rows by window_id
window_features = defaultdict(dict)
window_metadata = {}

for row in feature_rows:
    wid = row["window_id"]
    ch_id = row["channel_id"]
    if wid not in window_metadata:
        window_metadata[wid] = {
            "subject_id": row["subject_id"],
            "canonical_label": row["canonical_label"],
            "split_name": row["split_name"],
            "record_id": row["record_id"],
            "repetition_id": row.get("repetition_id", row["record_id"]),
            "dataset_id": row["dataset_id"],
        }
    for feat_name in FEATURE_ORDER:
        col_name = f"{ch_id}__{feat_name}"
        window_features[wid][col_name] = row[feat_name]

# Build aligned arrays
n_features_per_channel = len(FEATURE_ORDER)
n_channels = len(PRIMARY_CHANNELS)
n_features_total = n_features_per_channel * n_channels
feature_columns = []
for ch_id in PRIMARY_CHANNELS:
    for feat_name in FEATURE_ORDER:
        feature_columns.append(f"{ch_id}__{feat_name}")

print(f"Wide matrix dimensions: {len(window_features)} windows × {n_features_total} features")
print(f"Feature columns: {n_channels} channels × {n_features_per_channel} features = {n_features_total}")

X_list = []
y_list = []
groups_list = []
repetition_ids_list = []
dataset_ids_list = []
split_names_list = []
window_ids_ordered = []

for wid in sorted(window_features.keys()):
    if len(window_features[wid]) != n_features_total:
        continue  # Skip incomplete windows
    row_values = [window_features[wid].get(col, np.nan) for col in feature_columns]
    X_list.append(row_values)
    meta = window_metadata[wid]
    y_list.append(meta["canonical_label"])
    groups_list.append(meta["subject_id"])
    repetition_ids_list.append(meta.get("repetition_id", meta["record_id"]))
    dataset_ids_list.append(meta["dataset_id"])
    split_names_list.append(meta["split_name"])
    window_ids_ordered.append(wid)

X = np.array(X_list, dtype=np.float64)
y = np.array(y_list)
groups = np.array(groups_list)
repetition_ids = np.array(repetition_ids_list)
dataset_ids = np.array(dataset_ids_list)
split_names = np.array(split_names_list)

# Handle NaN: replace with 0 (features with QC flags)
nan_count = np.isnan(X).sum()
if nan_count > 0:
    print(f"⚠️ Found {nan_count} NaN values ({nan_count/X.size*100:.2f}%), replacing with 0")
    X = np.nan_to_num(X, nan=0.0)

print(f"\n{'='*60}")
print(f"  X shape: {X.shape}")
print(f"  y shape: {y.shape} — classes: {dict(zip(*np.unique(y, return_counts=True)))}")
print(f"  groups: {len(np.unique(groups))} unique subjects")
print(f"  Train windows: {(split_names == 'train').sum()}")
print(f"  Validation windows: {(split_names == 'validation').sum()}")

# %% [markdown]
# ## 6. Save Feature Matrix as `.npz`
#
# Format tương thích với `day32_generate_synthetic_matrix.py`:
# ```python
# np.savez_compressed(path, X=X, y=y, groups=groups,
#                     repetition_ids=reps, dataset_ids=dids)
# ```

# %%
# === CELL 9: Save NPZ matrix ===
output_path = Path(DATA_DIR) / "day31-features-mendeley-real.npz"

np.savez_compressed(
    output_path,
    X=X,
    y=y,
    groups=groups,
    repetition_ids=repetition_ids,
    dataset_ids=dataset_ids,
    split_names=split_names,
    feature_columns=np.array(feature_columns),
)

file_size_mb = output_path.stat().st_size / 1024 / 1024
npz_sha256 = hashlib.sha256(output_path.read_bytes()).hexdigest()

print(f"✅ Feature matrix saved: {output_path}")
print(f"   Size: {file_size_mb:.2f} MB")
print(f"   SHA-256: {npz_sha256}")
print(f"   X: {X.shape}, y: {y.shape}")
print(f"   Feature columns ({len(feature_columns)}): {feature_columns[:6]}...")

# Save evidence
evidence = {
    "schema_version": "day31-colab-etl-evidence.v1",
    "pipeline": "Day27_31_Colab_ETL_Pipeline",
    "dataset_id": "mendeley-4channel-hand-gesture-v2",
    "dataset_view_id": "mendeley_core4_primary_v1",
    "subjects_downloaded": len(set(r["subject_id"] for r in records)),
    "subjects_in_catalog": len(catalog),
    "total_records": len(records),
    "total_windows": len(window_rows),
    "feature_rows_extracted": len(feature_rows),
    "wide_matrix_rows": X.shape[0],
    "wide_matrix_features": X.shape[1],
    "nan_replaced_count": int(nan_count),
    "train_windows": int((split_names == "train").sum()),
    "validation_windows": int((split_names == "validation").sum()),
    "class_distribution": dict(zip(*[a.tolist() for a in np.unique(y, return_counts=True)])),
    "subject_distribution": dict(zip(*[a.tolist() for a in np.unique(groups, return_counts=True)])),
    "output_path": str(output_path),
    "output_sha256": npz_sha256,
    "output_size_mb": round(file_size_mb, 2),
    "feature_set_version": "feature-set-14.v1.0.0",
    "window_ms": WINDOW_MS,
    "hop_ms": HOP_MS,
    "sampling_rate_hz": int(records[0]["sampling_rate_hz"]) if records else None,
    "channel_policy_id": CHANNEL_POLICY_ID,
    "primary_channels": list(PRIMARY_CHANNELS),
    "training_allowed": False,
    "test_set_opened": False,
    "download_errors": download_errors,
}

evidence_path = Path(DATA_DIR) / "evidence" / "day31-colab-etl-evidence.json"
evidence_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"\n✅ Evidence saved: {evidence_path}")

# %% [markdown]
# ## 7. Download `.npz` to Local Machine
#
# **Trên Colab:** File sẽ tự động download về máy tính.
# **Trên Local:** File đã nằm tại `DATA_DIR`.
#
# Sau khi có file `.npz`, copy nó vào Zone 2 trên máy local:
# ```bash
# cp day31-features-mendeley-real.npz \
#    /home/duyvd9/massive/projects/semg-fatigue/myolab-ai-data/external/mendeley-4channel-hand-gesture-v2/derived/
# ```
# Rồi chạy Day 32 Baseline Modeling trên máy local.

# %%
# === CELL 10: Download to local (Colab only) ===
if IN_COLAB:
    from google.colab import files
    files.download(str(output_path))
    files.download(str(evidence_path))
    print("📥 Download triggered! Check your browser downloads folder.")
else:
    print(f"ℹ️ Running locally. Files are at:")
    print(f"   Matrix: {output_path}")
    print(f"   Evidence: {evidence_path}")

# %% [markdown]
# ## 📊 Summary
#
# | Item | Value |
# |------|-------|
# | Dataset | Mendeley 4-Channel Hand Gesture v2 |
# | Subjects | `len(all_subjects)` |
# | Core Labels | rest, hand_close, wrist_flexion, wrist_extension |
# | Windows | `len(window_rows)` |
# | Features | 14 features × 3 channels = 42 per window |
# | Matrix | X shape = `X.shape` |
# | File Size | `file_size_mb` MB |
#
# **Next Step:** Chạy `Day32_Baseline_Modeling.ipynb` hoặc
# `ai-core/pipelines/day32_run_core_baselines.py` trên file `.npz` này.
