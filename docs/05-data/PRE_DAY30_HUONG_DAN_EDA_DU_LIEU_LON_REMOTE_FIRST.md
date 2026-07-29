# Hướng dẫn cực chi tiết: EDA dữ liệu sEMG lớn theo remote-first mà không giữ toàn bộ dataset trên máy

## 0. Điều đầu tiên phải hiểu đúng

Câu “EDA mà không tải dữ liệu về” có hai nghĩa khác nhau:

### Nghĩa không khả thi

```text
Không truyền bất kỳ byte tín hiệu nào
nhưng vẫn tính RMS/MAV/PSD/flatline/clipping trên tín hiệu.
```

Điều này không thể: phép tính phải nhìn thấy các mẫu số.

### Nghĩa khả thi và là mục tiêu của pack

```text
Không tải và không giữ toàn bộ corpus thành một bản sao local.
Chỉ đọc metadata hoặc truyền từng phần cần thiết,
chịu ngân sách cache/RAM, ghi summary rồi giải phóng dữ liệu.
```

Ta tối ưu **data at rest**, RAM và rủi ro; không thể làm network traffic bằng 0 nếu thực sự audit waveform.

---

# Phần I — Mô hình tư duy EDA bốn tầng

## Tầng 0 — Repository/source EDA

Không đọc tín hiệu.

Ta trả lời:

- dataset version nào;
- license gì;
- official source nào;
- có file-level listing không;
- archive nguyên khối hay nhiều object;
- size/ETag/Last-Modified;
- HTTP range có không;
- format nào;
- có metadata subject/day/gesture/repetition ở filename/path không.

**Chi phí:** rất nhỏ.

**Output:** remote catalog.

## Tầng 1 — Structural/metadata EDA

Không cần waveform.

Ta tính:

```text
N subjects
N days
N sessions
N gestures
N repetitions
file sizes
group/class coverage
missing group IDs
duplicate object candidates
```

Đây là tầng quan trọng nhất để phát hiện split/leakage trước khi xử lý tín hiệu.

## Tầng 2 — Bounded sample signal EDA

Ta chọn một sample được stratify và giới hạn bytes.

Mục tiêu:

- parser đúng không;
- cột/kênh/shape đúng không;
- unit/rate có mâu thuẫn không;
- signal có NaN/Inf/flatline/clipping rõ không;
- memory/network profile có khả thi không.

Không dùng sample EDA để kết luận tỷ lệ lỗi toàn corpus.

## Tầng 3 — Full streaming scan

Ta duyệt toàn bộ train/validation record nhưng:

```text
mỗi lần chỉ giữ một chunk/record trong RAM
→ tính sufficient statistics
→ append output
→ giải phóng
```

Nếu remote object listing cho phép, có thể không giữ corpus local. Tuy nhiên tổng network bytes có thể tương đương đọc toàn bộ dataset.

---

# Phần II — Khi nào remote-first thực sự hoạt động?

## Trường hợp A — nhiều file riêng, HTTP range hỗ trợ

Tốt nhất.

```text
catalog → select object → open ranged stream → chunk → stats
```

## Trường hợp B — nhiều file riêng, không có range

Vẫn làm được theo file:

```text
download tạm một file → EDA → xóa/LRU
```

Không giữ toàn corpus, nhưng mỗi file phải truyền toàn bộ.

## Trường hợp C — một ZIP/TAR nguyên khối

### ZIP

ZIP central directory nằm cuối file. Một số seekable HTTP filesystem có thể đọc central directory bằng range request, nhưng đọc member nén có thể vẫn cần nhiều range và phụ thuộc server.

### TAR.GZ/7Z/RAR

Random access thường kém. Có khả năng phải tải gần/toàn archive mới giải nén được member.

### Quyết định đúng

```yaml
remote_signal_eda:
  status: BLOCKED_BY_MONOLITHIC_ARCHIVE
fallback:
  - metadata_only
  - request_individual_files
  - controlled_acquisition_to_zone2
  - run_compute_near_data_if_provider_supports
```

Không viết code giả vờ streaming nếu transport/format không hỗ trợ.

---

# Phần III — Quy trình cụ thể cho hai dataset

## 1. Mendeley 4-channel

Vai trò: sparse 4-channel Task A engineering, core 4 labels, không cross-day và không fatigue.

### Pha M1 — source metadata

ZONE 1 đã có:

- `dataset-source-record.yaml`;
- `license-record.yaml`;
- `label-dictionary.yaml`;
- `canonical-mapping-draft.yaml`.

Copy/chuẩn hóa chúng vào:

```text
ZONE1/data-platform/datasets/external/mendeley-4channel-hand-gesture-v2/
```

### Pha M2 — xác định access topology

Tạo `remote-objects.input.csv`. Nếu repository chỉ cung cấp một archive:

```yaml
access_topology: MONOLITHIC_ARCHIVE
remote_eda_capability:
  metadata: true
  signal_sample: conditional
  full_signal_scan_without_acquisition: false_or_not_verified
```

### Pha M3 — metadata EDA

Không điền sampling rate/unit từ biên độ. Chỉ dùng evidence từ paper/header/file.

### Pha M4 — sample parser verification

Nếu có file riêng: chọn một số subject × 10 gestures × repetitions từ train/validation.

Nếu archive nguyên khối: tải archive một lần vào ZONE 2 là lựa chọn trung thực hơn việc tạo parser remote giả. Tính SHA-256, inventory, giải nén. Đây vẫn đáp ứng kiến trúc hai vùng vì raw không vào Git.

### Pha M5 — full EDA

- đọc từng file;
- không concatenate toàn bộ CSV;
- output Parquet summaries;
- plot stratified sample;
- unknown gestures giữ trong audit view;
- core training view chỉ 4 labels;
- hand_open absent.

## 2. GRABMyo

Vai trò: multi-day robustness, public healthy engineering baseline.

### Pha G1 — catalog file-level

GRABMyo nên được ưu tiên file-level/record-level remote catalog nếu official host cung cấp object listing. Không hard-code path pattern trước khi catalog xác minh.

### Pha G2 — metadata hierarchy

Khóa tối thiểu:

```text
subject_id
day_id
session_id nếu có
source_label
repetition_id
signal object URL
```

### Pha G3 — bounded sample

Sample phải phủ:

- nhiều subject;
- cả ba ngày thực tế nếu catalog xác nhận;
- mọi gesture được chọn cho project subset;
- nhiều repetitions;
- train và validation;
- tuyệt đối không test.

### Pha G4 — cross-day audit

Với cùng subject/gesture/channel hoặc representation:

```text
MAV ratio giữa ngày
RMS ratio giữa ngày
median/MAD shift
MDF/MNF shift nếu eligible
missing support
channel-order consistency
```

Không gọi các shift này là fatigue. Chúng có thể đến từ repositioning, contact, effort, posture hoặc protocol.

---

# Phần IV — Streaming statistics: toán cần hiểu

## 1. Vì sao không tính mean bằng cách giữ toàn bộ vector?

Mean:

\[
\bar{x} = \frac{1}{N}\sum_{i=1}^{N}x_i
\]

Chỉ cần giữ `N` và tổng. Nhưng cộng số lớn trực tiếp có thể kém ổn định; variance càng dễ sai.

## 2. Welford online mean/variance

Với mẫu mới \(x_n\):

\[
\delta = x_n - \mu_{n-1}
\]

\[
\mu_n = \mu_{n-1} + \frac{\delta}{n}
\]

\[
M_{2,n} = M_{2,n-1} + \delta(x_n - \mu_n)
\]

Variance mẫu:

\[
s^2 = \frac{M_2}{n-1}
\]

Bộ nhớ là \(O(1)\) mỗi kênh.

## 3. RMS streaming

\[
RMS = \sqrt{\frac{1}{N}\sum_{i=1}^{N}x_i^2}
\]

Giữ `sum_sq` và `N`.

## 4. MAV streaming

\[
MAV = \frac{1}{N}\sum_{i=1}^{N}|x_i|
\]

Giữ `sum_abs` và `N`.

## 5. Nonfinite ratio

\[
r_{nf}=\frac{N_{NaN}+N_{Inf}}{N}
\]

## 6. Flatline candidate

Một heuristic đơn giản:

\[
r_{flat}=\frac{\#\{|x_i-x_{i-1}|\le \epsilon\}}{N-1}
\]

`epsilon` phải gắn với unit/scale; nếu unit chưa xác minh, chỉ dùng exact-repeat ratio hoặc ghi PROVISIONAL.

## 7. Clipping candidate

Không biết ADC rail thì không được nói “clipping confirmed”. Chỉ có thể báo:

```text
potential_clipping_ratio
= fraction of samples exactly at observed min/max
```

và gắn `warning_only`.

## 8. PSD/MDF/MNF khó streaming hơn

PSD cần window/block. Ta có thể xử lý Welch theo block, nhưng phải biết:

- sampling rate;
- raw vs processed;
- anti-aliasing;
- window length;
- overlap;
- detrending;
- frequency band.

Do đó remote EDA ưu tiên structural/amplitude/QC trước. Frequency features chỉ mở khi `feature_eligibility.frequency_domain=true`.

---

# Phần V — Bộ nhớ, network và disk budget

## 1. RAM

Giả sử chunk có:

```text
100,000 rows × 32 channels × float64
≈ 25.6 MB chưa tính overhead
```

Pandas có overhead lớn hơn. Nên bắt đầu `chunk_rows=25_000` hoặc `50_000`, đo thực tế rồi tăng.

## 2. Disk cache

Cache phải bounded:

```yaml
max_cache_bytes: 10 GiB
high_watermark: 90%
low_watermark_after_eviction: 70%
eviction: LRU
```

## 3. Network ledger

Mỗi run cần ghi:

```text
requested_bytes
transferred_bytes
objects_opened
range_requests
full_object_downloads
cache_hits
cache_misses
```

Nếu thư viện không cung cấp chính xác, ghi `NOT_MEASURED`, không bịa.

## 4. Dung lượng ZONE 2

Nếu cuối cùng buộc phải tải archive:

```text
archive + extracted + normalized + temp + evidence
```

Dự phòng thường 2–3× archive, nhưng phải đo format thực tế. `check_storage_capacity.py` cung cấp estimate, không phải bảo đảm.

---

# Phần VI — Mẫu lệnh vận hành

## 1. Bootstrap

```bash
bash scripts/dev/bootstrap_pre_day30_storage.sh --apply
```

## 2. Kiểm tra repo không chứa raw

```bash
python scripts/data/audit_repo_no_raw_data.py \
  --repo-root /home/duyvd9/massive/projects/semg-fatigue/MyoLab-AI \
  --output qa-validation/evidence/pre-day30/repo-raw-scan.json
```

## 3. Build catalog

```bash
python scripts/data/build_remote_catalog.py \
  --input /home/duyvd9/massive/projects/semg-fatigue/myolab-ai-data/external/grabmyo-v1.1.0/source-metadata/remote-objects.input.csv \
  --output /home/duyvd9/massive/projects/semg-fatigue/myolab-ai-data/external/grabmyo-v1.1.0/remote-catalog/remote-catalog.json
```

## 4. Chọn sample

```bash
python scripts/data/select_remote_sample.py \
  --catalog <catalog.json> \
  --config data-platform/configs/pre_day30_remote_eda.research.yaml \
  --output <sample-plan.json>
```

## 5. EDA

```bash
python scripts/data/streaming_signal_eda.py \
  --plan <sample-plan.json> \
  --output-dir <ZONE2/evidence/dayXX/sample-eda> \
  --mode bounded-sample
```

## 6. Gate

```bash
python scripts/data/pre_day30_dual_gate.py \
  --config data-platform/configs/pre_day30_storage.local.yaml \
  --output qa-validation/evidence/pre-day30/pre-day30-dual-gate.json
```

---

# Phần VII — Các sai lầm cần tránh

1. `wget -r` toàn repository trước khi inventory.
2. Đưa archive/raw vào repo vì đường dẫn tiện.
3. Load toàn bộ CSV/Parquet vào một DataFrame.
4. Dùng notebook làm source of truth.
5. Chạy EDA test set để chọn threshold.
6. Vẽ mọi waveform thành PNG.
7. Suy unit từ magnitude.
8. Suy sampling từ số dòng/duration không đáng tin.
9. Gọi day drift là fatigue.
10. Gộp Mendeley và GRABMyo trước harmonization.
11. Dùng `tooling PASS` thay cho `real EDA PASS`.
12. Giả vờ remote streaming với monolithic archive không hỗ trợ random access.

---

# Phần VIII — Khi nào được sang Day 30?

Chỉ khi cả hai decision machine-readable ghi:

```yaml
real_dataset_or_remote_signal_access_verified: true
real_eda_executed: true
test_set_opened: false
test_signal_rows_read: 0
readiness: GO_FOR_DAY30_HARMONIZATION
```

Nếu chỉ metadata EDA hoặc sample EDA hoàn thành, có thể làm một phần compatibility design nhưng Day 30 full phải là `CONDITIONAL/BLOCKED`.

---

# Phần IX — Runbook thực hành từ máy sạch đến Dual Gate

Phần này mô tả như một buổi bạn tự thao tác. Không bỏ qua bước chỉ vì “đã có code”.

## Bước A — Mở terminal và xác nhận vị trí

```bash
export MYOLAB_REPO=/home/duyvd9/massive/projects/semg-fatigue/MyoLab-AI
export MYOLAB_DATA=/home/duyvd9/massive/projects/semg-fatigue/myolab-ai-data

realpath "$MYOLAB_REPO"
realpath "$MYOLAB_DATA" 2>/dev/null || true
```

Kỳ vọng:

```text
/home/duyvd9/massive/projects/semg-fatigue/MyoLab-AI
/home/duyvd9/massive/projects/semg-fatigue/myolab-ai-data
```

Kiểm tra quan hệ cha-con:

```bash
python - <<'PY'
from pathlib import Path
repo = Path('/home/duyvd9/massive/projects/semg-fatigue/MyoLab-AI').resolve()
data = Path('/home/duyvd9/massive/projects/semg-fatigue/myolab-ai-data').resolve()
print('repo=', repo)
print('data=', data)
print('data_inside_repo=', repo in data.parents)
print('repo_inside_data=', data in repo.parents)
PY
```

Cả hai giá trị cuối phải `False`.

## Bước B — Kiểm tra dung lượng và filesystem

```bash
df -h "$MYOLAB_REPO"
df -h "$(dirname "$MYOLAB_DATA")"
df -T "$MYOLAB_REPO"
df -T "$(dirname "$MYOLAB_DATA")"
```

Bạn cần ghi lại:

```yaml
filesystem_type: ext4_or_other
free_space_before: <value>
mount_point: <value>
```

Tại sao? Nếu cache và repo ở cùng partition, dù tách thư mục, chúng vẫn tranh cùng dung lượng. Hai vùng tách về governance nhưng chưa chắc tách vật lý.

## Bước C — Tạo virtual environment riêng

Không cài package vào Python hệ thống của máy công ty.

```bash
cd "$MYOLAB_REPO"
python3 -m venv .venv-pre-day30
source .venv-pre-day30/bin/activate
python -m pip install --upgrade pip
python -m pip install -r environment/requirements-pre-day30.txt
```

Kiểm tra:

```bash
python - <<'PY'
import numpy, pandas, fsspec, requests, yaml
print('numpy', numpy.__version__)
print('pandas', pandas.__version__)
print('fsspec', fsspec.__version__)
print('requests', requests.__version__)
print('yaml', yaml.__version__)
PY
```

Không dùng version từ output này để sửa environment lock chính thức một cách tự động. Đây mới là environment thực thi EDA, cần được capture sau.

## Bước D — Bootstrap hai vùng

```bash
bash scripts/dev/bootstrap_pre_day30_storage.sh --dry-run
bash scripts/dev/bootstrap_pre_day30_storage.sh --apply
```

Sau đó:

```bash
find "$MYOLAB_DATA" -maxdepth 3 -type d | sort
```

Bạn phải hiểu vì sao từng directory tồn tại; không tạo folder chỉ để “đẹp skeleton”.

## Bước E — Tạo retrieval receipt trước khi lấy URL file

Ví dụ tại:

```text
$MYOLAB_DATA/external/grabmyo-v1.1.0/source-metadata/retrieval-receipt.yaml
```

Nội dung mẫu:

```yaml
schema_version: retrieval-receipt.v1
dataset_id: grabmyo-v1.1.0
source_record_id: <hash-or-reference>
source_landing_page: <official-url>
retrieved_at: <ISO-8601>
operator: Duy
mode: REMOTE_METADATA_ONLY
credentials_used: false
accepted_terms: <true|false|not_required>
notes:
  - No signal body downloaded in this step.
```

Receipt khác archive hash. Receipt chứng minh bạn đã lấy danh sách từ nguồn nào, lúc nào, theo điều khoản nào.

## Bước F — Điền `remote-objects.input.csv`

Mỗi hàng là một **logical signal object**, không phải mỗi chunk mạng.

Ví dụ:

```csv
record_id,url,official_source,format,size_bytes,partition,subject_id,day_id,session_id,repetition_id,source_label,channel_columns,sampling_rate_hz,unit,notes
GRAB-S001-D01-G01-R01,<official-file-url>,true,csv,,train,S001,D01,,R01,<verified-label>,"",2048,,Need channel inspection
```

### Chưa biết partition thì làm gì?

Không để script tự random split từng file sau khi đã đọc waveform. Quy trình đúng:

1. Xây hierarchy từ metadata.
2. Freeze group keys.
3. Tạo split manifest bằng subject/day policy.
4. Join partition trở lại remote object catalog.
5. Seal test IDs.
6. Sau đó mới signal EDA.

Nếu chưa split, dùng:

```text
partition=UNASSIGNED
```

và sample selector phải block. Không đổi `UNASSIGNED` thành `train` cho tiện.

### Chưa biết channel columns?

Để rỗng và chỉ chạy catalog/metadata EDA. `streaming_signal_eda.py` sẽ báo `CHANNEL_COLUMNS_REQUIRED_FOR_CSV`. Đây là đúng vì parser chưa đủ contract.

## Bước G — HEAD audit

```bash
python scripts/data/build_remote_catalog.py \
  --input "$MYOLAB_DATA/external/grabmyo-v1.1.0/source-metadata/remote-objects.input.csv" \
  --output "$MYOLAB_DATA/external/grabmyo-v1.1.0/remote-catalog/remote-catalog.json"
```

Đọc output bằng:

```bash
python - <<'PY'
import json
p='/home/duyvd9/massive/projects/semg-fatigue/myolab-ai-data/external/grabmyo-v1.1.0/remote-catalog/remote-catalog.json'
d=json.load(open(p))
print(json.dumps(d['summary'], indent=2))
for r in d['records'][:5]:
    print(r['record_id'], r['head_status'], r.get('size_bytes'), r.get('accept_ranges'))
PY
```

### Diễn giải

| Kết quả | Ý nghĩa | Hành động |
|---|---|---|
| `HTTP_200`, range=true | tốt cho seek/chunk | thử bounded sample |
| `HTTP_200`, range=false | file-level tạm tải | cache object có giới hạn |
| `HTTP_403` | cần auth/terms/header | không bypass; cập nhật access workflow |
| `HTTP_404` | URL stale/sai | sửa catalog từ official listing |
| size=null | server không trả length | không dùng để estimate budget; vẫn có thể thử |
| redirect sang login HTML | không phải signal object | block |

Bạn nên kiểm tra `content_type`. Nếu mong CSV nhưng server trả `text/html`, rất có thể đang tải trang login/error.

## Bước H — Hash catalog

```bash
sha256sum "$MYOLAB_DATA/external/grabmyo-v1.1.0/remote-catalog/remote-catalog.json" \
  > "$MYOLAB_DATA/external/grabmyo-v1.1.0/remote-catalog/remote-catalog.sha256"
```

Mọi sample plan phải ghi hash catalog. Phiên bản script hiện tạo plan hash; khi tích hợp production, thêm catalog hash thành required field.

## Bước I — Metadata summary bằng SQL/Polars/Pandas

Với catalog chỉ vài nghìn dòng, pandas đủ. Không cần Spark.

```python
import json
import pandas as pd

catalog = json.load(open('remote-catalog.json'))
df = pd.DataFrame(catalog['records'])

print(df.groupby(['partition', 'source_label']).size())
print(df.groupby(['subject_id', 'day_id']).size())
print(df['size_bytes'].describe())
```

Đừng nhầm số file với số repetition nếu một repetition có nhiều file/modalities.

## Bước J — Tạo split/test seal trước waveform

Một split manifest tối thiểu:

```yaml
schema_version: group-split.v1
dataset_id: grabmyo-v1.1.0
group_unit: subject_id
secondary_audit_unit: day_id
seed: 302026
train_subjects: [...]
validation_subjects: [...]
test_subjects: [...]
created_before_signal_eda: true
```

Test seal:

```yaml
schema_version: test-seal.v1
split_manifest_sha256: <hash>
opened: false
signal_rows_read: 0
owner: Duy
```

Code EDA không được có chế độ `--include-test-for-completeness`.

## Bước K — Chọn sample

```bash
python scripts/data/select_remote_sample.py \
  --catalog "$MYOLAB_DATA/external/grabmyo-v1.1.0/remote-catalog/remote-catalog.json" \
  --config data-platform/configs/pre_day30_remote_eda.research.yaml \
  --output "$MYOLAB_DATA/external/grabmyo-v1.1.0/metadata/bounded-sample-plan.json"
```

Kiểm tra:

```bash
python - <<'PY'
import json
p='/home/duyvd9/massive/projects/semg-fatigue/myolab-ai-data/external/grabmyo-v1.1.0/metadata/bounded-sample-plan.json'
d=json.load(open(p))
assert d['test_signal_records_selected'] == 0
print('records', d['selected_record_count'])
print('known bytes', d['selected_known_bytes'])
print('sha256', d['plan_sha256'])
PY
```

## Bước L — Chạy sample EDA với checkpoint

```bash
python scripts/data/streaming_signal_eda.py \
  --plan "$MYOLAB_DATA/external/grabmyo-v1.1.0/metadata/bounded-sample-plan.json" \
  --output-dir "$MYOLAB_DATA/external/grabmyo-v1.1.0/evidence/day29/sample-eda" \
  --mode bounded-sample \
  --chunk-rows 50000
```

Script hiện ghi JSONL từng record. Ưu điểm:

- crash sau record 150 vẫn còn 149 kết quả;
- append/inspect dễ;
- không giữ toàn summary trong RAM.

Khi tích hợp thật, thêm resume ledger:

```text
record_id → status → output hash
```

để rerun bỏ qua record đã PASS cùng config/catalog hash.

## Bước M — Đọc và triage lỗi

```bash
python - <<'PY'
import json
from collections import Counter
p='/home/duyvd9/massive/projects/semg-fatigue/myolab-ai-data/external/grabmyo-v1.1.0/evidence/day29/sample-eda/record-statistics.jsonl'
statuses=Counter()
errors=Counter()
for line in open(p):
    r=json.loads(line)
    statuses[r['status']]+=1
    if r['status']=='ERROR': errors[r['error']]+=1
print(statuses)
print(errors.most_common(10))
PY
```

Không sửa parser để “nuốt lỗi” chung. Phân loại:

- format mismatch;
- channel mapping missing;
- auth/access;
- corrupted object;
- unsupported compression;
- source metadata conflict.

## Bước N — Full scan hay controlled download?

Dùng decision table:

| Điều kiện | Quyết định |
|---|---|
| file-level + range + parser PASS | full streaming khả thi |
| file-level no range, từng file nhỏ | bounded local cache |
| file-level no range, file cực lớn | cân nhắc download một lần hoặc compute near data |
| monolithic archive | controlled acquisition hoặc block |
| access gated/DUA | hoàn tất governance trước |
| format unsupported | thêm adapter sau khi xác minh format |

### “Compute near data” nghĩa là gì?

Chạy code trên VM/notebook/server ở gần object storage của nhà cung cấp, chỉ tải summary về. Chỉ dùng nếu provider chính thức hỗ trợ và governance cho phép. Không đưa credential vào repo.

## Bước O — Chuyển JSONL summary sang Parquet

```python
import json
import pandas as pd

rows=[]
for line in open('record-statistics.jsonl'):
    record=json.loads(line)
    if record['status']!='PASS':
        continue
    for channel, stats in record['channels'].items():
        rows.append({
            'record_id': record['record_id'],
            'subject_id': record.get('subject_id'),
            'day_id': record.get('day_id'),
            'source_label': record.get('source_label'),
            'channel': channel,
            **stats,
        })
pd.DataFrame(rows).to_parquet('channel-level-statistics.parquet', index=False)
```

Parquet này nằm ZONE 2. Chỉ copy compact aggregate CSV/JSON vào ZONE 1.

## Bước P — Tạo plots có kiểm soát

Không plot toàn bộ. Tạo plot manifest trước:

```yaml
plot_manifest:
  seed: 302026
  selected_record_ids:
    - ...
  selection_rule: stratified_subject_day_label
  max_plots: 100
```

Mỗi plot phải hiện:

- dataset;
- subject/day/gesture/repetition;
- channel;
- sampling/unit status;
- raw/processed state;
- partition (không phải test);
- source object hash/ref.

## Bước Q — Cross-day GRABMyo

Sau khi có channel-level stats:

```python
import pandas as pd

df=pd.read_parquet('channel-level-statistics.parquet')
keys=['subject_id','source_label','channel']
pivot=df.pivot_table(index=keys, columns='day_id', values='rms', aggfunc='median')
```

Báo ratio/log-ratio nhưng không gọi fatigue:

\[
\Delta_{d_2,d_1}=\log\frac{RMS_{d_2}+\epsilon}{RMS_{d_1}+\epsilon}
\]

Dùng log-ratio vì ratio đối xứng hơn trên thang log. `epsilon` phải nhỏ và được versioned; không chọn sau khi nhìn test.

## Bước R — Readiness decisions

Mendeley:

```yaml
status: GO_FOR_DAY30_HARMONIZATION
real_eda_executed: true
test_set_opened: false
test_signal_rows_read: 0
core_classes_verified:
  - rest
  - hand_close
  - wrist_flexion
  - wrist_extension
hand_open_supported: false
```

GRABMyo:

```yaml
status: GO_FOR_DAY30_HARMONIZATION
real_eda_executed: true
cross_day_audit_completed: true
test_set_opened: false
test_signal_rows_read: 0
fatigue_inference_allowed: false
```

## Bước S — Sync evidence nhỏ

```bash
bash scripts/dev/sync_pre_day30_evidence_to_repo.sh --dry-run
bash scripts/dev/sync_pre_day30_evidence_to_repo.sh --apply
```

Sau sync:

```bash
git status --short
python scripts/data/audit_repo_no_raw_data.py \
  --repo-root "$MYOLAB_REPO" \
  --output qa-validation/evidence/pre-day30/repo-raw-scan.json
```

Review từng file trước `git add`.

## Bước T — Dual Gate

```bash
python scripts/data/pre_day30_dual_gate.py \
  --config data-platform/configs/pre_day30_storage.local.yaml \
  --output qa-validation/evidence/pre-day30/pre-day30-dual-gate.json
```

Không sửa JSON output bằng tay để biến BLOCK thành GO. Sửa upstream evidence và chạy lại.

---

# Phần X — Format support matrix và chiến lược mở rộng adapter

| Format | Remote metadata | Remote signal | Lưu ý |
|---|---:|---:|---|
| CSV/TXT | tốt | chunk streaming tốt | cần delimiter/header/channel contract |
| NPY | tốt | seekable/range có thể tốt | header + contiguous array; remote library behavior cần test |
| NPZ | tốt | conditional | ZIP container; member access phụ thuộc seek/range |
| Parquet | rất tốt | tốt nếu server range + row groups | phù hợp summary/index hơn raw waveform |
| Zarr | rất tốt | rất tốt | chunk/object based; cần source thật dùng Zarr |
| HDF5/MAT v7.3 | tốt | conditional | h5py cần seekable file; chunk layout ảnh hưởng |
| MAT cũ | metadata hạn chế | thường cần file local/seek | scipy loader có thể cần cả object |
| WFDB DAT/HEA | tốt | tốt nếu adapter hỗ trợ URL/local cache | cần xác minh record pairs và library behavior |
| C3D | metadata conditional | thường tải object/seek | dùng ezc3d sau khi source format xác minh |
| ZIP/TAR.GZ | listing conditional | kém đến conditional | monolithic archive risk |

Pack chỉ implement CSV và NPY để giữ code trung thực, nhỏ và kiểm thử được. Không thêm MAT/WFDB/C3D trước khi bạn xác minh format thực tế của từng dataset.

---

# Phần XI — Checklist tự đánh giá sau khi học

Bạn phải tự trả lời được:

1. Tại sao metadata EDA có thể làm mà không tải signal body?
2. Vì sao full streaming scan vẫn có thể truyền gần toàn bộ bytes?
3. Vì sao `Accept-Ranges` quan trọng?
4. Khi nào cache khác acquired source?
5. Vì sao Mendeley archive nguyên khối có thể buộc controlled acquisition?
6. Vì sao không dùng test trong EDA chất lượng?
7. Vì sao GRABMyo cross-day shift không phải fatigue?
8. Welford giúp giảm memory như thế nào?
9. Vì sao exact median khó streaming hơn mean?
10. Vì sao Parquet phù hợp cho summary nhưng không mặc định là format raw tốt nhất?
11. Artifact nào là SSOT ở ZONE 1 và artifact nào ở ZONE 2?
12. Tại sao tooling PASS không đồng nghĩa real EDA PASS?
