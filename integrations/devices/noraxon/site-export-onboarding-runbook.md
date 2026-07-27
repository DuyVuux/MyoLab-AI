# Noraxon Site Export Onboarding Runbook

Quy trình 8 bước để tích hợp actual export từ Motion Lab vào dự án.
Chỉ thực hiện khi có de-identified export thật từ site.

---

## Step 1 — Receive

**Input:** Export đã khử định danh từ Motion Lab operator.

**Output:** Immutable source bundle + SHA-256 hash.

**Checklist:**

- [ ] File nhận được đã qua PHI screening
- [ ] SHA-256 hash đã được tính và lưu
- [ ] Immutable copy đã lưu tại `data-platform/raw/noraxon-site/`
- [ ] Receipt timestamp đã ghi

---

## Step 2 — Inventory

**Input:** Source bundle từ Step 1.

**Output:** File tree, headers, variables, formats.

**Tool:** `scripts/data/inspect_unknown_export.py`

```bash
python3 scripts/data/inspect_unknown_export.py \
  --input path/to/export/bundle \
  --output qa-validation/evidence/day25-site-export-inspection.json
```

---

## Step 3 — Classify

Phân biệt mỗi file trong bundle:

| Phân loại               | Ý nghĩa                                        |
|--------------------------|-------------------------------------------------|
| `NATIVE_ACQUISITION`    | File ghi trực tiếp từ sensor                    |
| `VENDOR_EXPORT`         | File đã qua export wizard                       |
| `PROCESSED_REPORT`      | Report/metric đã tính sẵn                       |
| `PROJECT_CONVERSION`    | File do project team chuyển đổi (không phải vendor) |

---

## Step 4 — Build field dictionary

Tạo ánh xạ cho mỗi file export:

```csv
source_field,semantics,unit,evidence,canonical_field
```

Ví dụ:

```csv
Time [s],timestamp,seconds,header inspection,sample_index_or_time
EMG.RTA [mV],signal,millivolts,header + manual confirm,samples
```

---

## Step 5 — Build site mapping profile

Sử dụng template: `integrations/devices/noraxon/mapping-profile.template.yaml`

Không hard-code vào model/DSP code.

---

## Step 6 — Implement site adapter

Tạo `NoraxonMotionLabAdapter v1.0.0`:

- Đọc mapping profile từ YAML
- Output canonical contract
- Ghi provenance (adapter_id, version, source_hash)
- Set `site_verified: true`
- Set `clinical_use_allowed: false` (cho đến khi có clinical protocol)

---

## Step 7 — Conformance tests

Kiểm tra bắt buộc:

- [ ] Sample count khớp header
- [ ] Duration tính toán đúng với Fs
- [ ] Timestamp monotonically increasing
- [ ] Sampling rate khớp acquisition settings
- [ ] Channel order khớp mapping profile
- [ ] Unit conversion chính xác
- [ ] Event marker alignment (nếu có)
- [ ] Source hash khớp immutable copy
- [ ] Raw/normalized comparison within tolerance

---

## Step 8 — Freeze version

```yaml
verification_status: SITE_VERIFIED
adapter_id: noraxon_motionlab_v1
adapter_version: 1.0.0
supported_profile_hash: sha256:...
freeze_date: <date>
verified_by: <operator>
```

Cập nhật:

- `integrations/devices/noraxon/site-export-evidence-bundle.template.json` → filled version
- `integrations/devices/noraxon/public-vs-site-capability-matrix.csv` → status updates
- `qa-validation/evidence/day25-noraxon-site-audit.json` → `status: SITE_VERIFIED`
