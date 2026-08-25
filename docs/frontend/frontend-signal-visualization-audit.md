# Frontend Signal Visualization Audit

## Architecture

- Renderer: React + SVG polyline.
- Data model: `WindowIdentity`, `Series`, `SignalViewerModel`.
- RAW/PROCESSED: explicit panel kind. Processed series requires `manifest_id`.
- Time axis: implicit x coordinate in seconds, but no rendered axis/ticks.
- Units: displayed in panel caption.
- Sampling rate: validated in `validateWindowIdentity` and `buildSeries`, not displayed in the panel caption.
- Mask regions: converted to intervals and shown in `<details>`, but not visually overlaid on waveform.
- Decimation: min/max decimation in `decimateMinMax`, default `max_points = 2000`.
- Interactions: no zoom, pan, brush, crosshair, synchronized selection, or tooltip.

## Correctness Strengths

- Missing window identity throws explicit errors.
- Invalid sample ranges and sampling rate fail closed.
- RAW and PROCESSED duration mismatch fails.
- Processed series cannot render without a manifest id.
- Null/invalid numeric values are normalized.
- Mask intervals are preserved as evidence text.

## Correctness Gaps

- Visual decimation is not disclosed in the UI.
- The chart lacks visible time/channel axes, so users cannot inspect exact timebase without reading metadata.
- Masked intervals are textual only; users cannot see mask placement on the waveform.
- No UI for processing version/filter details beyond manifest/profile ids.
- No large-series browser performance measurement was captured during discovery.

## Status

Signal visualization is `FUNCTIONAL` and research-safe for a golden demo, but not yet an advanced scientific signal explorer.
