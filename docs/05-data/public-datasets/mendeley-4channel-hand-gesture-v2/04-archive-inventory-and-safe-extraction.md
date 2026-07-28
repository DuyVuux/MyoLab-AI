# Archive inventory và safe extraction

Inventory phải ghi path, size, compressed size, extension và path-safety. Entry có absolute path hoặc `..` traversal phải làm gate FAIL.

Không chạy executable/script lạ trong archive. Không mở hàng loạt file bằng Excel. Chỉ extract vào controlled directory sau khi inventory PASS.
