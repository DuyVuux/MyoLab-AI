# Raw Immutability Policy — MotionLab Data Intelligence

## 1. Purpose
Khóa quy tắc lưu trữ nguồn cho DAY11: source bytes là bằng chứng gốc. Hệ thống có thể đọc, hash, lập ledger và tạo derivative, nhưng không được sửa/ghi đè source đã ingest.

## 2. Invariants
1. Raw source được mở read-only bởi ingestion/provenance logic.
2. Mỗi source có SHA-256 trên **exact bytes** và `source_id` content-addressed.
3. `source_id = src_sha256_<64 lowercase hex>`; filename/path không phải identity.
4. Re-ingest bytes giống hệt phải trả `DUPLICATE`; không append record mới và không overwrite first-seen metadata.
5. Raw missing values, row order, encoding, unit và vendor fields không bị sửa ở raw layer.
6. Filter, resample, interpolation, de-identification transform, unit conversion và canonicalization tạo derivative riêng có provenance; không viết ngược raw.
7. Nếu verify hash/byte-size fail: `FAIL CLOSED`; source không được coi là cùng bằng chứng.
8. Ledger là append-only. Update-in-place một SourceRecord đã ghi là forbidden.
9. Raw patient data không commit Git. Repo chỉ chứa schema, policy và synthetic fixtures.
10. Approved storage/access/retention do governance quyết định; Git path không phải approved raw store.

## 3. Layers
```text
Vendor/source bytes
        ↓ hash/read-only
RAW / SourceRecord
        ↓ parser (later days)
CURATED canonical representation
        ↓ versioned processing
PROCESSED / metrics / evidence
```

`RAW immutable` không có nghĩa filesystem không bao giờ thay đổi vì backup/storage operations; nghĩa là analytical provenance phải có immutable logical identity và mọi mutation của source bytes làm hash verification fail.

## 4. Duplicate semantics
- Same bytes, same filename → duplicate.
- Same bytes, different filename → duplicate by content; filename không tạo identity mới.
- Different bytes, same filename → **new source identity**; không overwrite record cũ.
- Metadata khác nhưng bytes giống nhau → duplicate; DAY11 không silently rewrite first-seen record. Nếu cần observation history, thiết kế event/audit extension sau.

## 5. Storage reference
`storage_reference` phải là opaque reference tới approved storage. Không dùng source path như public log key. Filename/path có thể chứa identifier nên chỉ tồn tại trong approved provenance context.

## 6. Hash policy
- Algorithm: SHA-256.
- Python implementation: `hashlib.file_digest(file_obj, "sha256")` với Python 3.11+.
- Hash trên bytes trước parse/normalize/de-identify.
- Digest lowercase hex, 64 ký tự.
- Không dùng mtime/file size làm identity; size chỉ là integrity evidence bổ sung.

## 7. Failure rules
| Failure | Required behavior |
|---|---|
| Source path missing/directory | typed failure |
| unreadable source | typed failure |
| ledger malformed | `LedgerCorruptionError`; do not continue silently |
| source hash mismatch | `SourceIntegrityError`; fail closed |
| unknown governance | research reuse = not authorized |
| duplicate digest in ledger | ledger corruption; do not choose one silently |

## 8. Privacy boundary
Original filename, storage reference và vendor metadata có thể chứa identifier. Không đưa chúng vào public logs, screenshots, CI artifacts hay synthetic fixtures bằng giá trị thật. DAY05 privacy rules tiếp tục có hiệu lực.

## 9. Reproducibility boundary
DAY11 chứng minh exact-source identity và deterministic duplicate behavior. Nó **chưa** chứng minh parser correctness, canonical Session reproducibility, QC reproducibility hay processing reproducibility.

## 10. Requirement traceability
- FR-007: raw missing values/source bytes không tự sửa.
- FR-008: checksum + source identifier.
- FR-053: processed steps không overwrite raw.
- NFR-002: provenance source identity.
- NFR-003: raw immutable + checksum verification.
- AC-09: raw data bất biến và checksum xác minh được.
