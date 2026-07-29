# Leakage notes

Các lỗi phải tự kiểm tra:

- fit scaler trên toàn dataset;
- chọn CH4 sau khi nhìn outer test;
- window overlap giữa partition;
- random split theo window;
- chọn resampling/filter bằng test performance;
- dùng subject/day/file name làm predictor;
- mở test để kiểm tra shape hoặc class distribution.
