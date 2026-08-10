# DAY14 Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| D14-01 | Vendor mapping v0.1 uses exact approved aliases only | Prevent silent anatomy/laterality inference | ACCEPTED |
| D14-02 | Unknown/ambiguous mapping returns UNMAPPED/UNKNOWN | Preserve evidence and fail safely | ACCEPTED |
| D14-03 | Metadata completeness is profile-specific | Basic ingestion/QC and protocol metrics need different context | ACCEPTED |
| D14-04 | OOD readiness at DAY14 is metadata-contract only | No reference distribution/model/threshold is validated yet | ACCEPTED |
| D14-05 | `layout_id` is explicit, never synthesized | A guessed layout would corrupt future shift analysis | ACCEPTED |
| D14-06 | Missing DAY11 retention policy is backfilled unchanged from the original DAY11 handoff | Repair a known integration omission without redefining DAY14 scope | ACCEPTED |
| D14-07 | SSL remains research/data-readiness only | Technology Plan defers representation learning; no training authorization | ACCEPTED |
| D14-08 | OOD is not QC and not pathology | Different questions and evidence semantics | ACCEPTED |
