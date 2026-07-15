# Signal Ingestion Service — MVP-0 v0.1

## Responsibility

Convert a Generic CSV + JSON sidecar package into the canonical in-memory `NormalizedSignal` representation.

## Non-responsibilities

This service does not:

- filter or rectify sEMG;
- decide signal quality beyond structural/time/unit checks;
- compute RMS/MAV/MDF/MNF;
- compute MFCV/CV;
- infer fatigue;
- create clinical wording.

## Modules

```text
src/importers/base_importer.py
src/importers/csv_importer.py
src/normalizers/unit_normalizer.py
src/normalizers/channel_mapper.py
src/normalizers/metadata_extractor.py
src/validators/file_format_validator.py
src/validators/metadata_validator.py
```

## Contract

Input:

```text
<session>.csv
<session>.manifest.json
```

Output:

```python
ImportResult(
    signal=NormalizedSignal | None,
    issues=tuple[ValidationIssue, ...],
)
```

Critical issues return `signal=None`. Non-blocking issues may return a signal but must remain visible to downstream QC.

## Canonical unit

All supported amplitudes are converted explicitly to microvolts (`uV`):

```text
uV × 1
mV × 1,000
V  × 1,000,000
```

The source unit is preserved in channel metadata. Unit inference from amplitude is prohibited.

## Source integrity

The importer computes SHA-256 over the CSV bytes. When `source_hash_sha256` is present in the manifest, a mismatch blocks import with `SOURCE_HASH_MISMATCH`.

SHA-256 establishes byte-level identity only. It does not establish signal quality, authenticity of acquisition, or clinical validity.
