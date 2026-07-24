# Chính sách Human Review và Sign-off v0.1

## Nguyên tắc

- AI output là evidence kỹ thuật, không phải final clinical decision.
- Technical review và clinical review là hai lớp khác nhau.
- Chỉ bác sĩ được clinical sign-off.
- Mọi override/remeasure/reject phải có reason code.
- Original AI result và source hash không bị ghi đè.
- Final report chỉ được tạo sau clinical approval.

## Trạng thái

```text
pending_technical_review
→ pending_clinical_review
→ approved | rejected | remeasure_requested
```

`superseded` dùng khi report/kết luận đã được thay thế bởi phiên review mới, không dùng để xóa lịch sử.
