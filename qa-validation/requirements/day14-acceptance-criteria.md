# DAY14 Acceptance Criteria

1. `clinical/ontologies/muscle-channel-ontology.v0.1.yaml` exists and is versioned.
2. `configs/validation/metadata-policy.v0.1.yaml` defines profile-specific optional/warning/fail behavior.
3. `channel_mapper.py` performs deterministic exact mapping and never fuzzy-guesses anatomy/laterality.
4. Unknown aliases preserve raw vendor text and return `UNMAPPED + UNKNOWN`.
5. `channel-layout-context.v0.1.yaml` exists and is explicitly OOD metadata-contract readiness only.
6. Unknown geometry/placement remains `UNKNOWN/NOT_VERIFIED`.
7. `layout_id` is not synthesized.
8. No OOD score/model/reference distribution/shift threshold is introduced.
9. Missing DAY11 `unlabeled-corpus-retention-policy.v0.1.md` is backfilled and remains data-readiness only.
10. No SSL/model training, no raw patient data, no parser DAY16/17 implementation.
11. DAY14 tests pass and available DAY09–DAY13 regression tests pass on the live repository.
12. Human review verifies site alias coverage limitations and confirms no silent clinical/anatomical inference.

## Status rule
- `GO_FOR_DAY_15`: all engineering criteria pass; upstream backfill present; unresolved site mapping/layout facts are explicit and non-blocking for corrupted-fixture work.
- `READY_WITH_LIMITATIONS`: engineering pass but live regression/human review or site coverage confirmation is pending without breaking DAY15 safety.
- `BLOCKED_WITH_EVIDENCE`: mapping logic silently guesses, required governance path missing, or verified geometry/site claims lack evidence.
