# DAY38 FEYNMAN LEARNING GUIDE — QC Freeze, Properties & Determinism

## Core Concept
Imagine building a house on bedrock vs sand. Before adding high-level fatigue features (Phase 3), DAY38 freezes the foundation — verifying that signal quality rules are invariant, reproducible, and fail closed.

## Key Principles
1. **Property & Metamorphic Verification**: Testing fundamental invariants (e.g. low amplitude is not poor contact, QC fail blocks metric, raw data is never mutated) across arbitrary inputs.
2. **Allowlist Hash Freezing**: Recording exact SHA-256 signatures for the 15 files that define QC behavior, ensuring any unverified code drift is detected instantly.
3. **Fail-Closed Safety**: Any missing evidence or unverified quality status results in metric abstention or block, never false confidence.
