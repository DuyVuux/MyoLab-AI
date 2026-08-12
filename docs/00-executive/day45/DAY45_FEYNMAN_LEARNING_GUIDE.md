# DAY45 FEYNMAN LEARNING GUIDE — Data Lineage, Processing Manifests & Reproducible DSP

## 1. Hôm nay đang giải bài toán gì?

Hãy tưởng tượng bạn nhìn thấy một vector sEMG đã xử lý và một con số RMS ở ngày mai. Nếu chỉ có vector đó, bạn chưa biết:

- nó đến từ file raw nào;
- có đúng channel/window hay không;
- filter nào đã chạy;
- filter chạy bằng code version nào;
- notch 50 Hz là do site thật xác nhận hay chỉ do một fixture synthetic;
- đoạn missing đã bị xóa hay vẫn được mask;
- normalization reference có hợp lệ không;
- có ai vô tình dùng locked evaluation để fit parameter không.

DAY45 giải bài toán **provenance**: mọi processed artifact phải có một “gia phả” đủ chính xác để replay và audit.

Một câu ngắn nhất:

> **A processed signal without provenance is just an array; a processed signal with an unbroken manifest is an evidence-bearing artifact.**

---

## 2. Analogy — hộ chiếu của một processed waveform

Raw signal giống nguyên liệu có số lô. Processing giống một chuỗi nhà máy. Nếu sản phẩm cuối bị lỗi, ta cần biết:

```text
lô nguyên liệu nào
→ máy nào
→ công thức nào
→ thứ tự công đoạn nào
→ thông số nào
→ output từng công đoạn nào
```

`ProcessingManifest` chính là hộ chiếu đó.

Nếu chỉ ghi:

```text
"filtered = true"
```

thì gần như vô dụng.

Nếu ghi:

```text
source_id = src_sha256_...
window_id = qcw_...
processor = DAY41_BANDPASS
version = day41-bandpass.v0.1.0
method = butterworth_sos
low_cut = 20
high_cut = 400
order = 4
phase = ZERO_PHASE
input_hash = ...
output_hash = ...
```

thì ta có thể tái tạo và kiểm tra.

---

## 3. Ba loại identity khác nhau

### 3.1 Source identity

DAY11 dùng:

```text
source_id = src_sha256_<SHA256 exact source bytes>
```

Nó trả lời:

> Đây có đúng raw source byte-for-byte không?

### 3.2 Processing run identity

DAY45 dùng:

```text
processing_run_id = prun_sha256_<canonical execution request>
```

Nó trả lời:

> Đây có phải cùng một yêu cầu processing không?

### 3.3 Processed artifact identity

DAY45 dùng:

```text
artifact_id = part_sha256_<run + output hash + mask hash + count + unit>
```

Nó trả lời:

> Đây có đúng processed result này không?

Không nên dùng một ID cho cả ba câu hỏi vì semantics khác nhau.

---

## 4. Vì sao content-addressed identity tốt?

Một random UUID có thể unique, nhưng không chứng minh nội dung.

Ví dụ:

```text
UUID A = request 20–400 Hz
UUID B = request 20–400 Hz y hệt
```

Ta không tự biết hai request giống nhau.

Với content address:

\[
ID = \mathrm{SHA256}(\mathrm{CanonicalJSON}(facts))
\]

Nếu `facts` giống hệt:

\[
ID_1 = ID_2
\]

Nếu chỉ một parameter thay đổi:

\[
ID_1 
e ID_2
\]

Điều này rất hữu ích cho reproducibility và idempotency.

---

## 5. Canonical serialization là gì?

Hash một dictionary trực tiếp có thể nguy hiểm nếu thứ tự key khác nhau:

```json
{"a": 1, "b": 2}
```

và:

```json
{"b": 2, "a": 1}
```

về nghĩa là giống nhau.

DAY45 canonicalize bằng:

- keys sorted;
- separators cố định;
- UTF-8;
- no NaN serialization;
- dataclass/enum được đổi về primitive representation.

Sau đó mới SHA-256.

---

## 6. Hash lineage là gì?

Giả sử có bốn step:

```text
Raw → Bandpass → Notch → Mask → Envelope
```

Đặt:

\[
h_0 = H(raw)
\]

Bandpass record:

\[
input = h_0, \quad output = h_1
\]

Notch:

\[
input = h_1, \quad output = h_2
\]

Mask:

\[
input = h_2, \quad output = h_3
\]

Envelope:

\[
input = h_3, \quad output = h_4
\]

Final artifact phải có:

\[
output\_hash = h_4
\]

Nếu Notch record nói input là `x != h1`, lineage bị đứt. Không được bỏ qua chỉ vì output nhìn vẫn hợp lý.

---

## 7. Tại sao hash mask riêng?

Hai processed waveforms có thể gần giống nhau về numeric values nhưng khác validity mask.

Ví dụ:

```text
Signal A: sample 100–110 masked
Signal B: không masked
```

Nếu downstream RMS chỉ nhìn values sau `nanmean` chẳng hạn, kết quả có thể khác semantics rất lớn.

Do đó DAY45 theo dõi:

```text
input_mask_sha256
output_mask_sha256
```

cho từng step.

Mask là một phần của evidence, không chỉ là helper array.

---

## 8. Mask-not-delete quan trọng ra sao?

DAY43 đã khóa:

```text
MASK_NOT_DELETE
```

Nếu 50 samples xấu:

Sai:

```text
xóa 50 samples
→ signal ngắn đi
→ time axis thay đổi ngầm
```

Đúng trong current contract:

```text
mask 50 samples
→ giữ sample index
→ output vẫn cùng length
→ giá trị unavailable là NaN
```

Điều này giữ alignment với event, channel khác và future multimodal data.

---

## 9. Raw immutability khác processed reproducibility thế nào?

**Raw immutability:** raw không đổi.

\[
H(raw_{before}) = H(raw_{after})
\]

**Processed reproducibility:** cùng raw + config + code → cùng processed output trong declared semantics.

\[
F(raw, config, code) = output
\]

Hai khái niệm liên quan nhưng không giống nhau.

Một pipeline có thể không mutate raw nhưng vẫn non-deterministic. Hoặc deterministic nhưng lại overwrite raw. Cả hai đều không đạt.

---

## 10. Config fingerprint dùng để làm gì?

Tên profile không đủ.

Ví dụ hai người đều gọi:

```text
research-filter-v1
```

nhưng một người đổi cutoff từ 400 thành 450 Hz.

Nếu không hash config, tên vẫn y hệt.

DAY45 convergence recipe có fingerprint:

```text
precipe_sha256_07dfd4b38537be69dd6d6435c92a1923f1b928a095f5de385cbb83bc1b9d7401
```

Bất kỳ thay đổi semantic nào trong recipe phải làm fingerprint thay đổi.

---

## 11. Code hash dùng để làm gì nếu đã có version?

Version string có thể bị quên bump.

Ví dụ:

```text
version = day41-bandpass.v0.1.0
```

nhưng file code đã sửa.

`artifact_sha256` giúp phát hiện:

```text
same label ≠ same bytes
```

Best practice là có cả:

```text
human-readable version
+
content hash
```

---

## 12. Event sourcing ở DAY45 có nghĩa gì?

DAY45 chưa xây event store. Nó chỉ định nghĩa event semantics.

Ví dụ:

```text
PROCESSING_STARTED
PROCESSING_COMPLETED
PROCESSING_FAILED
REPROCESS_TRIGGERED
```

Event trả lời:

> Điều gì đã xảy ra trong workflow?

Manifest trả lời:

> Exact processing evidence của một run là gì?

Event và manifest liên quan nhưng không phải cùng artifact.

---

## 13. Vì sao không nhét waveform vào event?

Event store có thể được dùng cho:

- audit;
- workflow reconstruction;
- process mining;
- KPI;
- future interaction learning.

Nếu nhét waveform vào event:

- storage phình lớn;
- privacy surface tăng;
- duplication raw data;
- khó retention/governance;
- event replay trở thành data lake trá hình.

Do đó event chỉ reference:

```text
source_id
processing_run_id
manifest_id
profile fingerprint
reason code
```

Waveform ở data layer, không ở event.

---

## 14. Correlation ID khác processing run ID

`processing_run_id` là content identity.

`correlation_id` là workflow grouping identity.

Ví dụ một session có:

```text
import
→ QC
→ process
→ reprocess
→ metric
```

nhiều operation IDs khác nhau có thể cùng correlation ID.

Điều này giúp DAY53/86 reconstruct process mà không trộn identity semantics.

---

## 15. Failure semantics — tại sao null quan trọng?

Nếu processing fail, nguy hiểm nhất là vẫn có một object nhìn như thành công:

```json
{"status":"FAILED","processed_fs":2000,"output_hash":"..."}
```

Người downstream có thể vô tình dùng `output_hash`.

DAY45 v0.1 chọn shape rõ:

```text
FAILED:
  final_artifact = null
  processed_fs_hz = null
  output_units = null
  steps = []
  reason_codes = non-empty
```

Không ambiguous.

---

## 16. Tại sao FAILED manifest không lưu partial completed steps?

Về mặt observability, lưu partial steps có thể hữu ích. Nhưng ở v0.1 nó làm shape phức tạp:

```text
failed nhưng có output giữa chừng
```

và downstream có thể hiểu nhầm.

DAY45 chọn contract đơn giản, fail-closed trước. Nếu sau này cần partial trace, nên thêm một schema version mới hoặc `attempt_trace` riêng.

Đây là ví dụ của engineering principle:

> Simple safety boundary trước, richer observability sau khi có use case thật.

---

## 17. Reprocess khác retry

**Retry exact request:**

```text
same source + same window + same profile + same code
→ same processing_run_id
```

**Reprocess:**

có intent rằng đây là processing generation mới liên quan run cũ:

```text
reprocess_of_run_id = old_run
```

Nó tạo content identity mới vì parent link là một fact mới.

---

## 18. DAY41 ZERO_PHASE và realtime

DAY41 reference research filter có:

```text
phase_mode = ZERO_PHASE
```

`filtfilt` dùng future samples nên acausal.

Điều đó phù hợp offline research nhưng không realtime.

DAY45 manifest phải ghi effect/timing metadata; provenance không biến acausal filter thành realtime-compatible.

---

## 19. DAY42 notch và site mains

Reference convergence uses explicit 50 Hz only trong synthetic context.

Đây là khác biệt quan trọng:

```text
explicit synthetic 50 Hz
≠
site mains verified 50 Hz
```

Provenance giúp sau này nhìn manifest và biết config authority từ đâu.

Không được biến reference recipe thành site default.

---

## 20. DAY44 normalization và leakage

Normalization dễ gây leakage vì reference có thể đến từ:

- same evaluation subject;
- locked partition;
- incompatible protocol;
- incompatible domain;
- wrong unit.

DAY44 đã tách eligibility khỏi computation.

DAY45 chỉ record eligibility reference; không fit hay normalize.

Điều này bảo vệ nguyên tắc:

```text
No valid reference → no normalized value
```

---

## 21. Worked Example 1 — exact retry

Input execution facts A:

```text
source S
window W
recipe R
code C
input hash X
mask hash M
Fs 2000
unit uV
```

Run ID:

\[
P_1 = H(S,W,R,C,X,M,2000,uV)
\]

Chạy lại y hệt:

\[
P_2 = H(S,W,R,C,X,M,2000,uV)
\]

Kết quả:

\[
P_1 = P_2
\]

DAY45 unit test kiểm điều này.

---

## 22. Worked Example 2 — đổi filter config

Đổi recipe fingerprint:

```text
20–400 Hz → 20–350 Hz
```

Ngay cả source/window giống nhau:

\[
P_{old} 
e P_{new}
\]

Nếu ID không đổi, provenance design bị lỗi vì hai processing requests khác nhau bị collapse.

---

## 23. Worked Example 3 — mask thay đổi

Trước metadata mask:

```text
M0 = all false
```

Sau mask:

```text
M1[1800:1850] = true
```

Manifest cần:

```text
METADATA_MASK.input_mask_hash  = H(M0)
METADATA_MASK.output_mask_hash = H(M1)
```

Envelope phải có:

```text
Envelope.input_mask_hash = H(M1)
Envelope.output_mask_hash = H(M1)
```

Nếu Envelope ghi input mask là `H(M0)`, lineage bị reject.

---

## 24. Counterexample — chỉ lưu final output hash

Giả sử chỉ lưu:

```text
raw_hash
final_hash
```

Nếu output sai, bạn không biết:

- band-pass sai;
- notch sai;
- mask sai;
- smoothing sai.

Step hash chain cho phép localization.

---

## 25. Counterexample — event chứa local path

Sai:

```json
{"source_path":"LOCAL_PATH_WITH_IDENTIFIER"}
```

Vấn đề:

- không portable;
- có thể chứa định danh;
- path thay đổi giữa máy;
- không phải immutable identity.

Đúng:

```json
{"source_refs":["src_sha256_..."]}
```

---

## 26. Counterexample — FAILED nhưng có output

Sai:

```text
status = FAILED
output_hash = abc...
```

Một consumer bất cẩn có thể tiếp tục dùng output.

DAY45 reject shape này.

---

## 27. Common Mistakes

1. Dùng filename làm source identity.
2. Dùng UUID random làm run identity khi cần exact replay.
3. Hash config nhưng không canonicalize.
4. Chỉ hash final output, không hash từng step.
5. Quên hash mask.
6. Version code nhưng không content-hash code.
7. Lưu source path vào event.
8. Lưu waveform vào event store.
9. Cho FAILED manifest chứa artifact.
10. Gọi reprocess là retry mà không giữ parent relation.
11. Copy research filter settings thành site default.
12. Fit normalization trên evaluation data.
13. Dùng `0` thay null/unavailable.
14. Xóa masked samples rồi vẫn claim grid unchanged.
15. Nghĩ provenance = explainability lâm sàng. Provenance chỉ chứng minh technical lineage.

---

## 28. Cách kiểm chứng implementation

### A. Identity tests

- same facts → same run ID;
- changed profile → different run ID;
- source ID/hash mismatch → reject.

### B. Lineage tests

- break step input hash → reject;
- break config hash → reject;
- break mask hash → reject;
- final artifact != final step → reject.

### C. Failure tests

- failed manifest artifact → reject;
- failed event without reason → reject.

### D. Event tests

- deterministic event ID;
- invalid source path reference → reject;
- duplicate event ID in reference sink → reject.

### E. Integrated test

Run actual DAY41–43 processors and DAY44 eligibility, then build one manifest from their metadata and hashes.

---

## 29. What not to learn too deeply today

Không cần đi sâu:

- Kafka internals;
- distributed event sourcing consensus;
- enterprise lineage platform;
- blockchain provenance;
- cryptographic signatures/PKI;
- production event retention architecture;
- full DAG orchestration systems.

DAY45 cần content-addressed provenance v0.1 rõ, testable, đủ cho Phase 3R.

---

## 30. Flashcards

1. **Q:** Source ID đại diện gì?  
   **A:** Exact raw source bytes.

2. **Q:** Processing run ID đại diện gì?  
   **A:** Exact processing request facts.

3. **Q:** Artifact ID đại diện gì?  
   **A:** Exact processed output artifact within a run.

4. **Q:** Vì sao hash mask?  
   **A:** Mask thay đổi data validity semantics.

5. **Q:** `FAILED` có final artifact không?  
   **A:** Không trong DAY45 v0.1.

6. **Q:** Event có waveform không?  
   **A:** Không.

7. **Q:** Persistent event store có chưa?  
   **A:** Chưa; target DAY53.

8. **Q:** Same retry có same run ID không?  
   **A:** Có nếu facts giống hệt.

9. **Q:** Reprocess có parent relation không?  
   **A:** Có qua `reprocess_of_run_id`.

10. **Q:** Site binding DAY45?  
    **A:** null / NOT_VERIFIED.

11. **Q:** Numeric normalization DAY45?  
    **A:** Không.

12. **Q:** Locked fitting?  
    **A:** Forbidden.

13. **Q:** Raw mutation?  
    **A:** Forbidden.

14. **Q:** Acausal filter có thành realtime vì có manifest không?  
    **A:** Không.

15. **Q:** Provenance có chứng minh clinical correctness không?  
    **A:** Không.

16. **Q:** Config hash mismatch nghĩa gì?  
    **A:** Recorded parameters không khớp config identity.

17. **Q:** Broken step hash chain xử lý thế nào?  
    **A:** Manifest invalid/fail closed.

18. **Q:** Local source path có portable identity không?  
    **A:** Không.

19. **Q:** Output unit phải có ở completed manifest không?  
    **A:** Có.

20. **Q:** Failed manifest có processed Fs không?  
    **A:** Không.

---

## 31. Exercises

### Beginner 1

Cho raw hash `A`, band-pass output `B`, notch input `C`. Nếu `B != C`, manifest có valid không? Giải thích.

### Beginner 2

Tại sao `filename=trial1.csv` không đủ làm source identity?

### Beginner 3

Nêu ba field không được đưa vào processing event.

### Intermediate 1

Thiết kế identity cho một reprocess run dùng cùng source/window nhưng profile mới. Những field nào phải thay đổi?

### Intermediate 2

Một step giữ waveform values y hệt nhưng đổi mask. Output hash waveform không đổi. Tại sao manifest vẫn phải coi result semantics khác?

### Integration Exercise

Cho pipeline:

```text
raw → bandpass → mask → RMS
```

Hãy mô tả minimum provenance DAY45 + DAY46 cần để chứng minh RMS không sử dụng masked window.

---

## 32. Quiz

1. `processing_run_id` có phụ thuộc emitted timestamp không?
2. Vì sao?
3. `manifest_id` khác run ID ở đâu?
4. Khi nào final artifact được phép non-null?
5. `config_sha256` được tính từ gì?
6. `source_id` phải quan hệ thế nào với source SHA?
7. Nếu `is_resampled=false` nhưng Fs thay đổi thì sao?
8. Event nào là terminal success?
9. Event nào chỉ thể hiện intent reprocess?
10. DAY45 có persistent event store chưa?
11. Tại sao event không lưu waveform?
12. DAY45 có chạy MVC normalization không?
13. 50 Hz reference notch có chứng minh site mains 50 Hz không?
14. Có được fit trên benchmark-locked không?
15. Broken mask chain có invalidate manifest không?

### Answers

1. Không.
2. Timestamp không phải semantic execution fact; nếu phụ thuộc timestamp exact retry mất deterministic identity.
3. Run ID định danh request; manifest ID định danh semantic record/outcome.
4. Chỉ `COMPLETED`.
5. Canonical explicit step parameters.
6. `source_id = src_sha256_<source sha256>`.
7. Reject vì grid changed without declaration.
8. `PROCESSING_COMPLETED`.
9. `REPROCESS_TRIGGERED`.
10. Chưa.
11. Privacy, duplication, event-store scope và portability.
12. Không.
13. Không.
14. Không.
15. Có.

---

## 33. Readiness Check

Bạn sẵn sàng sang DAY46 nếu có thể tự giải thích:

1. Source ID, processing run ID, manifest ID và artifact ID khác nhau thế nào.
2. Vì sao step hash chain và mask hash chain đều cần thiết.
3. Vì sao failed manifest phải không có processed-looking artifact.
4. Vì sao event store không nên chứa waveform.
5. Vì sao `RESEARCH_ONLY` provenance không tạo clinical claim.
6. DAY46 phải dùng manifest thế nào để RMS/MAV trace về raw source/window/profile.

Nếu chưa trả lời được sáu câu này, nên đọc lại sections 3–18 trước khi triển khai metrics.


---

## 34. Deep Dive — provenance không phải là “log cho có”

Một log text kiểu:

```text
Applied bandpass successfully
```

chỉ cho biết một hành động được báo là đã xảy ra. Nó không đủ để chứng minh input/output nào liên quan. Provenance mạnh hơn log vì nó chứa machine-checkable identities và relationships.

Có thể xem ba mức như sau:

```text
Log:       "Bandpass ran"
Metadata:  "Bandpass 20–400 Hz ran on channel 1"
Provenance:"Input hash A, mask M, code C, params P produced output hash B"
```

Mức cuối mới đủ cho reproducible evidence chain.

---

## 35. Deep Dive — SHA-256 chứng minh gì và không chứng minh gì?

SHA-256 giúp trả lời:

> Hai nội dung có byte representation giống nhau không, với xác suất collision thực tế cực nhỏ?

Nó **không** tự chứng minh:

- ai tạo dữ liệu;
- người đó có quyền tạo hay không;
- dữ liệu clinically correct;
- file không bị thay trước lần hash đầu tiên;
- actor đã được authenticated;
- timestamp là legally trusted.

Do đó content hash là một thành phần của data integrity, không phải toàn bộ security/compliance solution.

---

## 36. Deep Dive — Merkle/DAG có cần không?

Có thể nghĩ hash chain DAY45 là một DAG đơn giản. Một hệ thống lớn có thể dùng Merkle tree/DAG để deduplicate và verify graph hiệu quả. Nhưng DAY45 chưa cần một framework đó.

Lý do không over-engineer:

- pipeline hiện có số step nhỏ;
- one-session/offline evidence dễ serialize;
- plain typed records dễ review/test;
- chưa có requirement distributed multi-writer lineage store.

Nếu sau này số artifact lớn, graph store/Merkle indexing có thể được thêm mà không cần đổi semantic fields cốt lõi.

---

## 37. Deep Dive — idempotency và determinism khác nhau thế nào?

**Determinism:** cùng input/config/code → cùng result/identity.

**Idempotency:** lặp lại cùng operation không gây side effect trùng không mong muốn.

DAY45 cung cấp deterministic IDs để hỗ trợ idempotency, nhưng persistent idempotency store chưa thuộc scope.

Ví dụ:

```text
same request → same event_id
```

Reference sink reject duplicate ID. Trong production, một store/dispatcher có thể dùng ID đó để suppress duplicate. DAY45 không tự tuyên bố distributed exactly-once delivery.

---

## 38. Deep Dive — tại sao event timestamp không nằm trong run ID?

Giả sử cùng một processing request chạy lúc 10:00 và 10:05.

Nếu timestamp nằm trong run ID:

```text
ID(10:00) != ID(10:05)
```

Bạn mất khả năng nhận biết exact retry.

Do đó run ID chỉ dùng execution facts. Timestamp thuộc event, vì nó mô tả **khi nào workflow event xảy ra**, không phải **processing request là gì**.

---

## 39. Deep Dive — provenance và scientific reproducibility

Trong nghiên cứu DSP, một kết quả chỉ có ý nghĩa khi ta biết experiment configuration. DAY45 đưa tư duy scientific reproducibility vào software artifact:

```text
raw evidence
+ selection/window definition
+ method
+ parameters
+ implementation version
+ random/adaptive fitting state
+ result hash
```

DAY45 hiện không có random model seed vì không training/modeling. Nếu future processing có stochastic component, seed/RNG algorithm sẽ phải trở thành identity fact.

---

## 40. Deep Dive — vì sao normalization reference là provenance-critical?

Giả sử:

\[
y(t) = \frac{x(t)}{MVC}\times 100
\]

Nếu chỉ lưu `y(t)` và method `MVC_PERCENT`, bạn vẫn không biết MVC nào đã dùng.

Hai references:

\[
MVC_1 = 1000\,\mu V, \qquad MVC_2 = 800\,\mu V
\]

cho hai output khác nhau từ cùng raw signal. Vì vậy reference ID/hash/version là part of provenance identity.

DAY45 chưa tính ratio nhưng đã dành field `normalization_eligibility_ref` để downstream không mất boundary này.

---

## 41. Deep Dive — provenance cho resampling

Nếu future profile resample 2000 Hz → 1000 Hz, manifest phải ghi:

```text
native_fs_hz = 2000
processed_fs_hz = 1000
is_resampled = true
```

và processing step phải ghi method + anti-alias config.

Nếu `is_resampled=false` mà Fs thay đổi, DAY45 reject. Đây là một ví dụ hay về “semantic consistency check”: không cần hiểu waveform để biết metadata đang tự mâu thuẫn.

---

## 42. Deep Dive — provenance cho causal vs zero-phase

Cùng cutoff/order nhưng phase mode khác nhau có thể cho timing semantics khác:

```text
ZERO_PHASE → acausal, near-zero phase distortion offline
CAUSAL     → forward-only, group delay
```

Vì vậy phase mode phải là parameter identity, không chỉ là một implementation detail.

Nếu activation timing được tính ở DAY48, provenance phase mode trở nên cực kỳ quan trọng.

---

## 43. Mini design review exercise

Bạn nhận manifest sau:

```text
outcome = COMPLETED
source_id = src_sha256_A
source_sha = B
profile = research-v1
step 0 input = X output = Y
step 1 input = Z output = W
final output = W
```

Hãy tìm ít nhất hai lỗi tiềm năng.

**Đáp án:**

1. `source_id` phải encode đúng `source_sha`; A/B mismatch là invalid.
2. `step 1 input` phải bằng `step 0 output`; nếu Z != Y, lineage bị đứt.

Final hash matching W không cứu được broken intermediate chain.

---

## 44. Mini security review exercise

Event:

```json
{
  "processing_run_id":"prun_sha256_...",
  "source_path":"LOCAL_PATH_WITH_DIRECT_IDENTIFIER",
  "reason_code":"FAILED"
}
```

Có gì sai?

- source path không portable;
- path có thể chứa direct identifier;
- event contract cấm source path;
- event phải reference `src_sha256_*`.

---

## 45. Teach-back challenge

Nếu phải giải thích DAY45 cho một Principal Engineer trong 90 giây, câu trả lời tốt nên chứa bốn ý:

1. DAY45 không thêm DSP algorithm; nó đóng raw-to-processed lineage.
2. Run/manifest/artifact IDs là content-addressed và deterministic.
3. Mỗi step có config + signal hash + mask hash chain, broken chain fail closed.
4. Processing events chỉ mang references/reasons; persistent event store chưa được claim.

Nếu bạn nói được bốn ý này và nêu được một failure example, bạn đã nắm đúng architectural intent.
