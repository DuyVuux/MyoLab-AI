# DAY09 Golden Fixtures — Noraxon MR4 Single CSV

These fixtures are synthetic and contain no patient data. They encode the observed single-CSV anatomy documented by the Motion Lab CSV Architecture.

## Files
- `valid_minimal.csv`: minimal happy-path anatomy.
- `valid_unknown_fields.csv`: proves unknown metadata/columns are preserved at contract level.
- `invalid_missing_blank_separator.csv`: negative fixture; must fail DAY09 anatomy validation.
- `fixture-manifest.json`: SHA-256 and classification for each fixture.

## Important boundary
Passing these fixtures means **contract tooling is coherent**, not that a site export has been clinically validated. Actual approved exports are rechecked later at Gate B/retrospective validation.
