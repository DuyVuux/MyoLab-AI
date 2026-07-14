# ADR-0002 — Offline-First Before Realtime Clinical Claims

## Status
Draft

## Context
Realtime clinical claims require streaming integration, latency control, safety validation, workflow validation, and human-review design. MVP-0 should prove the pipeline with files first.

## Decision
MVP-0 will process synthetic/CSV/Noraxon-style exports offline. Demo may show near-real-time visualization but must not claim validated realtime clinical operation.

## Consequences
- First pipeline target: file → QC → features → fatigue evidence → JSON/report.
- Realtime is roadmap, not Day 1 build target.
