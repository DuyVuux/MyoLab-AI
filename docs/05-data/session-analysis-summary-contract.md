# Session Analysis Summary Contract v0.1

## Mục đích

Tạo payload ổn định cho frontend/report mà không expose toàn bộ stage internals.

## Field groups

- Identity/status.
- Signal quality và MFCV capability.
- Trend summaries theo channel.
- Evidence/rule conclusion.
- Engineering confidence.
- Explainability.
- Provenance.
- Safety/limitations/links.

## Null behavior

Khi `status=abstained`:

```text
technical_conclusion = abstained
confidence.final_score_0_to_1 = null
confidence.category = not_available
channels có thể rỗng
```

## Unit

- RMS/MAV slope: `uV/min`.
- MDF/MNF slope: `Hz/min`.
- Percent change: `%`.
- Confidence: unitless `[0,1]`, không phải probability.

## Prohibited content

- raw/processed sample arrays;
- PSD vectors;
- patient direct identifiers;
- diagnosis/treatment/return-to-play decision;
- FRS hoặc probability chưa được validation.
