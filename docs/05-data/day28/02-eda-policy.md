# EDA Policy

1. Chỉ train + validation partitions.
2. Test partition không được đọc.
3. Descriptive statistics không tự động sửa raw data.
4. Threshold phát triển từ train; validation chỉ audit sau khi freeze.
5. Không dùng file name/subject ID làm predictor.
6. Không gọi heuristic QC là clinical threshold.
7. Không gọi public dataset là Noraxon-compatible.
8. Mọi output phải có dataset/profile/split hash.
9. Unknown labels được giữ trong raw provenance.
10. EDA report phải có negative findings và limitations.
