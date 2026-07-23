# Kế hoạch kiểm thử Day 21

- Idempotency: cùng session + key trả cùng analysis ID.
- State machine: không nhảy stage, terminal không quay lại running.
- Warning: được propagate tới terminal output.
- Abstention: QC fail không gọi inference runtime.
- Failure: runtime error khác abstention và có trace ID.
- Safety: API không chứa raw samples hoặc probability claim.
- Contract: JSON Schema Draft 2020-12 pass.
