# DAY 17 — CANONICAL OUTPUT SCHEMA VÀ OPENAPI CONTRACT v0.1

**Điều kiện bắt đầu:** Day 16 regression baseline đã pass, freeze và commit.  
**Mục tiêu:** tạo một contract ổn định giữa offline analysis pipeline với backend/frontend/report, thay vì để client phụ thuộc trực tiếp vào 12 stage files nội bộ.  
**Không thuộc phạm vi:** triển khai production FastAPI server, database, authentication thật, background worker, file storage, dashboard hoặc clinical report final.

---

## 1. Kết quả cuối ngày

```text
Offline Analysis Package
        ↓
API Summary Builder
        ↓
SessionAnalysisSummary v0.1
        ↓
JSON Schema + OpenAPI 3.1
        ↓
Contract Tests + Examples
```

Artifact chính:

```text
openapi.yaml

docs/04-api/
├── api-overview.md
├── offline-analysis-api-contract.md
├── api-error-taxonomy.md
└── openapi-v0.1.yaml

docs/05-data/
└── session-analysis-summary-contract.md

packages/common-schemas/json/
├── session-analysis-summary.schema.json
├── analysis-job.schema.json
├── session-import-response.schema.json
└── problem-details.schema.json

services/api-server/src/schemas/
├── analysis_contract.py
└── api_errors.py

scripts/data/
└── build_analysis_api_summary.py

scripts/dev/
├── validate_openapi_contract.py
└── run_day17_checks.sh
```

---

## 2. Vì sao cần canonical summary?

Nếu frontend đọc trực tiếp:

```text
04-time-domain-features.json
06-frequency-features.json
07-trend-features.json
08-fatigue-evidence.json
09-fatigue-rule.json
10-explainable-inference.json
```

thì bất kỳ thay đổi nội bộ nào cũng có thể phá UI. Canonical summary tạo một anti-corruption layer:

```text
Internal stage contracts
→ stable API-facing contract
```

Nó chỉ chứa dữ liệu cần thiết cho UI/report review, không chứa PSD vectors, raw samples hoặc các chi tiết DSP quá sâu.

---

## 3. Các phần phải học kỹ

### 3.1. API contract first

Contract-first nghĩa là chốt:

```text
endpoint
request schema
response schema
status code
error semantics
versioning
```

trước khi viết route/business implementation.

### 3.2. JSON Schema và OpenAPI

- JSON Schema mô tả cấu trúc dữ liệu.
- OpenAPI mô tả HTTP API và có thể tham chiếu các schema.
- OpenAPI không thay thế test business logic.

### 3.3. HTTP method và status code

- `POST /v1/sessions/import`: tạo session import resource → `201 Created`.
- `POST /v1/sessions/{id}/analyses`: tạo analysis job → `202 Accepted`.
- `GET /v1/analyses/{id}`: đọc job state → `200 OK`.
- `GET /v1/analyses/{id}/summary`: đọc summary → `200 OK`.
- Dữ liệu không đủ phân tích vẫn là một kết quả domain `abstained`, không nhất thiết là HTTP 500.

### 3.4. Synchronous và asynchronous

Offline pipeline có thể chạy vài giây/phút. Contract nên dùng job resource:

```text
POST analyze → 202 + job id
GET job → queued/running/completed/abstained/failed
GET summary khi terminal
```

### 3.5. Idempotency

Client có thể retry. `Idempotency-Key` giúp tránh tạo hai analysis job cho cùng request ngoài ý muốn.

### 3.6. Error taxonomy

Phân biệt:

- `400`: request syntax/field sai;
- `404`: resource không tồn tại;
- `409`: conflict/version mismatch/non-empty duplicate;
- `413`: file quá lớn;
- `422`: semantic validation không đạt;
- `500`: lỗi hệ thống ngoài dự kiến.

QC fail không phải lỗi hệ thống. Nó trở thành `abstained` trong analysis domain.

### 3.7. API versioning

Day 17 dùng:

```text
URL version: /v1
schema version: session-analysis-summary.v0.1
config/model versions: nằm trong provenance
```

Breaking API change cần `/v2` hoặc migration policy rõ; thay đổi additive có thể giữ `/v1` nếu backward compatible.

---

## 4. Canonical `SessionAnalysisSummary v0.1`

Các nhóm field:

```text
identity
status
source/provenance
signal quality
MFCV capability
channel feature trends
structured evidence
technical rule conclusion
engineering confidence
explainability
safety and review requirements
links
summary hash
```

Không chứa:

```text
raw samples
PSD vector từng bin
patient name/MRN/email/phone
diagnosis
treatment recommendation
probability of fatigue
FRS
return-to-play decision
```

---

## 5. Kế hoạch tuần tự theo bước

## Bước 0 — Xác nhận Gate Day 16

**Thời gian:** 08:00–08:15

```bash
git status --short
git log -3 --oneline
bash scripts/dev/run_day16_checks.sh
```

**Done:** baseline v0.1 tồn tại và compare PASS.

---

## Bước 1 — Tạo branch/checkpoint

**Thời gian:** 08:15–08:25

```bash
git switch -c day17-output-schema-openapi-contract
git status --porcelain=v1 > /tmp/day17-start-status.txt
git diff > /tmp/day17-start.patch
```

---

## Bước 2 — Vẽ consumer map

**Thời gian:** 08:25–08:50

Vẽ:

```text
Offline package
  ├── API server
  ├── Web portal
  ├── Report generator
  └── QA/audit tools
```

Ghi field mỗi consumer cần. Không đưa field vào API chỉ vì internal stage có field đó.

**Output:** `docs/note/day17/02-reading-notes.md`.

---

## Bước 3 — Học HTTP lifecycle và job resource

**Thời gian:** 08:50–09:20

Tự mô tả sequence:

```text
upload file
→ import session created
→ request analysis
→ job queued/running
→ terminal status
→ summary available
```

Giải thích vì sao analysis `abstained` vẫn có thể trả HTTP 200 khi client đọc result.

**Output:** `docs/note/day17/03-math-notes.md` (ghi state machine/logic, không nhất thiết có phép tính số).

---

## Bước 4 — Review current root `openapi.yaml`

**Thời gian:** 09:20–09:35

```bash
ls -l openapi.yaml || true
sed -n '1,120p' openapi.yaml 2>/dev/null || true
cp openapi.yaml /tmp/openapi.before-day17.yaml 2>/dev/null || true
```

Nếu file hiện có chứa contract thật, merge thủ công. Không ghi đè mù.

---

## Bước 5 — Chốt data contract trước code

**Thời gian:** 09:35–10:10

Viết:

```text
docs/05-data/session-analysis-summary-contract.md
```

Chốt:

- required vs optional;
- enum values;
- unit của slope/percent change;
- null behavior khi abstained;
- safety invariants;
- provenance;
- summary hash.

---

## Bước 6 — Viết JSON Schemas

**Thời gian:** 10:10–11:00

Tạo:

```text
session-analysis-summary.schema.json
analysis-job.schema.json
session-import-response.schema.json
problem-details.schema.json
```

Dùng JSON Schema Draft 2020-12.

**Done:** schema không cho phép `score_is_probability=true` hoặc `clinical_use_allowed=true`.

---

## Bước 7 — Viết Pydantic contract models

**Thời gian:** 11:00–11:45

File:

```text
services/api-server/src/schemas/analysis_contract.py
```

Model phải validate:

- status/conclusion enums;
- confidence score `[0,1]` hoặc null;
- score không phải probability;
- clinical use false;
- human review true;
- không direct identifiers;
- summary hash có 64 hex chars.

---

## Bước 8 — Viết API summary builder

**Thời gian:** 11:45–12:20

Builder đọc Day 15 package và rút gọn thành:

```text
QC summary
feature trend summaries
MFCV eligibility
pattern/evidence summary
rule result
engineering confidence
explainability
safety
```

Không copy full feature rows hoặc PSD vectors.

---

## Bước 9 — Viết CLI tạo summary

**Thời gian:** 13:00–13:25

```bash
python scripts/data/build_analysis_api_summary.py \
  --analysis-dir qa-validation/evidence/day17-golden-analysis \
  --output qa-validation/evidence/day17-golden-api-summary.json
```

---

## Bước 10 — Viết OpenAPI 3.1 contract

**Thời gian:** 13:25–14:35

Canonical source:

```text
docs/04-api/openapi-v0.1.yaml
```

Sau review, đồng bộ sang root:

```bash
cp docs/04-api/openapi-v0.1.yaml openapi.yaml
```

Endpoint tối thiểu:

```text
POST /v1/sessions/import
POST /v1/sessions/{session_id}/analyses
GET  /v1/analyses/{analysis_id}
GET  /v1/analyses/{analysis_id}/summary
GET  /v1/analyses/{analysis_id}/manifest
GET  /health
```

---

## Bước 11 — Viết error taxonomy và Problem Details

**Thời gian:** 14:35–15:00

File:

```text
docs/04-api/api-error-taxonomy.md
services/api-server/src/schemas/api_errors.py
```

Mỗi error có:

```text
type
title
status
detail
instance
error_code
trace_id
```

Không đưa raw traceback hoặc nội dung file vào response.

---

## Bước 12 — Tạo request/response examples

**Thời gian:** 15:00–15:35

Tạo:

```text
docs/04-api/examples/session-import.response.json
docs/04-api/examples/analysis-job.response.json
docs/04-api/examples/analysis-completed.response.json
docs/04-api/examples/analysis-abstained.response.json
docs/04-api/examples/problem-details.response.json
```

Completed và abstained examples phải được sinh từ actual Day 15 package, không viết tay lệch contract.

---

## Bước 13 — Viết OpenAPI validator

**Thời gian:** 15:35–16:10

File:

```text
scripts/dev/validate_openapi_contract.py
```

Validator kiểm tra:

- OpenAPI version 3.1.x;
- unique operationId;
- path/method hợp lệ;
- local `$ref` resolve được;
- security scheme tồn tại;
- responses có `application/json` hoặc `application/problem+json`;
- examples khớp JSON schemas;
- không prohibited fields/claims.

---

## Bước 14 — Viết contract tests

**Thời gian:** 16:10–16:45

File:

```text
qa-validation/automated-tests/test_api_contract_day17.py
```

Test:

- golden summary schema pass;
- abstained summary schema pass;
- summary deterministic;
- no raw/PHI fields;
- OpenAPI local refs valid;
- operationIds unique;
- examples đúng schema;
- safety booleans bất biến.

---

## Bước 15 — Chạy golden API summary

**Thời gian:** 16:45–17:10

Dùng offline pipeline tạo package golden và abstained, sau đó build summaries.

**Expected:**

```text
golden → completed / supported_pattern / engineering_high
flatline → abstained / confidence score null
```

---

## Bước 16 — Validate schemas và OpenAPI

**Thời gian:** 17:10–17:35

```bash
python scripts/dev/validate_day17_outputs.py
python scripts/dev/validate_openapi_contract.py --openapi openapi.yaml
```

---

## Bước 17 — Review backward compatibility

**Thời gian:** 17:35–17:55

Trả lời:

1. Thêm optional field có breaking không?
2. Đổi enum value có breaking không?
3. Đổi `confidence` từ number sang string có breaking không?
4. Xóa field có breaking không?
5. Khi nào cần `/v2`?

**Output:** `docs/note/day17/07-decisions.md`.

---

## Bước 18 — Review privacy/security surface

**Thời gian:** 17:55–18:15

Xác nhận:

- không direct identifiers trong contract;
- upload endpoint không echo raw file;
- error không leak path/traceback;
- bearer auth chỉ là contract placeholder, chưa claim production security;
- raw signal vẫn on-prem/object storage có kiểm soát.

---

## Bước 19 — Hoàn thiện notes

**Thời gian:** 19:00–19:30

Hoàn thiện `docs/note/day17/01...09`.

---

## Bước 20 — Chạy one-command checker

**Thời gian:** 19:30–20:00

```bash
bash scripts/dev/run_day17_checks.sh
```

Full Day 16 regression tùy chọn:

```bash
DAY17_FULL_REGRESSION=1 bash scripts/dev/run_day17_checks.sh
```

---

## Bước 21 — Tự kiểm tra kiến thức

1. JSON Schema khác OpenAPI thế nào?
2. Vì sao `POST analyze` trả `202`?
3. Vì sao QC fail không phải HTTP 500?
4. Idempotency-Key giải quyết rủi ro gì?
5. `400`, `409`, `413`, `422` khác nhau thế nào?
6. Vì sao frontend không nên đọc 12 stage files trực tiếp?
7. Breaking change là gì?
8. Vì sao confidence score phải ghi `score_is_probability=false`?
9. Vì sao API summary không chứa PSD vector đầy đủ?
10. Vì sao human review vẫn là required field?

Đạt ít nhất 8/10.

---

## Bước 22 — Commit

```bash
git add \
  openapi.yaml \
  docs \
  packages/common-schemas \
  services/api-server/src/schemas \
  scripts \
  qa-validation

git diff --staged --check
git diff --staged --stat

git commit -m \
  "day17: define canonical analysis output and openapi contract v0.1"

git tag day17-api-contract-v0.1
```

---

## 6. Definition of Done

- [ ] Day 16 baseline pass trước khi bắt đầu.
- [ ] Canonical summary schema hoàn chỉnh.
- [ ] Golden và abstained summary đều valid.
- [ ] Summary deterministic.
- [ ] OpenAPI 3.1 contract valid theo checker.
- [ ] operationId unique.
- [ ] Examples valid.
- [ ] Error taxonomy rõ.
- [ ] Không raw sample/direct identifier/prohibited claim.
- [ ] `clinical_use_allowed=false`.
- [ ] `human_review_required=true`.
- [ ] `score_is_probability=false`.
- [ ] Tất cả Markdown mới bằng tiếng Việt.

---

## 7. Handoff tiếp theo

Sau Day 17, bước hợp lý là:

```text
Day 18 — Dashboard wireframe + clinical-safe UI copy
Day 19 — Minimal API mock/backend adapter
Day 20 — Dashboard Import/Context + Signal Quality
```
