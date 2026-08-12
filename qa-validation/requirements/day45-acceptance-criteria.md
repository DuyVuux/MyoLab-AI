# DAY45 Acceptance Criteria

- [ ] Mandatory three roadmap outputs exist.
- [ ] One processed artifact traces to exact SourceRecord identity, WindowIdentity, processing recipe fingerprint and code-component hashes.
- [ ] Processing step input/output hashes form a continuous chain.
- [ ] Mask hashes form a continuous chain and 1:1 sample alignment is preserved in the convergence evidence.
- [ ] Failed manifest contains no processed-looking artifact/output unit/processed Fs.
- [ ] Processing event IDs are deterministic for operation/type/sequence/correlation.
- [ ] Events contain no waveform, raw payload, source path, patient name, MRN or clinical free text.
- [ ] `PROCESSING_STARTED`, `PROCESSING_COMPLETED`, `PROCESSING_FAILED`, `REPROCESS_TRIGGERED` are defined.
- [ ] Persistent event store remains `NOT_IMPLEMENTED` / deferred to DAY53.
- [ ] No normalization fitting is performed; benchmark-locked fitting remains forbidden.
- [ ] DAY40–44 focused convergence regression passes.
- [ ] Highest claim remains `PROCESSING_PROVENANCE_READY`.
