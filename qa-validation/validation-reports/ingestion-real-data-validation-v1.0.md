# Ingestion Real-Data Validation v1.0 — DAY20

**Status:** `EVIDENCE_PENDING`  
**Raw patient data in this artifact:** prohibited  
**Purpose:** record structural/parser/integrity evidence for approved de-identified exports without copying raw values into repository.

## 1. Required validation set

Gate B needs at minimum:

1. one approved de-identified MR4 single CSV representative of supported P0 export;
2. one approved de-identified MR4 separated export including `info.csv` and representative `signal`/`signal_2d` files;
3. optional Vicon export only when an approved use case relies on Vicon context.

Synthetic fixtures remain mandatory regression evidence but cannot replace site/sample validation.

## 2. Evidence-capture rule

Repository evidence may contain:

```text
source evidence ID
approved data class
de-identification status
privacy approval reference
file basename or opaque reference
SHA-256
byte size
observed structural shape
parser version/config
result status/reason
property-suite result
reviewer/timestamp
```

Do not copy:

```text
patient name
MRN
DOB
free-text clinical note
raw time-series rows
video frames
absolute storage path if it exposes identifiers
```

## 3. Validation matrix

| Evidence item | Required Gate status | Current isolated-pack state | Promotion evidence |
|---|---|---|---|
| Privacy/de-id path | SITE_VERIFIED | NOT_VERIFIED | Site approval/reference |
| DAY19 live three-parser binding | LIVE_REPO_VERIFIED | NOT_VERIFIED | strict DAY19/DAY20 run log |
| Single CSV real/sample validation | SITE_VERIFIED | NOT_VERIFIED | approved export hash + parser report |
| Separated export real/sample validation | SITE_VERIFIED | NOT_VERIFIED | directory manifest + parser report + info layout review |
| Vicon minimal contract | VERIFIED_DOCUMENTED | VERIFIED_DOCUMENTED | DAY18 engineering evidence |
| Vicon site sync | optional / use-case dependent | NOT_VERIFIED | sync evidence only if needed |
| Property safety invariants | VERIFIED_DOCUMENTED + live regression | documented; live pending | DAY15-19 regression on current repo |
| Event/correlation minimum | VERIFIED_DOCUMENTED | VERIFIED_DOCUMENTED | DAY12/DAY19 contracts |
| DomainContext minimum | VERIFIED_DOCUMENTED | VERIFIED_DOCUMENTED | DAY12/DAY14 contracts |
| OOD model | NOT REQUIRED | NOT IMPLEMENTED | must not block Gate B |

## 4. Required commands after integration

```bash
cd /path/to/MyoLab-AI
DAY20_STRICT_UPSTREAM=1 bash scripts/dev/run_day20_checks.sh
```

Then validate approved exports using the **current live parser entry points**. Do not use a synthetic parser wrapper to promote site evidence.

For each source set, record only a privacy-safe evidence ledger. Compare source SHA before/after parser execution. Verify deterministic replay on same input/config. Verify invalid controlled copies fail closed in the approved test environment; do not fuzz patient data outside approved boundaries.

## 5. Single CSV review checklist

- exact structural layout matches supported profile;
- raw source hash unchanged;
- unknown fields preserved;
- missing values preserved;
- timestamp/count/unit rules behave as specified;
- canonical session does not contain direct identifiers;
- parser output stage is no stronger than `INGESTED`;
- exact replay deterministic.

## 6. Separated export review checklist

- `info.csv` physical framing explicitly reviewed;
- every signal retains its source reference/hash;
- `signal` and `signal_2d` shapes distinguished;
- mixed Fs accepted without resampling;
- orphan/unknown signal evidence preserved;
- unknown unit not inferred;
- directory retry produces consistent assembly identity/event behavior;
- no patient-derived identifier copied into evidence artifacts.

## 7. Vicon review checklist — optional

- only approved sections consumed;
- units/multi-row headers preserved;
- missing markers preserved;
- X/Y/Z not converted to anatomical planes without evidence;
- sync offset/drift/quality remain unknown unless measured/verified.

## 8. Result semantics

`PASS` here means parser/data-integrity behavior is supported for the validated source class. It does **not** mean QC validated, clinical interpretation validated, OOD capability validated, MFCV eligible, or MotionLab pilot ready.

## 9. Current conclusion

No approved de-identified real/sample exports or site privacy approval evidence were supplied to this isolated DAY20 builder. Therefore this report remains `EVIDENCE_PENDING`; it must not be used to promote Gate B by schedule.
