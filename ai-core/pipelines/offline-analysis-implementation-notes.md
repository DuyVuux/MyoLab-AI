# Ghi chú triển khai Offline Analysis

- `run_offline_analysis.py` là CLI; logic chính nằm trong `offline_analysis.py`.
- Không đưa raw arrays vào stage JSON.
- Analysis fingerprint dựa trên canonical payload/config hashes, không dựa trên output path.
- Temporary output chỉ publish khi toàn pipeline hoàn tất.
- Không dùng package này như clinical report cuối.
