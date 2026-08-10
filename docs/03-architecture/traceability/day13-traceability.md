# DAY13 Requirement Traceability

| Requirement | Source | DAY13 behavior | Artifact | Test/evidence | State |
|---|---|---|---|---|---|
| FR-004 | SRS | Validate each signal's Fs independently; never assume common rate | `time_count_unit.py` | tests 13–18 | IMPLEMENTED + VALIDATED on synthetic fixtures |
| FR-005 | SRS | Strict monotonic time; metadata count and begin_time checks when available | `time_count_unit.py` | tests 4–12 | IMPLEMENTED + VALIDATED on synthetic fixtures |
| FR-006 | SRS | Preserve V/uV distinction; conversions only via versioned registry + provenance | `unit-registry.v0.1.yaml` + module | tests 19–28 | IMPLEMENTED + VALIDATED on synthetic fixtures |
| FR-023 | SRS | Missing metadata is explicit NOT_EVALUATED; no inferred/default value | module | tests 9,12,17,22 | IMPLEMENTED; completeness severity remains DAY14 policy |
| AC-02 | SRS acceptance | Invalid timestamp/count/unit cases produce typed failure, no silent coercion | tests + corrupted fixtures | tests 5,6,8,11,14,16,21,34,39 | VALIDATED on synthetic fixtures |

## Evidence boundary
No site clinical threshold is frozen here. No claim is made that all future vendor units are covered. Unknown units and absent metadata fail/surface explicitly until later policy/evidence resolves them.
