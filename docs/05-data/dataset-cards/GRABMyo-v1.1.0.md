# Dataset Card — GRABMyo v1.1.0

- Dataset ID: `GRABMYO_V1_1_0`
- Repository: PhysioNet
- DOI: `10.13026/89dm-f662`
- License: `CC BY 4.0` — reverified for DAY64
- Status: `VERIFIED_USABLE`
- Phase 5R selection: `INCLUDE_CORE`

Authoritative release facts used by the adapter contract: 43 healthy participants, three
sessions/days, 2048 Hz acquisition, 32 recorded channels per file of which 28 are sEMG
channels and four are unused. Header examples declare physical units in `mV`.

The adapter must preserve the original raw hash and source unit. If canonical output uses
`V`, the exact `mV → V` conversion is explicit with factor `1e-3` and transform provenance.
No anatomy, gesture name, or site equivalence is inferred from channel names alone.

Raw payload policy: external configured root only; not redistributed in this package.
