# %% [markdown]
# # 🤖 MyoLab-AI — Day 32 Baseline Modeling (Real Data)
#
# **Mục tiêu:** Chạy 6 core baseline models + 4 optional models trên
# feature matrix thật từ Mendeley, sử dụng StratifiedGroupKFold (cross-subject).
#
# **Input:** File `.npz` từ `Day27_31_Colab_ETL_Pipeline`
# **Output:** Metrics JSON (F1, Balanced Accuracy, Confusion Matrix)
#
# **Logic tái sử dụng từ repo:**
# - `ai-core/modeling/day32/model_factory.py` → `build_core_models()`, `build_optional_models()`
# - `ai-core/modeling/day32/grouped_cv.py` → `make_grouped_folds()`
# - `ai-core/modeling/day32/core_gate.py` → `decide_core_gate()`
# - `ai-core/modeling/day32/aggregation.py` → `aggregate_window_labels()`

# %% [markdown]
# ## 0. Setup

# %%
import sys
import os
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timezone

import numpy as np

# Detect environment
try:
    import google.colab
    IN_COLAB = True
    REPO_DIR = "/content/MyoLab-AI"
except ImportError:
    IN_COLAB = False
    REPO_DIR = str(Path(__file__).resolve().parents[1]) if "__file__" in dir() else "."

# Add repo to path
sys.path.insert(0, os.path.join(REPO_DIR, "ai-core", "modeling"))
sys.path.insert(0, os.path.join(REPO_DIR, "packages", "semg-core"))

print(f"Running in Colab: {IN_COLAB}")
print(f"REPO_DIR: {REPO_DIR}")

# %% [markdown]
# ## 1. Load Feature Matrix

# %%
# === CONFIG: Edit this path to your .npz file ===
NPZ_PATH = os.environ.get(
    "DAY31_MATRIX",
    # Default paths to check
    None,
)

# Auto-detect .npz file
search_paths = [
    Path(REPO_DIR) / "data_temp" / "day31-features-mendeley-real.npz",
    Path("/content/data/day31-features-mendeley-real.npz"),
    Path(REPO_DIR).parent / "myolab-ai-data" / "external" / "mendeley-4channel-hand-gesture-v2" / "derived" / "day31-features-mendeley-real.npz",
]

if NPZ_PATH:
    matrix_path = Path(NPZ_PATH)
else:
    matrix_path = None
    for p in search_paths:
        if p.exists():
            matrix_path = p
            break

if matrix_path is None or not matrix_path.exists():
    if IN_COLAB:
        from google.colab import files
        print("📤 Please upload your day31-features-mendeley-real.npz file:")
        uploaded = files.upload()
        matrix_path = Path(list(uploaded.keys())[0])
    else:
        raise FileNotFoundError(
            "Feature matrix not found. Set DAY31_MATRIX env var or place file in one of:\n"
            + "\n".join(f"  - {p}" for p in search_paths)
        )

print(f"Loading: {matrix_path}")
data = np.load(matrix_path, allow_pickle=False)

X = data["X"]
y = data["y"]
groups = data["groups"]

# Optional arrays
repetition_ids = data.get("repetition_ids", np.array([f"r{i}" for i in range(len(y))]))
dataset_ids = data.get("dataset_ids", np.full(len(y), "mendeley-4channel-hand-gesture-v2"))
split_names = data.get("split_names", None)
feature_columns = data.get("feature_columns", None)

print(f"X: {X.shape}")
print(f"y: {y.shape} → {dict(zip(*np.unique(y, return_counts=True)))}")
print(f"groups: {len(np.unique(groups))} unique subjects")
if feature_columns is not None:
    print(f"Features: {len(feature_columns)} columns")
    print(f"  First 6: {list(feature_columns[:6])}")

# %% [markdown]
# ## 2. Build Grouped Folds
#
# StratifiedGroupKFold từ `ai-core/modeling/day32/grouped_cv.py`

# %%
from day32.grouped_cv import make_grouped_folds

N_SPLITS = 5
SEED = 3201

folds = make_grouped_folds(y, groups, N_SPLITS, seed=SEED)

print(f"Created {len(folds)} folds (StratifiedGroupKFold, seed={SEED})")
for fold in folds:
    train_groups = set(fold["train_groups"])
    val_groups = set(fold["validation_groups"])
    overlap = train_groups & val_groups
    print(f"  Fold {fold['fold_id']}: train={len(fold['train_indices'])} "
          f"(groups={len(train_groups)}), val={len(fold['validation_indices'])} "
          f"(groups={len(val_groups)}), leakage={'❌' if overlap else '✅ None'}")

# %% [markdown]
# ## 3. Run Core Baselines (6 Models)
#
# Models từ `ai-core/modeling/day32/model_factory.py`:
# 1. dummy_majority
# 2. dummy_stratified
# 3. lda_shrinkage
# 4. logistic_regression
# 5. linear_svm
# 6. random_forest

# %%
from day32.model_factory import build_core_models, build_optional_models, CORE_MODEL_IDS
from sklearn.metrics import (
    balanced_accuracy_score, f1_score,
    classification_report, confusion_matrix,
)

CLASS_ORDER = ["rest", "hand_close", "wrist_flexion", "wrist_extension"]

def run_model_all_folds(model_id, model_factory_fn, X, y, folds, class_order):
    """Run one model across all folds and aggregate metrics."""
    fold_results = []
    all_y_true = []
    all_y_pred = []

    for fold in folds:
        train_idx = np.array(fold["train_indices"])
        val_idx = np.array(fold["validation_indices"])

        model = model_factory_fn()[model_id]
        started = time.perf_counter()
        try:
            model.fit(X[train_idx], y[train_idx])
            pred = model.predict(X[val_idx])
            elapsed = time.perf_counter() - started

            macro_f1 = float(f1_score(y[val_idx], pred, average="macro", zero_division=0))
            bal_acc = float(balanced_accuracy_score(y[val_idx], pred))

            fold_results.append({
                "fold_id": fold["fold_id"],
                "status": "COMPLETED",
                "macro_f1": macro_f1,
                "balanced_accuracy": bal_acc,
                "fit_and_predict_seconds": elapsed,
            })
            all_y_true.extend(y[val_idx].tolist())
            all_y_pred.extend(pred.tolist())

        except Exception as exc:
            elapsed = time.perf_counter() - started
            fold_results.append({
                "fold_id": fold["fold_id"],
                "status": "FAILED",
                "failure_reason": f"{type(exc).__name__}:{exc}",
                "fit_and_predict_seconds": elapsed,
            })

    # Aggregate across folds
    completed = [r for r in fold_results if r["status"] == "COMPLETED"]
    if completed:
        mean_f1 = np.mean([r["macro_f1"] for r in completed])
        std_f1 = np.std([r["macro_f1"] for r in completed])
        mean_acc = np.mean([r["balanced_accuracy"] for r in completed])
        std_acc = np.std([r["balanced_accuracy"] for r in completed])
    else:
        mean_f1 = std_f1 = mean_acc = std_acc = 0.0

    return {
        "model_id": model_id,
        "n_folds": len(folds),
        "completed_folds": len(completed),
        "mean_macro_f1": float(mean_f1),
        "std_macro_f1": float(std_f1),
        "mean_balanced_accuracy": float(mean_acc),
        "std_balanced_accuracy": float(std_acc),
        "fold_results": fold_results,
        "aggregated_confusion_matrix": confusion_matrix(
            all_y_true, all_y_pred, labels=class_order
        ).tolist() if all_y_true else None,
        "aggregated_classification_report": classification_report(
            all_y_true, all_y_pred, labels=class_order,
            target_names=class_order, output_dict=True, zero_division=0,
        ) if all_y_true else None,
    }


# Run all core models
print("=" * 70)
print("  CORE BASELINES (6 models × 5 folds = 30 runs)")
print("=" * 70)

core_results = []
for model_id in CORE_MODEL_IDS:
    print(f"\n  🔹 {model_id}...", end=" ", flush=True)
    result = run_model_all_folds(model_id, build_core_models, X, y, folds, CLASS_ORDER)
    core_results.append(result)
    print(f"F1={result['mean_macro_f1']:.4f}±{result['std_macro_f1']:.4f}, "
          f"BA={result['mean_balanced_accuracy']:.4f}±{result['std_balanced_accuracy']:.4f}")

# %% [markdown]
# ## 4. Core Gate Check

# %%
from day32.core_gate import decide_core_gate

# Use first-fold results for gate check (matches original pipeline)
first_fold_results = []
for result in core_results:
    fold_0 = next((r for r in result["fold_results"] if r["fold_id"] == 0), None)
    if fold_0:
        first_fold_results.append({
            "model_id": result["model_id"],
            **fold_0,
        })

gate = decide_core_gate(first_fold_results)
print(f"\nCore Gate: {gate['status']}")
print(f"  Missing models: {gate['missing_models']}")
print(f"  Failed models: {gate['failed_models']}")
print(f"  Optional models may run: {gate['optional_models_may_run']}")

# %% [markdown]
# ## 5. Run Optional Models (if gate passes)

# %%
optional_results = []
if gate["optional_models_may_run"]:
    from day32.model_factory import OPTIONAL_MODEL_IDS

    print("=" * 70)
    print("  OPTIONAL MODELS (4 models × 5 folds = 20 runs)")
    print("=" * 70)

    for model_id in OPTIONAL_MODEL_IDS:
        print(f"\n  🔸 {model_id}...", end=" ", flush=True)
        result = run_model_all_folds(model_id, build_optional_models, X, y, folds, CLASS_ORDER)
        optional_results.append(result)
        print(f"F1={result['mean_macro_f1']:.4f}±{result['std_macro_f1']:.4f}, "
              f"BA={result['mean_balanced_accuracy']:.4f}±{result['std_balanced_accuracy']:.4f}")
else:
    print("⚠️ Core gate did not pass. Optional models skipped.")

# %% [markdown]
# ## 6. Results Summary & Leaderboard

# %%
all_results = core_results + optional_results

# Sort by mean_macro_f1 descending
leaderboard = sorted(all_results, key=lambda r: r["mean_macro_f1"], reverse=True)

print("\n" + "=" * 70)
print("  📊 DAY 32 BASELINE LEADERBOARD (Mendeley Real Data)")
print("=" * 70)
print(f"  {'Rank':<6} {'Model':<25} {'Macro-F1':<18} {'Balanced Acc':<18} {'Folds'}")
print("-" * 70)
for rank, result in enumerate(leaderboard, 1):
    tier = "⭐" if result["model_id"] in CORE_MODEL_IDS else "🔸"
    print(f"  {rank:<6} {tier} {result['model_id']:<22} "
          f"{result['mean_macro_f1']:.4f}±{result['std_macro_f1']:.4f}  "
          f"{result['mean_balanced_accuracy']:.4f}±{result['std_balanced_accuracy']:.4f}  "
          f"{result['completed_folds']}/{result['n_folds']}")

# Best non-dummy model
non_dummy = [r for r in leaderboard if "dummy" not in r["model_id"]]
if non_dummy:
    best = non_dummy[0]
    print(f"\n  🏆 Best: {best['model_id']} (F1={best['mean_macro_f1']:.4f})")

# %% [markdown]
# ## 7. Save Evidence JSON

# %%
evidence = {
    "schema_version": "day32-real-baseline-evidence.v1",
    "scope": "MENDELEY_REAL_DATA",
    "dataset_id": "mendeley-4channel-hand-gesture-v2",
    "dataset_view_id": "mendeley_core4_primary_v1",
    "matrix_path": str(matrix_path),
    "matrix_sha256": hashlib.sha256(matrix_path.read_bytes()).hexdigest(),
    "matrix_shape": list(X.shape),
    "n_subjects": int(len(np.unique(groups))),
    "n_classes": int(len(np.unique(y))),
    "class_order": CLASS_ORDER,
    "class_distribution": dict(zip(*[a.tolist() for a in np.unique(y, return_counts=True)])),
    "cv_strategy": "StratifiedGroupKFold",
    "n_splits": N_SPLITS,
    "seed": SEED,
    "core_gate": gate,
    "leaderboard": [
        {
            "model_id": r["model_id"],
            "mean_macro_f1": r["mean_macro_f1"],
            "std_macro_f1": r["std_macro_f1"],
            "mean_balanced_accuracy": r["mean_balanced_accuracy"],
            "std_balanced_accuracy": r["std_balanced_accuracy"],
            "completed_folds": r["completed_folds"],
        }
        for r in leaderboard
    ],
    "core_results": core_results,
    "optional_results": optional_results,
    "sealed_test_rows_read": 0,
    "pooled_training_executed": False,
    "created_at": datetime.now(timezone.utc).isoformat(),
}

evidence_path = Path(REPO_DIR) / "qa-validation" / "evidence" / "day32" / "day32-real-baseline-evidence.json"
evidence_path.parent.mkdir(parents=True, exist_ok=True)
evidence_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
print(f"✅ Evidence saved: {evidence_path}")

# Also save a copy next to the matrix
if matrix_path.parent != evidence_path.parent:
    alt_evidence = matrix_path.parent / "day32-real-baseline-evidence.json"
    alt_evidence.write_text(json.dumps(evidence, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    print(f"✅ Copy saved: {alt_evidence}")

print("\n🎉 Day 32 Real Data Baseline — COMPLETE")
