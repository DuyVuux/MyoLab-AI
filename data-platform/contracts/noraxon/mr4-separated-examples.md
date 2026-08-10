# MR4 Separated Export Examples v0.1

## Evidence boundary
The available Motion Lab CSV Architecture documents the logical fields and signal shapes, but does not fully specify the physical row framing of `info.csv`. DAY10 therefore freezes **logical contract + safety rules** and leaves physical layout `NOT_VERIFIED` until an approved actual export is audited in the integrated repository.

## Logical record example
- `info.csv`: type, software versions, project, subject metadata surfaces, measurement_date, record_name.
- one or more independent signal files.

## Signal example A — EMG (`signal`)
Metadata includes `type=signal`, vendor `name`, `time_units=s`, `begin_time`, `frequency=2000`, `count`, `units=uV`. Data shape is `time,value`.

## Signal example B — COP (`signal_2d`)
Observed example family includes COP at `frequency=100`, `count=1650`, `units=mm` with data shape `time,x,y`.

## Cross-day anti-assumption
DAY09 single CSV may carry table-level `frequency=2000`. DAY10 explicitly forbids reusing that as a record-wide same-Fs rule. Per-signal metadata is the source for separated signals.

## Privacy warning
`last_name`, `first_name`, `born`, `project`, `measurement_date`, and `record_name` can carry identifying or quasi-identifying information. Synthetic fixtures never contain real values. Real audit must run only under approved DAY05 governance.
