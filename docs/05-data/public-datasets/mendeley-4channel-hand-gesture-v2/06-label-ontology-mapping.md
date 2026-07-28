# Label ontology mapping

Allowed Task A targets:

```text
rest, hand_open, hand_close, wrist_flexion, wrist_extension
```

Additional states remain separate:

```text
unknown, ambiguous, artifact, not_attempted, transition
```

Mọi mapping cần source protocol/data-dictionary evidence. Unmapped source labels phải fail hoặc exclude có reason; không default về rest.
