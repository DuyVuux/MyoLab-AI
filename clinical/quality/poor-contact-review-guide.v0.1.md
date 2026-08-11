# Poor Contact / Unexpected Channel Review Guide v0.1

## Safety position
A detector can flag **suspected** poor contact; it cannot diagnose electrode detachment or pathology. **Low activation is not a bad electrode**. Stroke, paresis, selective weakness, task-specific recruitment and post-operative states can legitimately produce low activation.

## Review sequence
1. Confirm exact session/channel/window and raw provenance.
2. Review dropout/flatline/high-baseline/power-line/spectral evidence.
3. Compare adjacent channels only when montage/context makes comparison supportable.
4. Check protocol/task: was activation expected?
5. If acquisition and physiological explanations remain plausible, keep `UNKNOWN/REVIEW_REQUIRED`.
6. Never auto-repair, interpolate, zero, replace, or transform the raw channel.

## Evidence hierarchy
Low amplitude alone = insufficient. Corroborated low-relative amplitude + acquisition artifact evidence = `POOR_CONTACT_SUSPECTED`, still not causal proof. Clinician/operator observation or impedance/contact evidence can raise evidence tier later, but this DAY28 rule does not manufacture it.
