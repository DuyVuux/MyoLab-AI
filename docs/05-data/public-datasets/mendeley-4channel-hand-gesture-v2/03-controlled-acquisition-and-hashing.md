# Controlled acquisition và hashing

1. Dry-run URL/destination/license.
2. Download vào file `.part`.
3. Tính SHA-256 streaming.
4. Atomic rename khi hoàn tất.
5. Ghi retrieval receipt.
6. Không extract trước inventory.

Archive gốc là immutable source artifact. Bất kỳ chuyển đổi nào phải sinh artifact mới và ghi provenance.
