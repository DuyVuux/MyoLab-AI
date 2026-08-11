# Dataset Card — GRABMyo v1.1.0

## Identity
- Dataset ID: `GRABMYO_V1_1_0`
- Repository: PhysioNet
- DOI: `10.13026/89dm-f662`
- License: **CC BY 4.0 — VERIFIED**
- DAY33 role: public external source for multi-day/cross-session research.

## Observed acquisition facts
The official PhysioNet record describes 43 healthy participants recorded across three
sessions/days with a 2048 Hz amplifier. The protocol uses forearm and wrist electrode
rings and records hand/wrist gestures plus rest. DAY33 treats these as external-source
facts, not as MotionLab/Noraxon equivalence.

## Allowed use in this roadmap
- validate public-data acquisition and provenance workflow;
- later adapter/windowing research;
- cross-day domain challenge;
- engineering benchmark context.

## Forbidden claims
- no Vinmec/site representativeness;
- no clinical efficacy;
- no pathology ground truth;
- no assumption that GRABMyo electrode geometry equals Ultium layout.

## Storage policy
Raw files must live under an external configured data root. The repository stores only
catalog metadata, hashes/ledgers, adapters and synthetic fixtures.
