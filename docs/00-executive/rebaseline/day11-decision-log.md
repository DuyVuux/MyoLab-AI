# DAY11 Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| D11-01 | Source identity is content-addressed SHA-256 | filename/path are unstable and may contain PHI | ACCEPTED_DESIGN |
| D11-02 | Duplicate exact bytes do not append/overwrite SourceRecord | preserves first-seen provenance and idempotence | ACCEPTED_DESIGN |
| D11-03 | Different bytes with same filename are distinct sources | prevents silent replacement | ACCEPTED_DESIGN |
| D11-04 | Ledger implementation is append-only JSONL, single writer for DAY11 | smallest deterministic implementation; concurrency hardening not silently invented | ACCEPTED_WITH_LIMITATION |
| D11-05 | Rich DomainContext is not added today | belongs to DAY12/DAY14; avoid scope creep | ACCEPTED_DESIGN |
| D11-06 | Unknown research reuse permission is denial-by-default | governance uncertainty cannot become training authorization | ACCEPTED_DESIGN |
| D11-07 | DAY10 physical info.csv framing limitation is carried, not silently closed | DAY11 hashes bytes independent of parser framing | CARRIED_LIMITATION |
