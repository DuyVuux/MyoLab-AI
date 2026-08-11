# DAY33 Research Benchmark Corpus v1

This directory contains **synthetic known-truth research fixtures only**. It deliberately
does not contain raw patient, employer/customer, Noraxon site, or bulk public dataset
payloads.

## Why public data is cataloged but not copied here

DAY33 verifies public source provenance and licensing, then keeps raw public payloads in
external storage. This prevents multi-GB data from entering Git and preserves the project
rule that source data is referenced by manifest/hash rather than treated as source code.

## Corpus partitions

- `benchmark-development`: truth is visible and may support detector engineering in DAY34/35.
- `benchmark-locked`: signal payload is present, but truth is absent from the public manifest.
  DAY33 writes only a SHA-256 commitment. Do not inspect/reconstruct locked truth for tuning.

## Evidence semantics

Every payload item is `SYNTHETIC_KNOWN_TRUTH`, uses DAY22
`QC_WINDOW_WITH_CONTEXT`, contains no direct identifier, and has
`clinical_evidence=false`.

`SYNTHETIC_LOW_AMPLITUDE_STRESS` is an engineering stress case only. It is never a
synthetic stroke/paresis/atrophy case.

## Regeneration

From repository root:

```bash
PYTHONPATH=packages/semg-core \
python3 scripts/data/build_research_benchmark_corpus.py \
  --catalog data-platform/datasets/public-sEMG-catalog.v0.1.yaml \
  --output-root qa-validation/test-data/research/day33/corpus-build
```

The committed reference corpus is generated with the same builder version and is checked
by SHA-256 in the manifest.
