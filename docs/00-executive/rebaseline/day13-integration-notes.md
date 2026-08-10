# DAY13 Integration Notes

DAY13 adds a deterministic integrity validation layer and intentionally does not overwrite upstream shared README or DAY12 canonical contracts.

Safety boundaries:
- no MR4 production parser (DAY16/DAY17);
- no vendor-to-canonical channel inference (DAY14);
- no signal-quality detector (DAY21+);
- no raw mutation, sorting, interpolation, resampling or silent unit coercion;
- no OOD score, SSL training or Process-Mining capability; DAY13 is `GIỮ NGUYÊN` in the Technology Augmentation Plan;
- missing metadata remains explicit and mixed sampling rates are validated per signal.
