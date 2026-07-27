# Day 25 Research-Grounded Starter Pack v2.0

Gói này thay thế **nội dung Day 25 dạng giả định ban đầu** bằng một phiên bản được tổng hợp trực tiếp từ bốn báo cáo deep research tiền Day 25 trong Project.

## Trạng thái dự kiến

```text
status                = CONDITIONAL_READY
implementationAllowed = true
trainingAllowed       = false
```

## Tại sao chưa được training?

Các nguồn nghiên cứu cho thấy landscape dataset/repository đã đủ để dựng data engineering và experiment contract, nhưng các điểm site-level còn thiếu:

- chưa kiểm actual de-identified export từ Motion Lab;
- chưa khóa field-level schema của export;
- native JSON export chưa được xác minh;
- MFCV eligibility của setup 16 Ultium sensors chưa được xác minh;
- exact hardware/software/module/license tại site chưa được ghi nhận.

## Cách cài vào repository

```bash
unzip -l day25_research_grounded_starter_pack.zip
unzip -n day25_research_grounded_starter_pack.zip
bash scripts/dev/run_day25_research_checks.sh
```

`-n` giúp không ghi đè file đang có. Khi file cùng vai trò đã tồn tại, merge từng schema/function/register và tăng version nếu semantics thay đổi.

## Artifact trọng tâm

```text
docs/plans/DAY25_EXECUTION_PLAN.md

docs/05-data/day25-research/
├── source-evidence-register.csv
├── dataset-inventory-v0.2.csv
├── dataset-license-access-register-v0.2.csv
├── research-conflict-register.csv
├── free-first-research-stack.md
├── repository-reuse-shortlist.md
├── canonical-research-dataset-contract.md
├── domain-gap-register-v0.2.csv
└── data-readiness-gate-policy.md

integrations/devices/noraxon/
├── public-vs-site-capability-matrix.csv
├── export-format-register.csv
├── logical-field-dictionary-draft.csv
├── site-evidence-request-checklist.md
├── motion-lab-questions-vi.md
├── noraxon-support-questions-en.txt
└── site-export-evidence-bundle.template.json
```

## Safety invariants

- Không commit raw signal hoặc direct identifier.
- Không biến `unknown` thành `rest`.
- Không random split theo window.
- Không gọi engineering score là xác suất lâm sàng.
- Không dùng dataset restricted khi chưa có DUA/IRB.
- Không gọi JSON là native MR3 output khi chưa có bằng chứng.
- Không tính MFCV khi geometry/IED/orientation chưa được xác minh.
