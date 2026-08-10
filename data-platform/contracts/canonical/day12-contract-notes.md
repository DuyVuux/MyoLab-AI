# DAY12 Canonical Contract Notes

## Purpose

DAY12 defines the boundary between vendor/source metadata and canonical MotionLab analysis objects. It does **not** parse MR4 files, validate time/count/unit numerically (DAY13), map vendor signal names to canonical muscle/channel ontology (DAY14), or emit Clinical Event Store events (DAY19/DAY53).

## Core invariants

1. `session_id`, `subject_analysis_id`, `signal_id`, `case_id`, and `correlation_id` are opaque identifiers; they do not embed patient name, MRN, birth date, record name, task name, or diagnosis.
2. Every canonical signal references a DAY11 `SourceRecord` using `src_sha256_<digest>`.
3. `record_name` is not copied into the broadly consumed Session object. The canonical Session stores a restricted `record_name_ref` pointing back to source metadata.
4. Source/vendor text is preserved exactly when represented. Runtime models intentionally do **not** strip whitespace from source text.
5. `UNKNOWN` means no value is available and therefore cannot carry an invented value.
6. `VERIFIED` requires explicit evidence references.
7. `SOURCE_REPORTED` preserves a source-reported value but does not elevate it to site-verified truth.
8. `canonical_channel_ref` is an interface for DAY14. DAY12 never infers muscle/side/channel from a vendor string such as `LT_BICEPS`.
9. `DomainContext` is descriptive metadata only. It does not produce an OOD score, clinical confidence, or generalization guarantee.
10. `ProcessCorrelation` is identity/correlation only. Raw payloads are forbidden; event type/state semantics belong to later days.

## Evidence status semantics

| State | Meaning | Can carry value? | Minimum evidence |
|---|---|---:|---|
| VERIFIED | Confirmed by an approved evidence source | yes | >=1 evidence ref |
| SOURCE_REPORTED | Present in source/vendor metadata | yes | source ref recommended |
| UNKNOWN | No value known | no | none |
| NOT_VERIFIED | Candidate/value may exist but is not verified | yes or null | explicit status |
| DISCOVERY_REQUIRED | Requires dedicated discovery before use | usually null | open question/decision ref |

## Why source strings are not stripped

DAY11's runtime immutability upgrade uses strict validation. DAY12 refines this rule: canonical values may be normalized only by an explicit versioned rule, but *source-reported text* is evidence and must not be silently transformed by global whitespace stripping. A source value like `"  LT_BICEPS  "` is therefore preserved exactly until a later mapping/normalization rule acts on it with provenance.

## DAY13 handoff

DAY13 receives:
- evidence-bearing sampling rates and units;
- source-linked measurement time;
- Session/Signal identities;
- unknown states that must remain explicit.

DAY13 may validate numeric/time/unit consistency. It must not retroactively infer clinical semantics from vendor names.
