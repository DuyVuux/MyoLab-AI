# MR4 Single-CSV Contract Examples v0.1

## Purpose
Tài liệu này minh họa contract DAY09. Mọi CSV bên dưới là **synthetic contract fixture**, không phải dữ liệu bệnh nhân và không phải bằng chứng SITE_VERIFIED.

## Observed anatomy represented
1. Row 1 metadata header.
2. Row 2 metadata values.
3. Row 3 blank separator.
4. Row 4 data header.
5. Row 5+ time-series rows.

## Example A — valid minimal
```csv
type,begin_time,frequency,count,created with version,exported with version,measurement_date,record_name
record,0.00000,2000,3,Noraxon MR 4.0.22,4.0.22,2025-08-26T17:29:12.325+07:00,SYNTHETIC_TREADMILL_EMG

time,Activity,Marker,Pressure Platform-Velocity,LT Force,RT Force,LT BICEPS FEM.,RT BICEPS FEM.
0.00000,REST,,1.20,510.0,508.0,12.5,11.7
0.00050,,,1.20,512.0,509.0,13.1,12.2
0.00100,,M1,1.20,515.0,511.0,12.8,12.0
```

### Correct interpretation
- `frequency=2000` is record/table-level metadata observed for this single-CSV family. It must not create a global assumption that every signal in a separated export shares 2000 Hz.
- `LT Force` and `RT Force` retain vendor naming. Exact physical semantics beyond documented pressure/treadmill context remain NOT_VERIFIED.
- Unknown metadata/columns must be preserved.

## Example B — valid with unknown fields
A new metadata key `future_vendor_field` and data column `FutureSensor-A` are legal contract-evolution evidence. DAY09 must preserve them rather than reject merely because semantics are unknown.

## Example C — invalid anatomy
If row 3 is not blank, the file does not match the observed DAY09 golden anatomy. DAY09 validator rejects the fixture as contract mismatch. Future evidence may version the contract rather than silently relaxing v0.1.

## What DAY09 deliberately does not validate
- physiological plausibility;
- monotonic time as a production validation engine;
- count-vs-row enforcement as production logic;
- signal quality;
- clinical meaning;
- canonical muscle ontology;
- parser performance.

Those belong to later days according to the 90-Day roadmap.
