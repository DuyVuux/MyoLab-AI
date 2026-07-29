# PRE-DAY30 — Kế hoạch triển khai EDA thật cho Mendeley và GRABMyo

**Mục tiêu:** hoàn tất EDA/QC có bằng chứng cho cả hai public dataset trước Day 30, trong khi raw data không đi vào Git và máy không cần giữ một bản sao đầy đủ của mọi corpus.

**Vai trò:** Single Operator.

**Phạm vi:** dữ liệu public cho Task A; chưa huấn luyện; chưa mở sealed test; chưa harmonize/pooled training; không suy diễn hiệu năng sang Noraxon/Vinmec.

---

## 1. Kết quả cuối cần đạt

```yaml
mendeley:
  real_eda_executed: true
  readiness: GO_FOR_DAY30_HARMONIZATION
  test_signal_rows_read: 0

grabmyo:
  real_eda_executed: true
  cross_day_audit_completed: true
  readiness: GO_FOR_DAY30_HARMONIZATION
  test_signal_rows_read: 0

pre_day30_dual_gate:
  decision: GO_FOR_DAY30_HARMONIZATION
  day30_full_execution_allowed: true
  day31_training_allowed: false
```

Nếu không đạt đủ, output phải là `BLOCKED_WITH_EVIDENCE`, không đổi thành PASS thủ công.

---

## 2. Kiến trúc hai vùng

### ZONE 1 — repository gốc

```text
/home/duyvd9/massive/projects/semg-fatigue/MyoLab-AI/
```

Chứa:

- source code;
- schema/config;
- dataset source/license records;
- mapping/ontology;
- logical split manifest và test seal;
- report Markdown;
- evidence nhỏ, đã tổng hợp;
- test tự động.

Không chứa:

- archive dataset;
- raw waveform;
- extracted corpus;
- cache remote;
- hàng nghìn ảnh EDA;
- model binary.

### ZONE 2 — controlled data workspace

```text
/home/duyvd9/massive/projects/myolab-ai-data/
```

Chứa:

```text
external/<dataset_id>/
├── source-metadata/       # landing-page receipt, URL list, remote HEAD metadata
├── remote-catalog/        # object catalog; chưa phải signal
├── cache/                 # cache bounded, có thể xóa
├── acquired/              # file đã tải có chủ đích; có thể rỗng
├── extracted/             # chỉ dùng nếu buộc phải tải archive
├── normalized/            # canonical records nếu thực sự cần
├── metadata/              # Parquet/CSV indexes
├── splits/                # subject/day/repetition split + test seal
├── derived/               # summary/features/index, không copy raw vô nghĩa
└── evidence/day28|day29/  # evidence đầy đủ
```

---

## 3. Thứ tự thực thi bắt buộc

## Bước 0 — Freeze trạng thái trước chạy

**Input**

- Git worktree hiện tại.
- Day 27/28/29 manifests.
- Hai absolute path đã khóa.

**Action**

```bash
git status --short
python scripts/data/check_two_zone_contract.py \
  --config data-platform/configs/pre_day30_storage.local.yaml
```

**Output**

```text
qa-validation/evidence/pre-day30/two-zone-contract-check.json
```

**Stop condition**

- ZONE 1 hoặc ZONE 2 không đúng path;
- ZONE 2 nằm bên trong ZONE 1;
- repo chứa raw/archive lớn;
- test seal đã mở.

---

## Bước 1 — Bootstrap ZONE 2, không tải dữ liệu

**Input:** storage config.

**Action**

```bash
bash scripts/dev/bootstrap_pre_day30_storage.sh --apply
```

**Output:** directory tree và marker files.

**Không được làm:** `wget -r`, `curl` toàn bộ archive, copy raw vào repo.

---

## Bước 2 — Tạo remote object catalog

**Input**

- official source record;
- URL từng file nếu repository cung cấp;
- metadata: subject/day/gesture/repetition nếu biết.

**Action**

1. Tạo `remote-objects.input.csv` từ template.
2. Chạy HTTP `HEAD`/range capability audit.
3. Không đọc body tín hiệu.

```bash
python scripts/data/build_remote_catalog.py \
  --input /home/duyvd9/massive/projects/myolab-ai-data/external/grabmyo-v1.1.0/source-metadata/remote-objects.input.csv \
  --output /home/duyvd9/massive/projects/myolab-ai-data/external/grabmyo-v1.1.0/remote-catalog/remote-catalog.json
```

**Output**

- URL;
- size;
- ETag/Last-Modified;
- `Accept-Ranges`;
- format;
- partition/group metadata;
- signal-access feasibility.

**Stop condition**

- source URL không official;
- license/source record chưa pass;
- object không có định danh subject/repetition tối thiểu;
- source chỉ là monolithic archive nhưng kế hoạch lại ghi streaming từng file.

---

## Bước 3 — EDA metadata-only

**Input:** remote catalog.

**Action**

Không đọc waveform. Tính:

- tổng file và bytes;
- file type;
- subject/day/gesture/repetition coverage;
- missing groups;
- duplicate URL/ETag/size candidates;
- expected disk/network budgets.

**Output**

```text
ZONE2/.../evidence/day28|day29/metadata-eda-summary.json
ZONE2/.../evidence/day28|day29/metadata-coverage.csv
```

**Decision**

- `GO_FOR_BOUNDED_SAMPLE`;
- `BLOCKED_CATALOG_INCOMPLETE`;
- `MONOLITHIC_ARCHIVE_REQUIRES_CONTROLLED_ACQUISITION`.

---

## Bước 4 — Chọn sample có giới hạn

**Input:** catalog + split manifest.

**Action**

Chỉ chọn từ `train` và `validation`, stratify theo:

```text
dataset × subject × day × gesture × repetition
```

Dùng ngân sách cố định, ví dụ:

```yaml
max_total_bytes: 2147483648  # 2 GiB
max_records: 300
subjects_per_dataset: 8
gestures_all_required: true
days_all_required_for_grabmyo: true
random_seed: 302026
```

```bash
python scripts/data/select_remote_sample.py \
  --catalog <remote-catalog.json> \
  --config data-platform/configs/pre_day30_remote_eda.research.yaml \
  --output <sample-plan.json>
```

**Output:** immutable sample-plan + hash.

**Stop condition:** sample chứa `partition=test`.

---

## Bước 5 — Bounded-sample signal EDA

**Input:** sample plan.

**Action**

Đọc một record/chunk, tính summary, ghi output, giải phóng RAM. Cache có giới hạn và có thể xóa.

```bash
python scripts/data/streaming_signal_eda.py \
  --plan <sample-plan.json> \
  --output-dir <ZONE2/evidence/dayXX/sample-eda> \
  --mode bounded-sample
```

**Output mỗi record/kênh**

- count;
- duration nếu sampling đã xác minh;
- mean/std/min/max;
- RMS/MAV;
- nonfinite/zero/flatline ratios;
- potential clipping;
- DC offset;
- source bytes actually transferred;
- cache hit/miss;
- reason codes.

**Stop condition**

- sampling/unit chưa xác minh mà report lại gắn đơn vị/thời gian tuyệt đối;
- parser đọc test signal;
- RAM vượt budget;
- cache vượt budget.

---

## Bước 6 — Quyết định có cần full streaming scan

Bounded sample chỉ trả lời: parser chạy được chưa, chất lượng sơ bộ ra sao, có vấn đề hệ thống rõ ràng không.

Full scan cần thiết để tính tỷ lệ lỗi toàn corpus. Hai lựa chọn:

### 6A. Full streaming không lưu toàn bộ

Phù hợp nếu repository hỗ trợ từng file hoặc range request.

```text
remote record → chunk → stats → append Parquet → discard bytes
```

### 6B. Controlled acquisition vào ZONE 2

Bắt buộc nếu source là monolithic ZIP/archive không thể đọc từng object. Archive chỉ được lưu ở:

```text
/home/duyvd9/massive/projects/myolab-ai-data/external/<dataset>/acquired/
```

Sau khi hash/inventory, giải nén vào `extracted/`. Không copy vào ZONE 1.

**Quyết định phải ghi bằng evidence, không dựa vào cảm giác.**

---

## Bước 7 — Mendeley real EDA completion

**Required output**

```text
ZONE2/external/mendeley-4channel-hand-gesture-v2/evidence/day28/
├── day28-preflight.json
├── metadata-eda-summary.json
├── file-level-statistics.parquet
├── channel-level-statistics.parquet
├── label-audit.csv
├── signal-quality-flags.csv
├── feature-eligibility.yaml
├── experiment-eligibility.yaml
├── eda-and-data-quality-report.md
└── day28-readiness-decision.yaml
```

**Mendeley-specific locks**

- core view có 4 lớp: `rest`, `hand_close`, `wrist_flexion`, `wrist_extension`;
- sáu label non-target nằm trong unknown/audit view;
- `hand_open` không được bịa;
- không fatigue claim;
- không cross-day claim.

---

## Bước 8 — GRABMyo real EDA completion

**Required output**

```text
ZONE2/external/grabmyo-v1.1.0/evidence/day29/
├── day29-preflight.json
├── metadata-eda-summary.json
├── file-level-statistics.parquet
├── channel-level-statistics.parquet
├── subject-day-coverage.csv
├── subject-day-gesture-support.csv
├── cross-day-feature-summary.parquet
├── cross-day-drift-summary.csv
├── cross-day-drift-observations.md
├── feature-eligibility.yaml
├── experiment-eligibility.yaml
├── eda-and-data-quality-report.md
└── day29-readiness-decision.yaml
```

**GRABMyo-specific locks**

- multi-day drift không đồng nghĩa fatigue;
- day/session/electrode variation phải được giữ riêng;
- cross-day summary chỉ dùng train/validation;
- public healthy data không chứng minh Motion Lab transfer.

---

## Bước 9 — Copy evidence nhỏ về ZONE 1

```bash
bash scripts/dev/sync_pre_day30_evidence_to_repo.sh --apply
```

Chỉ copy:

- readiness decisions;
- metadata summary;
- compact CSV/JSON/YAML;
- Markdown report;
- hash ledger.

Không copy:

- raw/acquired/extracted;
- normalized waveform;
- cache;
- large Parquet chứa sample-level signal;
- hàng nghìn PNG.

---

## Bước 10 — Dual gate

```bash
python scripts/data/pre_day30_dual_gate.py \
  --config data-platform/configs/pre_day30_storage.local.yaml \
  --output qa-validation/evidence/pre-day30/pre-day30-dual-gate.json
```

### GO

```yaml
decision: GO_FOR_DAY30_HARMONIZATION
mendeley_real_eda: PASS
grabmyo_real_eda: PASS
test_signal_rows_read: 0
training_allowed: false
```

### BLOCK

```yaml
decision: BLOCKED_WITH_EVIDENCE
blockers:
  - <reason_code>
```

---

## 4. Definition of Done

- [ ] Hai vùng đúng absolute path.
- [ ] ZONE 2 không nằm trong Git worktree.
- [ ] Repo scan không có raw/archive/model lớn.
- [ ] Remote catalog có source provenance.
- [ ] Đã ghi rõ repository có hỗ trợ file-level/range hay không.
- [ ] Mendeley EDA thật hoàn thành hoặc BLOCK có bằng chứng.
- [ ] GRABMyo EDA thật + cross-day audit hoàn thành hoặc BLOCK có bằng chứng.
- [ ] Không đọc sealed test signal.
- [ ] Không training.
- [ ] Không claim fatigue từ day drift.
- [ ] Evidence nhỏ đã đồng bộ về repo.
- [ ] Dual gate tạo quyết định machine-readable.

---

## 5. Handoff Day 30

Day 30 chỉ nhận:

```text
source/license records
remote/acquisition receipts
metadata indexes
label dictionaries
sampling/unit/channel profiles
EDA summaries
feature eligibility
split/test seals
readiness decisions
hashes
```

Day 30 không cần đọc toàn bộ raw signal và không được tạo pooled corpus vật lý.
