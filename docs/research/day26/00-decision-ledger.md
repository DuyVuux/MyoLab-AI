# Day 26 — Decision Ledger

| ID | Decision | Status | Rationale | Supersedes/depends on |
|---|---|---|---|---|
| D26-001 | Day 26 là blueprint-only; `trainingAllowed=false` | LOCKED | Chọn phương pháp trước results | Day25 readiness |
| D26-002 | Task A/B/C là ba lane riêng | LOCKED | Target/metric/claim khác nhau | Day25 taxonomies |
| D26-003 | Sparse feature baseline F0–F4; HD/MFCV gated | LOCKED | 4–16 channel scope, site MFCV chưa xác minh | Feature review |
| D26-004 | Minimum model set: Dummy×2, LDA, LR, Linear SVM, RF | LOCKED | Bao phủ sanity/linear/nonlinear với burden hợp lý | Model review |
| D26-005 | Cross-subject grouped evaluation là population benchmark chính | LOCKED | Tránh identity leakage | Validation review |
| D26-006 | Within-session chỉ debug | LOCKED | Không phản ánh deployment generalization | Validation review |
| D26-007 | P1 few-shot là MVP personalization research path | PROVISIONAL_LOCKED | Evidence tốt hơn P2/P3; P4 No-Go | Personalization review |
| D26-008 | Task B dùng fatigue context/supportability; Architecture 3 ưu tiên | LOCKED | Fatigue là một nguồn shift, không diagnosis mặc định | Fatigue review |
| D26-009 | Primary metric: subject-macro repetition Macro F1 | LOCKED | Equal subject/class weight | Metrics review |
| D26-010 | Probability chỉ sau fold-contained calibration gate | LOCKED | Tránh confidence semantics giả | Metrics review |
| D26-011 | File manifest+hash là governance SSOT; MLflow là mirror | LOCKED | Auditability + usability | Governance review |
| D26-012 | CPU single-thread là reference runtime | PROVISIONAL_LOCKED | Reproducibility trước optimization | Reproducibility policy |
| D26-013 | Real resolved `uv.lock` là hard gate trước Day29 | LOCKED | Không fabricate dependency lock | Reproducibility policy |
| D26-014 | Motion Lab local training/site adapter vẫn externally blocked | LOCKED | Actual export chưa site-verified | Day25 addendum |
