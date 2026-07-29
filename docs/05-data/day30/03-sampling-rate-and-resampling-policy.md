# Chính sách sampling rate

## Primary

Giữ 2000 Hz và 2048 Hz ở native rate. Window được khai báo bằng mili giây.

## Comparator

GRABMyo 2048 → 2000 dùng polyphase `up=125`, `down=128`.

## Bị chặn

- resample toàn bộ trước split;
- PSD với `fs` hard-code;
- downsample 1024 chỉ để số mẫu bằng nhau;
- resample mà không lưu provenance.
