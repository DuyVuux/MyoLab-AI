# Đặc tả Explainable Rule Engine v0.1

## Mục tiêu

Chuyển `FatigueEvidenceResult v0.1` thành kết luận kỹ thuật giải thích được, không tạo chẩn đoán, xác suất, FRS hoặc khuyến nghị điều trị.

## Input contract

- `downstream_allowed = true`;
- `abstention = false`;
- `config_id = fatigue_evidence_v0.1`;
- `schema_version = fatigue-evidence-result.v0.1`;
- có ít nhất một channel `evaluated`.

Nếu không đáp ứng, engine phải trả `abstained`.

## Output enum

```text
supported_pattern
no_supported_pattern
inconclusive
abstained
```

## Chính sách đa channel

- tất cả channel `supported_pattern` → overall `supported_pattern`;
- tất cả channel `no_supported_pattern` → overall `no_supported_pattern`;
- tất cả channel `inconclusive` → overall `inconclusive`;
- bất kỳ tổ hợp không đồng thuận nào → overall `inconclusive`.

## Explainability

Mỗi channel phải có:

- source pattern;
- rule strength;
- reason codes;
- decision basis;
- counterevidence;
- interpretation guard.

## Safety invariants

- `supported_pattern` không phải diagnosis;
- `no_supported_pattern` không phải `no_fatigue`;
- không output probability;
- không output FRS;
- không đưa treatment recommendation;
- human review vẫn bắt buộc;
- synthetic result không phải clinical evidence.
