# Public Benchmark Leakage Policy v1.0

## Freeze point
DAY66 is the anti-leakage freeze. The dataset versions, subject-wise partitions, adapter
versions, registered outputs, seed and locked-set prohibitions are fixed before DAY67.

## Unit of isolation
A subject is the minimum isolation unit. All sessions from a subject remain in the same split.
No window, trial or session from one subject may appear in both development and locked
partitions.

## Locked evaluation prohibitions
Locked data cannot be used to tune QC thresholds, select algorithms, fit normalization,
select features, train a model, or change split logic after seeing outcomes.

## If leakage occurs
The benchmark is invalidated. Do not hide the incident by regenerating a more favorable split.
Create a new protocol version, document the leakage event, regenerate partitions from a new
pre-registered seed, and re-run all dependent benchmark outputs.

## Public labels
Gesture/task labels are not QC artifact ground truth. QC accuracy/F1/sensitivity/specificity
are forbidden unless a valid reference truth exists for the relevant labels.
