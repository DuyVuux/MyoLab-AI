# DAY03 Feynman Learning Guide

## 1. DAY03 học cái gì?

Ba từ khóa của roadmap là:

- **workflow observation**;
- **sampling bias**;
- **operational baseline**.

Mục tiêu không phải học thống kê phức tạp. Mục tiêu là hiểu tại sao một con số thời gian chỉ có giá trị khi ta biết **nó được đo từ đâu, trên ca nào, trong boundary nào và bằng cách nào**.

## 2. Operational baseline là gì?

Hãy tưởng tượng bạn muốn chứng minh AI giúp bác sĩ tiết kiệm thời gian.

Nếu bạn chỉ nói:

> “Team nghĩ mỗi ca mất hơn 60 phút.”

đó là **estimate**.

Nếu bạn đứng quan sát, đo từng khoảng thời gian, biết ai đang làm gì, lưu evidence, rồi tổng hợp đúng cách, bạn mới bắt đầu có **operational baseline**.

Baseline không nhất thiết phải hoàn hảo ngay Round 1. Nhưng nó phải **thật và truy vết được**.

## 3. Vì sao DAY02 và DAY03 phải tách nhau?

DAY02 làm cái thước.

DAY03 dùng cái thước.

Nếu vừa thiết kế thước vừa đo ngay mà không freeze rule, bạn rất dễ thay rule sau khi nhìn thấy dữ liệu để tạo kết quả mình thích.

## 4. Measurement fact khác inference thế nào?

**Fact:** “Bác sĩ xem waveform trong 180 giây.”

**Operator report:** “Đoạn này khó xử lý.”

**Inference:** “Có vẻ do motion artifact.”

**Clinical interpretation:** “Đây là biến đổi do bệnh lý.”

DAY03 chỉ được nâng mức evidence theo đúng loại bằng chứng. Không được biến inference thành fact.

## 5. Sampling bias là gì?

Nếu Round 1 chỉ quan sát một ca dễ, bạn có thể thấy processing time rất thấp.

Nếu chỉ quan sát một ca cực khó, bạn có thể thấy processing time rất cao.

Cả hai đều là measurement thật, nhưng **không đại diện cho toàn bộ MotionLab**.

Vì vậy Round 1 nên mô tả:

- mình đã quan sát bao nhiêu ca;
- workflow/protocol nào;
- có partial case không;
- có remeasurement không;
- điều gì chưa được bao phủ.

Không được nói “MotionLab trung bình X phút” nếu sample chưa support điều đó.

## 6. Vì sao không cộng tất cả duration lại?

Software có thể export trong lúc bác sĩ đang xem một record khác.

Hai activity chồng nhau trong thời gian thực.

Nếu cộng thẳng duration, bạn tạo ra một “case time” dài hơn thời gian thực tế.

Vì vậy ta dùng **union of intervals** cho từng class và giữ elapsed time riêng.

## 7. Tại sao interpretation phải tách khỏi data toil?

North Star là giảm thời gian xử lý data, không phải loại bỏ vai trò chuyên môn của bác sĩ.

Nếu AI làm bác sĩ interpret kỹ hơn nhưng giảm cleaning rất mạnh, đó vẫn có thể là thành công.

Nếu bạn trộn interpretation vào manual-processing time, KPI sẽ mơ hồ.

## 8. Remeasurement phải đo như thế nào?

Cần ít nhất:

- có xảy ra không;
- số episode;
- thời gian burden;
- reason do operator báo cáo;
- denominator khi tính rate.

Một câu “thỉnh thoảng phải đo lại” chưa phải remeasurement rate.

## 9. Vì sao không đóng OQ chỉ để roadmap đẹp?

Open question là danh sách những thứ ta **chưa biết**.

Đóng OQ khi chưa có evidence sẽ làm hệ thống trông tiến triển nhanh, nhưng downstream sẽ xây trên thông tin giả.

Trong medical/clinical engineering, “UNKNOWN có provenance” tốt hơn “KNOWN nhưng sai”.

## 10. DAY03 có được xem raw sEMG không?

Không cần để hoàn thành time-motion study. Mục tiêu là workflow burden, không phải phân tích waveform.

Pack này cố tình không yêu cầu raw patient data vì privacy gate chuyên biệt nằm ở DAY05.

## 11. Vì sao current ZIP bị BLOCKED_WITH_EVIDENCE dù test PASS?

Vì có hai loại “pass”:

1. **engineering validation:** schema/code/test đúng;
2. **evidence gate:** dữ liệu thực tế đủ để ra quyết định chưa.

Code có thể hoàn hảo nhưng evidence chưa tồn tại.

Trong DAY03 hiện tại:

- engineering layer: ready;
- site evidence: chưa được cung cấp;
- vì vậy không được giả `GO_FOR_DAY_04`.

## 12. Ví dụ phản ví dụ

### Sai

“Bác sĩ nói thường mất 60 phút nên baseline = 60 phút.”

### Đúng

“60 phút là team estimate. Round-1 chưa có baseline-eligible observation; baseline remains UNKNOWN.”

### Sai

“3 ca đầu đều không phải đo lại → remeasurement rate MotionLab = 0%.”

### Đúng

“Trong 3 observed cases, 0 remeasurement episodes were observed; representativeness is not established.”

## 13. Mental model

`Event → Case → Round-1 sample → Baseline characterization → Later pilot comparison`

Không nhảy từ `Event` thẳng tới “clinical/product KPI proven”.

## 14. Self-check

1. Tôi có biết observation mode của từng row không?
2. Tôi có biết case boundary không?
3. Tôi có tách doctor/KTV/system/waiting/interpretation không?
4. Tôi có xử lý overlap bằng interval union không?
5. Tôi có biết record nào baseline eligible và tại sao không?
6. Tôi có đang suy rộng Round 1 thành toàn site không?
7. Tôi có biến operator report thành QC taxonomy không?
8. Tôi có đưa raw patient data vào repo không?

## 15. Flashcards

**Q:** Interview estimate có phải measured baseline không?  
**A:** Không.

**Q:** Synthetic fixture có baseline eligible không?  
**A:** Không.

**Q:** Một direct observation có tự động đại diện cho MotionLab không?  
**A:** Không.

**Q:** OQ chưa đóng có phải failure không?  
**A:** Không; silent closure mới nguy hiểm.

**Q:** Test PASS nhưng evidence thiếu thì status gì?  
**A:** `BLOCKED_WITH_EVIDENCE` hoặc limitation state phù hợp, không fake GO.

## 16. Bài tập

Cho ba events:

- Doctor inspect: 09:00–09:05
- Software export: 09:02–09:04
- Doctor interpret: 09:05–09:08

Hãy trả lời:

1. elapsed time từ 09:00–09:08 là bao nhiêu?
2. clinician data hands-on là bao nhiêu?
3. clinical interpretation là bao nhiêu?
4. có được cộng 5 + 2 + 3 = 10 phút rồi gọi elapsed không?

**Đáp án:** 8 phút; 5 phút; 3 phút; không.

## 17. Teach-back

Nếu bạn có thể giải thích câu sau cho một người mới, bạn đã hiểu DAY03:

> “DAY03 không tìm một con số đẹp; DAY03 tạo bằng chứng thật về cách MotionLab đang vận hành, và chỉ cho phép con số trở thành baseline khi source, boundary, timing, review và limitation đều truy vết được.”
