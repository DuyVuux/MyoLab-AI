# DAY10 Golden Contract Fixtures — Separated CSV

Fixtures are logical synthetic representations because the available architecture document does not fully specify `info.csv` physical row framing. They test field/shape/per-signal metadata contracts without containing patient data.

- `synthetic-info-logical.yaml`: PHI-bearing field surfaces represented with synthetic values.
- `synthetic-emg-signal.yaml`: `signal` shape `time,value`, 2000 Hz example.
- `synthetic-cop-signal2d.yaml`: `signal_2d` shape `time,x,y`, 100 Hz example.
- `invalid-signal2d-wrong-shape.yaml`: negative shape fixture.

Before DAY11 promotion, run the approved real-layout audit helper against the integrated repository/sample location. The helper must not log PHI values.
