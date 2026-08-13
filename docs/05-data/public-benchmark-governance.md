# Public Benchmark Governance v1.0

## Purpose

Phase 5R uses already-catalogued public sEMG sources to test portability of the engineering
pipeline. It is not a clinical-validation cohort and it is not a substitute for MotionLab site
data. Dataset inclusion is governed before any benchmark outcome is inspected.

## Selected execution core

### GRABMyo v1.1.0

Selected because the authoritative release provides a stable version/DOI, open access under
CC BY 4.0, explicit subject/session organization, explicit 2048 Hz sampling, and WFDB-style
files. The acquisition layout (forearm/wrist rings) is deliberately different from HD-sEMG.
Source waveform unit is `mV`; DAY65 must perform any `mV → V` conversion explicitly and
record transform provenance.

### Hyser v2.0.0

Selected as the complementary HD-sEMG domain. The authoritative PhysioNet record documents
20 subjects, two sessions, 256-channel HD-sEMG at 2048 Hz and an **Open Data Commons
Attribution License v1.0**. This corrects the earlier starting-context statement that called
Hyser CC BY 4.0.

## Verified-but-deferred candidates

Cerqueira fatigue v2 and the Mendeley 4-channel gesture v2 dataset remain verified public
research assets. They are not in the Phase-5R execution core because the benchmark is
intentionally limited to two directly complementary domains and because their current bulk
payloads were not acquired into this execution runtime. Deferral is not a license rejection.

## License and access policy

- A public download is not treated as permission by itself; an explicit license is required.
- Raw public payloads live under an external configured data root and are never committed.
- The repository may contain access recipes, version/DOI, source metadata fingerprints,
  externally supplied checksum manifests and adapter code.
- Dataset citation is mandatory in any portfolio benchmark publication.
- Public healthy data does not establish clinical effectiveness, hospital readiness or site
  representativeness.

## Evidence tier

All selected data remain `PUBLIC_EXTERNAL`. Public labels do not become
`EXPERT_ANNOTATION` or `ADJUDICATED_REFERENCE` merely because they are published.

## Runtime acquisition status

At DAY64, authoritative metadata/access/license pages are reachable through the research
browser, but raw binary waveform downloads are not materialized inside the execution
container. This is recorded as a downstream-relevant limitation and is re-evaluated at the
DAY67 execution gate.
