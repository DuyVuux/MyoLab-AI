# Test Plan Day 20

## Positive

```text
create session
→ import pass
→ mapping complete
→ preflight ready
→ calibration pass
→ quality pass
→ analysis queued
```

## Warning

```text
quality warning
→ trước acknowledgement: analysis blocked
→ sau acknowledgement: queued_with_warnings
```

## Fail

```text
quality fail
→ analysis handoff abstained
→ no conclusion payload
→ remeasure action
```

## Negative

- Missing unit.
- Duplicate channel mapping.
- Corrupt import.
- Patient creates clinical session.
- UC3/UC4 use clinical session type.
- Invalid state transition.
