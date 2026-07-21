# Chính sách khả năng tái lập cho DSP MVP-0

## 1. Mục tiêu

Có thể xác định config, code và environment nào đã tạo một preprocessing output.

## 2. Quy tắc

1. Config, code và evidence phải có SHA-256.
2. Cùng environment phải cho output hash giống nhau với fixture deterministic.
3. Khác environment được so bằng numerical tolerance, không ép bitwise equality nếu backend floating-point khác.
4. Release/pilot phải có lock file dependency và environment manifest.
5. Không thay đổi config đã freeze mà không bump version hoặc re-verify.

## 3. Thông tin cần lưu

- Python version.
- NumPy/SciPy/PyYAML version.
- OS và machine architecture.
- Byte order.
- NumPy build configuration.
- Config hash.
- Implementation file hashes.
- Verification report path/hash.

## 4. Giới hạn

Reproducibility của DSP không chứng minh clinical validity hoặc data quality của acquisition.
