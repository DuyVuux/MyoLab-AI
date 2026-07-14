# Day 02 — Reading Notes

## After-Fatigue Condition
- Thu biceps brachii bằng ma trận 64 điện cực.
- Sampling rate: 2048 Hz.
- Band-pass: 20–400 Hz.
- Phân tích RMS, MNF, PSD và CV.
- CV chỉ chấp nhận khi quan hệ giữa tín hiệu lân cận đủ tin cậy.
- Dùng đoạn 1000 ms cho RMS/MNF/PSD; đoạn 500 ms cho CV.

## Clinical Workflow
- Protocol và placement quyết định ý nghĩa tín hiệu.
- Signal Quality Gate chạy trước feature extraction.
- Dữ liệu không đạt phải trả “không đủ điều kiện phân tích”.
- MFCV cần đo cùng một cơ và cùng làn sóng lan truyền, dãy điện cực tuyến tính, khoảng cách biết trước và sampling phù hợp.
- Bác sĩ/KTV quyết định cuối.

## Kết luận áp dụng
- MVP-0 dùng offline file import.
- CSV phải đi kèm metadata rõ ràng.
- QC validity và MFCV eligibility là hai kiểm tra khác nhau.
- Threshold trong paper không được xem là clinical threshold chính thức.