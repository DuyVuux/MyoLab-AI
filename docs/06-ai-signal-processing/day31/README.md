# Day 31 — Controlled 14-feature sEMG engineering

## Delivery status

Day 31 implements a deterministic, source-specific feature-engineering
pipeline. It does not train, fit, tune, pool datasets, or read a sealed test
partition.

The reference implementation lives in:

```text
packages/semg-core/semg_core/day31_features/
```

It is intentionally separate from the stable Day 8
`semg_core.features` module to preserve backward compatibility.

## Locked contract

The canonical contract is
`ai-core/configs/day31_feature_contract.v1.yaml`. It defines exactly 14
features in fixed order:

```text
rms
mav
skewness_unbiased
kurtosis_fisher_unbiased
max_signed
min_signed
std_sample_ddof1
mean
spectral_min_power
spectral_max_power
spectral_std_power_ddof1
mdf_hz
mnf_hz
spectral_entropy_bits
```

Spectral power is the versioned proxy `abs(rfft(x))²/N`, over all finite bins
from DC through Nyquist, without one-sided interior-bin doubling. It is not
reported as a physical PSD in power/Hz.

## Safety boundary

The pipeline uses an exact allowlist of `train` and `validation`. Every input
window is validated before the first source read, so a later forbidden row
cannot cause partial batch access. Path components containing `test`,
`sealed-test`, `sealed_test`, `outer-test`, or `outer_test` are rejected.

Canonical source files must:

- resolve inside the configured `SEMG_DATA_ROOT`;
- match the SHA-256 stored in the Day 30 window index;
- use CSV, NPY, or NPZ canonical representation;
- provide explicit channel identifiers for binary formats;
- contain finite `[samples, channels]` data.

The implementation does not guess anatomical channel mappings.

## Numerical behavior

- Non-finite input fails closed by default.
- Constant and under-sized windows retain explicit NaN values internally and
  emit registered QC flags.
- JSON evidence represents missing numeric values as `null`; it never writes
  the non-standard `NaN` token.
- Amplitude calculations and spectral extraction use scale-safe paths.
- A finite input that exceeds float64 spectral-power range retains
  representable features, writes affected features as missing, and emits
  `numeric_overflow` plus `feature_nonfinite`.

## Dataset views

| View | Included channels | ALL14 dimension |
|---|---:|---:|
| `mendeley_core4_primary_v1` | CH1–CH3 | 42 |
| `mendeley_core4_ch4_sensitivity_v1` | CH1–CH4 | 56 |
| `grabmyo_project_subset_native28_v1` | F1–F16, W1–W12 | 392 |
| `cross_source_intersection_summary_v1` | five channel statistics | 70 |

CH4 remains sensitivity-only. U1–U4 remain excluded from GRABMyo primary.

## Running the gate

```bash
bash scripts/dev/run_day31_checks.sh
```

The orchestrator runs:

1. Day 30 regression and artifact checks;
2. bytecode compilation and Ruff;
3. preflight, registry, and contract validation;
4. golden source-view smoke extraction;
5. quality and Pearson/Spearman redundancy audit;
6. deterministic adversarial stress testing;
7. Day 31 pytest with at least 80% scoped coverage;
8. manifest and readiness-decision generation;
9. schema, safety-flag, raw-artifact, and prohibited-training-call audit.

## Zone 2 extraction

```bash
python scripts/data/day31_extract_features.py \
  --window-index /path/to/day30-window-index.json \
  --dataset-view mendeley_core4_primary_v1 \
  --data-root "$SEMG_DATA_ROOT" \
  --output "$SEMG_DATA_ROOT/derived/features/day31/mendeley.csv.gz" \
  --evidence-output qa-validation/evidence/day31/mendeley-extraction.json
```

For NPY/NPZ sources, pass `--channel-map` containing a JSON object from
`record_id` to an ordered channel-ID list.

## Gate interpretation

Portable validation can authorize only
`GO_FOR_DAY32_SEPARATE_BASELINE_SMOKE`. `GO full` additionally requires real
train/validation materialization, a resolved dependency lock, and an explicit
Day 32 training authorization. Absence of `SEMG_DATA_ROOT` must never be
reported as successful real-data extraction.
