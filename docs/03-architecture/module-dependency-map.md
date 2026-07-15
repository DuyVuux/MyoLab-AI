# Module Dependency Map — Day 3 Ingestion Slice

```mermaid
flowchart TD
    A[Generic CSV + sidecar manifest] --> B[metadata_validator]
    A --> C[file_format_validator]
    B --> D[metadata_extractor]
    C --> E[time-axis validation]
    D --> F[channel_mapper]
    E --> G[csv_importer]
    F --> G
    G --> H[NormalizedSignal]
    H --> I[Signal Quality Gate - Day 4+]
    I --> J[Preprocessing - later]
```

## Dependency rules

1. The importer depends on the Day 2 input contract.
2. Unit normalization happens before canonical object creation.
3. Structural or integrity failure blocks object creation.
4. A canonical object is not the same as a QC-passed session.
5. Downstream code consumes `NormalizedSignal`, not vendor CSV columns.
6. MFCV capability is not inferred by the importer.