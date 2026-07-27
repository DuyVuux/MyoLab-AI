# Day 25 Decision Record

## D25-DEC-001 — Chưa training

**Quyết định:** `trainingAllowed=false`.

**Lý do:** chưa có actual site export, exact site schema và model-ready dataset manifest đã được phê duyệt.

## D25-DEC-002 — Free-first stack theo vai trò

Không chọn một dataset duy nhất. Dùng stack riêng cho Task A/B/C.

## D25-DEC-003 — JSON là downstream representation

Cho tới khi có bằng chứng official/site, JSON chỉ là contract do project tạo, không phải native MR3 export.

## D25-DEC-004 — MFCV optional và disabled

Không bật MFCV trên setup site nếu thiếu geometry/IED/order/alignment/raw propagation evidence.

## D25-DEC-005 — Task C metric-first

UC2 bắt đầu bằng metric provenance, không classifier tổng hợp.

## D25-DEC-006 — Conflict registry là artifact bắt buộc

Metadata mâu thuẫn không được âm thầm chọn một phiên bản; phải được ghi và có evidence request.

## D25-DEC-007 — Training permissions tách 3 cấp

**Quyết định:** Thay cờ đơn `trainingAllowed=false` bằng 3 cờ riêng:

- `public_engineering_baseline: allowed=true` (kèm 6 điều kiện)
- `motionlab_local_model: allowed=false` (chờ actual site export)
- `clinical_model: allowed=false` (chờ ethics/IRB)

**Lý do:** Cờ đơn gây hiểu nhầm rằng không được train bất kỳ model nào, trong khi public baseline trên open datasets là an toàn.

**Tham chiếu:** `noraxon-output-uncertainty-resolution-addendum.md` §3

## D25-DEC-008 — Cô lập vendor uncertainty sau adapter (ADR-0009)

**Quyết định:** Tất cả source-specific uncertainty được cô lập trong adapter và mapping profile. Downstream pipeline chỉ phụ thuộc canonical contract.

**Lý do:** Tránh phải viết lại toàn bộ pipeline khi file thật từ Motion Lab khác schema suy đoán.

**Tham chiếu:** `docs/03-architecture/adr/ADR-0009-isolate-unknown-vendor-output-behind-adapters.md`

## D25-DEC-009 — No invented site schema

**Quyết định:** Không hard-code tên cột giả như `Time`, `Sensor 1.EMG`, `Ultium Channel 01` như thể là schema thật của Motion Lab. Chỉ dùng trong test fixture có namespace `candidate` và disclaimer.

**Lý do:** Tránh technical debt lớn khi file thật khác hoàn toàn.

**Tham chiếu:** `integrations/devices/noraxon/adapter-verification-policy.md`

## D25-DEC-010 — Capability degradation policy

**Quyết định:** Pipeline phải giảm chức năng có kiểm soát thay vì crash. Thiếu electrode geometry → tắt MFCV, pipeline sEMG vẫn chạy. Chỉ có processed metrics → report only, không raw reprocessing.

**Lý do:** Adapter không nên hard-fail khi thiếu optional fields.

**Tham chiếu:** `noraxon-output-uncertainty-resolution-addendum.md` §8
