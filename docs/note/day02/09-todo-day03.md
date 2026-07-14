# Day 03 — Todo

## Mục tiêu
Chuẩn hóa data/file input và triển khai ingestion adapter tối thiểu.

## Việc phải làm
1. Hoàn thiện `signal-import-spec.md`.
2. Chốt canonical internal signal representation.
3. Implement CSV importer:
   - parse timestamp;
   - parse channel;
   - normalize unit;
   - load manifest;
   - validate metadata.
4. Tạo fixtures:
   - valid file;
   - missing timestamp;
   - non-monotonic timestamp;
   - sampling mismatch;
   - missing channel;
   - unsupported unit.
5. Viết unit tests cho importer.
6. Sinh normalized session object và summary JSON.
7. Cập nhật decision log và open questions.

## Chưa làm trong Day 3
- Không filter.
- Không tính RMS/MDF/MNF.
- Không viết FRS.
- Không train ML.
- Không claim Noraxon compatibility trước sample export thật.

## Done criteria
- Importer xử lý đúng fixture hợp lệ.
- Fixture lỗi trả đúng reason code.
- Không silently infer metadata thiếu.
- Output có version và source provenance.