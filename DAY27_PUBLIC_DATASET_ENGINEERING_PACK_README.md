# Day 27 Public Dataset Engineering Pack

Gói additive để tích hợp vào skeleton hiện tại. Không chứa raw signal, archive tải từ internet, model artifact hoặc metric model.

## Mục tiêu

```text
exact source + license + immutable hash
→ archive inventory
→ profile-driven adapter
→ strict label mapping
→ subject-safe split + sealed test
→ Engineering Data Gate
```

## Quick start

```bash
unzip -n day27_public_dataset_engineering_pack.zip
bash scripts/dev/run_day27_checks.sh
```

Checker trong ZIP chỉ xác minh tooling/contract bằng fixture synthetic. Gate cho dataset thật vẫn ở `PENDING_EXTERNAL_DATA` cho đến khi bạn tải và kiểm tra canonical dataset theo kế hoạch.

## An toàn

- Không commit `/data/datasets/`.
- Không đưa raw patient/public signal vào Git.
- Download script mặc định dry-run và yêu cầu `--execute --accept-license`.
- Training tiếp tục bị khóa.
