# Năm lớp dữ liệu và ranh giới provenance

## L1 — Native acquisition record

Bản ghi gốc trong myoRESEARCH/MR3 hoặc hệ acquisition. Đây là nguồn gần acquisition nhất.

## L2 — Vendor export artifact

CSV, C3D, MAT hoặc native export package do vendor software tạo. Có thể mất metadata so với L1.

## L3 — Normalized table

Representation do dự án tạo sau khi parse, chuẩn hóa unit/channel/time và gắn provenance.

## L4 — Feature/metric store

RMS, MAV, MDF, MNF, trend, QC, gesture features và UC2 metrics; luôn giữ version và source reference.

## L5 — Model-ready dataset

Chỉ được tạo khi:

```text
legal approved
+ provenance complete
+ privacy pass
+ labels defined
+ split-safe groups
+ immutable manifest
+ training gate approved
```

## Invariant

```text
L3 không được gọi là native vendor data.
L4 không được dùng để dựng lại raw signal.
L5 không được tạo từ restricted data ngoài DUA.
```
