# DAY17 synthetic separated-export fixtures

All fixtures are synthetic engineering data. The physical layout is intentionally tied to `MR4_SEPARATED_SYNTHETIC_HORIZONTAL_V0_1` and is **not site-verified**.

- `base_record`: signal 2000 Hz + signal_2d 100 Hz.
- `unknown_type_record`: preserves unsupported signal type as evidence.
- `orphan_record`: missing vendor signal name is preserved and warned.
- `unknown_unit_record`: fails `UNIT_MISMATCH`; no unit inference.
- `bad_shape_record`: fails signal_2d shape contract.
- `count_mismatch_record`: fails count contract.
