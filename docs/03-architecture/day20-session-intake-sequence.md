# Sequence Session & Data Intake Day 20

```mermaid
sequenceDiagram
  actor KTV
  participant UI
  participant MockAPI
  participant IntakeStore

  KTV->>UI: Tạo session pseudonymous
  UI->>MockAPI: POST /v1/sessions
  MockAPI->>IntakeStore: Lưu SessionRecord
  KTV->>UI: Chọn nguồn và scenario import
  UI->>MockAPI: POST /v1/sessions/{id}/imports
  MockAPI->>IntakeStore: Lưu ImportRecord
  alt Mapping thiếu
    MockAPI-->>UI: mapping_required
    KTV->>UI: Bổ sung unit/muscle/side
    UI->>MockAPI: PUT /v1/imports/{id}/mapping
  end
  UI->>MockAPI: GET preflight
  MockAPI-->>UI: ready | mapping_required | import_blocked
  KTV->>MockAPI: POST calibration
  MockAPI-->>UI: pass | warning | fail
  UI->>MockAPI: GET quality
  alt QC warning
    KTV->>MockAPI: POST acknowledgement
  end
  UI->>MockAPI: POST analysis
  MockAPI-->>UI: queued | queued_with_warnings | abstained
```

## Blockers

| Upstream | Blocker | Downstream bị chặn |
|---|---|---|
| Import | `import_rejected` | Mapping/Preflight/QC |
| Mapping | completeness < 1 | Preflight ready |
| Calibration | fail | Analysis handoff |
| QC | warning chưa acknowledge | Analysis handoff |
| QC | fail | Analysis handoff queued; trả abstained |
