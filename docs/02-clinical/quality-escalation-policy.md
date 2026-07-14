# Quality Escalation Policy

**Document ID:** CLIN-QEP-001  
**Version:** 0.1.0  
**Status:** Draft — MVP-0  
**Applies to:** Signal import, metadata validation, protocol compatibility, signal quality, and optional capability checks  
**Primary users:** Kỹ thuật viên (KTV), bác sĩ/người review, đội kỹ thuật

## 1. Mục đích

Tài liệu này quy định cách hệ thống xử lý các kết quả kiểm tra chất lượng trước khi chạy phân tích mỏi cơ.

Nguyên tắc bắt buộc:

> **Quality fail không được biến thành “không phát hiện mỏi”.**

Khi dữ liệu không đủ điều kiện, hệ thống phải **abstain** và nêu rõ lý do thay vì suy diễn trạng thái mỏi hoặc không mỏi.

## 2. Outcome và hành vi hệ thống

| Status | `analysis_allowed` | Hành vi |
|---|---:|---|
| `pass` | `true` | Tiếp tục phân tích. |
| `warning` | `true` | Tiếp tục, giữ warning trong kết quả và yêu cầu review. |
| `fail` | `false` | Block analysis, trả về abstention và hướng dẫn khắc phục. |
| `import_rejected` | `false` | Không tạo analysis run; yêu cầu sửa file hoặc metadata rồi import lại. |

## 3. Quy tắc escalation

### 3.1. `import_rejected`

Áp dụng khi file hoặc metadata không thể được đọc hoặc không đáp ứng contract tối thiểu.

**Operator-facing correction:**

- kiểm tra CSV và manifest có tồn tại;
- sửa lỗi cú pháp JSON/YAML;
- bổ sung trường bắt buộc;
- sửa tên cột hoặc channel mapping;
- loại bỏ định danh trực tiếp không được phép;
- import lại sau khi sửa.

**Wording hiển thị:**

> Không thể nhập phiên đo. Vui lòng kiểm tra file và metadata theo hướng dẫn, sau đó thử lại.

### 3.2. `fail`

Áp dụng khi dữ liệu đã import được nhưng không đủ an toàn hoặc không tương thích để phân tích.

Ví dụ:

- sampling rate không đạt protocol;
- active phase quá ngắn;
- tín hiệu flatline, clipping hoặc nhiễu nghiêm trọng;
- thiếu metadata bắt buộc cho protocol;
- usable signal ratio dưới ngưỡng tối thiểu.

**Operator-facing correction:**

- kiểm tra lại vị trí và tiếp xúc điện cực;
- xác nhận sampling rate và cấu hình thiết bị;
- đo lại theo đúng protocol;
- bổ sung hoặc sửa phase marker;
- xác nhận muscle, side, unit và session parameters;
- chuyển cho người review nếu không thể khắc phục tại chỗ.

**Wording abstention:**

> Dữ liệu không đủ điều kiện để phân tích mỏi cơ. Hệ thống không đưa ra kết luận mỏi hoặc không mỏi. Vui lòng kiểm tra lý do và thực hiện đo lại hoặc sửa metadata nếu phù hợp.

### 3.3. `warning`

Phân tích được phép tiếp tục nhưng warning phải:

- được giữ trong output và report;
- có reason code rõ ràng;
- hiển thị cho KTV/người review;
- không bị tự động bỏ qua;
- được xem xét trước khi ký báo cáo cuối.

**Wording gợi ý:**

> Phân tích đã hoàn thành với cảnh báo chất lượng. Kết quả cần được KTV/bác sĩ review trước khi sử dụng.

### 3.4. `pass`

Phân tích được phép tiếp tục, nhưng `pass` không đồng nghĩa với:

- chẩn đoán lâm sàng;
- xác nhận tuyệt đối về tình trạng cơ;
- tự động đưa ra quyết định điều trị;
- bỏ qua human review trong workflow lâm sàng.

## 4. MFCV/CV capability branch

Kết quả:

```text
mfcv.eligible = false
```

**không đồng nghĩa với:**

```text
basic sEMG analysis = fail
```

Nếu basic sEMG analysis vẫn đáp ứng quality gate, hệ thống có thể tiếp tục với các đặc trưng như RMS, MAV, MDF, MNF và slope.

Khi MFCV/CV không đủ điều kiện:

- không tính hoặc nội suy MFCV/CV;
- không tạo giá trị giả;
- trả reason code về nguyên nhân không đủ điều kiện;
- ghi rõ capability này không khả dụng trong phiên đo;
- không chặn basic sEMG analysis trừ khi chính tín hiệu cơ bản cũng fail.

**Wording hiển thị:**

> Không đủ điều kiện tính MFCV/CV cho phiên đo này. Phân tích sEMG cơ bản vẫn được thực hiện nếu các kiểm tra chất lượng còn lại đạt yêu cầu.

## 5. Giới hạn về khuyến nghị

Hệ thống không được tự động đưa ra khuyến nghị điều trị như:

- dừng tập;
- tăng hoặc giảm tải bắt buộc;
- thay đổi phác đồ;
- xác nhận đủ điều kiện return-to-play.

Hệ thống chỉ được dùng wording hỗ trợ review, ví dụ:

> KTV/bác sĩ xem xét kết quả cùng đánh giá lâm sàng và protocol hiện tại.

## 6. Audit tối thiểu

Mỗi outcome phải lưu:

- status;
- `analysis_allowed`;
- reason codes;
- correction guidance;
- timestamp;
- validator/QC config version;
- reviewer status nếu có;
- MFCV/CV eligibility và lý do.

## 7. Done Criteria

- [x] Có operator-facing correction.
- [x] Không có automated treatment recommendation.
- [x] Có wording abstention rõ ràng.
- [x] Có MFCV capability behavior.
- [x] Quality fail không bị diễn giải thành “không phát hiện mỏi”.
- [x] `warning`, `fail` và `import_rejected` có hành vi khác nhau.
