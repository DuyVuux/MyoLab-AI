# DAY15 Requirement → Artifact → Test Traceability

| Requirement | DAY15 interpretation | Primary artifact | Verification |
|---|---|---|---|
| FR-004 | mixed per-signal Fs is legal | `ingestion-invariants.v0.1.yaml` | property `HETEROGENEOUS_FS_ALLOWED` |
| FR-005 | duplicate/out-of-order/count mismatch surfaced | corruption factory | fixed + generated property cases |
| FR-006 | unknown unit never inferred | invariant YAML | `test_18_unknown_unit_guessing_is_detected` |
| FR-007 | missing raw remains missing | valid-edge fixture | missing-value preservation property |
| FR-008 | hashes preserve source identity evidence | factory manifest | hash-before/after tests |
| FR-023 | missing/unknown metadata is flagged, never guessed | invariant YAML | unknown-unit typed rejection |
| NFR-003 | raw immutable | invariant `RAW_IMMUTABLE` | mutating adapter detection |
| NFR-012 | fail closed on parser/data failure | `FAIL_CLOSED`, `NO_SILENT_CRASH` | false-success/exploding adapter detection |
| AC-01 | ingestion test corpus covers valid+invalid cases without raw loss | factory + fixtures | unit/property suites |
| AC-02 | unit/Fs/provenance explicit or flagged | fixture truth + invariants | unit/mixed-Fs tests |

## State contribution

- Factory: `IMPLEMENTED`
- Fixture truth: `IMPLEMENTED/REVALIDATED` on synthetic evidence
- Property invariant contract: `DESIGNED/IMPLEMENTED`
- Production parser binding: `NOT_YET_APPLICABLE_UNTIL_DAY16_DAY17`
- Site validation: `NOT_VERIFIED`
- Clinical validation: `NOT_VALIDATED`
