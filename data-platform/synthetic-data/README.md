# Synthetic Data — Engineering Fixtures Only

## Day 3 fixture

```text
golden_signal_01.csv
golden_signal_01.manifest.json
golden_signal_01.generation.json
golden_signal_01.expected_ingestion_summary.json
```

Shape at 1000 Hz:

- baseline rest: 5 seconds = 5,000 samples;
- active contraction: 60 seconds = 60,000 samples;
- recovery: 5 seconds = 5,000 samples;
- total: 70 seconds = 70,000 samples.

The timestamp sequence uses:

```text
t[n] = n / Fs, n = 0, ..., N - 1
```

Therefore the last stored timestamp is `69.999 s`, while the half-open record span is `[0, 70.000 s)`.

## Regeneration

```bash
python data-platform/synthetic-data/generate_synthetic_semg.py \
  --output-dir data-platform/synthetic-data \
  --overwrite
```

The seed is fixed by default, so the CSV bytes and SHA-256 should be deterministic under the same Python/NumPy/text-formatting behavior.

## Prohibited claims

Do not use the fixture to claim:

- clinical validity;
- classifier accuracy;
- validated fatigue thresholds;
- real sensor noise characteristics;
- MFCV eligibility;
- patient outcome.
