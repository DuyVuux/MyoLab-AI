# Change Summary

UI-I1 establishes the integration seam only. Existing pages remain on their current data sources until UI-I2/UI-I3 migrations.

### Scientific safety encoded in runtime validators

- processed signal requires a processing manifest;
- sampling rate must be finite and positive;
- signal window must have positive duration;
- QC eligible fraction is limited to `[0,1]`;
- unavailable metric must be `null + reason`;
- payload shape mismatches fail closed;
- backend raw response text is not surfaced as UI error detail.

### Architecture decision

Candidate backend paths are not equivalent to verified live contracts. This package requires explicit endpoint verification before real-mode calls.
