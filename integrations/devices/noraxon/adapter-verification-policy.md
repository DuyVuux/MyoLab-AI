# Noraxon Adapter Verification Policy

## Adapter Classification

| Class              | Verification Level               | Ví dụ                                        |
|--------------------|----------------------------------|-----------------------------------------------|
| `generic`          | `PROJECT_VERIFIED`               | `generic_csv`, `generic_mat`, `generic_c3d`   |
| `vendor_candidate` | `OFFICIAL_PUBLIC_CAPABILITY_ONLY`| `noraxon_ascii_candidate`, `noraxon_mat_candidate` |
| `site_verified`    | `SITE_VERIFIED`                  | `noraxon_motionlab_v1` (chưa tồn tại)        |

## Naming Convention

**Được phép:**

```text
noraxon_ascii_candidate_v0.1
noraxon_mat_candidate_v0.1
noraxon_c3d_candidate_v0.1
```

**Không được phép** khi chưa có actual export:

```text
motionlab_noraxon_export_v1
noraxon_production_adapter_v1
```

## Candidate Adapter Requirements

Mỗi candidate adapter **bắt buộc** chứa metadata:

```yaml
site_verified: false
clinical_use_allowed: false
derived_from_real_motionlab_export: false
production_support_claimed: false
```

## Promotion Gate: Candidate → Site Verified

Điều kiện để promote adapter từ `vendor_candidate` lên `site_verified`:

1. Actual de-identified export đã nhận và hash
2. `inspect_unknown_export.py` đã chạy
3. Field dictionary đã xây
4. Mapping profile đã tạo và lock
5. Conformance tests (Step 7 của Runbook) đã pass
6. Adapter version frozen với profile hash
7. Evidence bundle đã cập nhật
8. Site audit JSON đã chuyển sang `SITE_VERIFIED`

## No Invented Site Schema

Không được hard-code hoặc công bố các tên cột sau như thể đó là schema thật của Motion Lab khi chưa có sample export:

- `Time`
- `Sensor 1.EMG`
- `Event`
- `Frame`
- `Ultium Channel 01`

Chỉ được sử dụng trong test fixture nếu:

- Có namespace `candidate`
- Có manifest `synthetic`
- Có disclaimer rõ ràng
- Không được dùng cho claim tương thích site
