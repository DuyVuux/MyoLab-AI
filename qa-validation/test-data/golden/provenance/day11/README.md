# DAY11 Synthetic Provenance Fixtures

All fixtures are synthetic and contain no patient identifiers or real clinical signal.

- `synthetic-mr4-source.csv`: canonical known bytes for hashing tests.
- `synthetic-mr4-source-duplicate-name-copy.csv`: byte-identical copy under another filename; must deduplicate by content.
- corrupted `mutated-same-name.csv`: same conceptual filename family but different bytes; must receive a different source ID.

These fixtures support engineering integrity only and are not clinical evidence.
