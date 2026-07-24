# Tiêu chí nghiệm thu Day 24

## Contract và workflow

- [ ] `ReviewCase` giữ `originalResultHash` bất biến.
- [ ] Review kỹ thuật chỉ do KTV, kỹ thuật viên Motion Lab hoặc bác sĩ thực hiện.
- [ ] Clinical sign-off chỉ do bác sĩ thực hiện.
- [ ] Chuyển trạng thái không hợp lệ bị chặn.
- [ ] Reject, supersede và yêu cầu đo lại bắt buộc có reason code.
- [ ] Feedback chưa adjudicate không được coi là training label.
- [ ] Report final chỉ sinh khi review state là `approved`.
- [ ] Report draft luôn có watermark.
- [ ] Report abstained không chứa kết luận giả.

## An toàn

- [ ] `rawSamplesIncluded=false`.
- [ ] `clinicalUseAllowed=false` trong prototype.
- [ ] `humanReviewRequired=true`.
- [ ] `automaticTreatmentRecommendation=false`.
- [ ] Không có câu chữ chẩn đoán, bắt buộc dừng tập hoặc quyết định return-to-play.
- [ ] AI output gốc không bị ghi đè bởi reviewer.

## Kỹ thuật

- [ ] Python tests pass.
- [ ] JSON Schema draft 2020-12 hợp lệ.
- [ ] TypeScript strict check pass.
- [ ] Report hash kiểm tra lại được.
- [ ] Evidence JSON được tạo deterministic theo payload nghiệp vụ.
- [ ] Checker artifact và safety pass.
