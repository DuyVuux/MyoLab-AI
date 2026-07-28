# Fatigue Context Architecture — Day 26

```text
Gesture classifier
        +
QC/protocol/context features
        +
Fatigue-context engine
        ↓
confidence semantics / supportability
        ↓
continue with warning | abstain | recommend recalibration/remeasurement
```

The engine does not diagnose fatigue or recommend treatment. Electrode/contact drift, motion artifact, force variation and non-compliance are separate branches.
