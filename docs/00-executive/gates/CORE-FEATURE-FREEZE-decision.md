# CORE FEATURE FREEZE DECISION STATEMENT

## Status Decision
**CORE_FEATURE_FREEZE**

## Inputs Verified
- `M6-R`: RESEARCH_ML_NOT_JUSTIFIED
- `Final-R`: READY_WITH_LIMITATIONS
- `Phase 7R Tests`: 13/13 PASS
- `ML Default`: OFF

## Enforced Action (Strict Boundaries)
Nghiêm cấm tuyệt đối việc thêm các tính năng/mô hình sau vào backend/core:
1. SSL (Self-Supervised Learning)
2. Transformer models
3. Classifier mới (new classifier)
4. Calibration
5. Conformal prediction
6. OOD (Out-Of-Distribution) models
7. RL (Reinforcement Learning)
8. MFCV (nếu chưa có bằng chứng eligibility đầy đủ)
9. Clinical prediction

## Phạm vi chỉnh sửa cho phép
Chỉ cho phép sửa bug nếu việc tích hợp giao diện (UI integration) làm bộc lộ ra lỗi thực sự trong quá trình kết nối end-to-end.
