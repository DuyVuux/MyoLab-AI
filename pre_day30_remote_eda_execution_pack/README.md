# Pre-Day30 — Dual Dataset Real-EDA Execution Pack

Gói này bổ sung bước vận hành còn thiếu giữa Day 28/29 và Day 30:

```text
Mendeley 4-channel thật → EDA/QC Day 28 thật ┐
                                             ├→ Pre-Day30 Dual Gate → Day 30 Harmonization
GRABMyo thật → EDA/QC + cross-day Day 29 thật ┘
```

## Hai vùng cố định

```text
ZONE 1 — Git/monorepo
/home/duyvd9/massive/projects/semg-fatigue/MyoLab-AI/

ZONE 2 — dữ liệu lớn ngoài Git
/home/duyvd9/massive/projects/myolab-ai-data/
```

ZONE 1 chỉ lưu code, schema, config, manifest, checksum và evidence nhỏ. ZONE 2 lưu remote catalog, cache có giới hạn, raw/normalized signal, index và evidence đầy đủ.

## Điểm cần hiểu đúng về “không tải dataset về”

Không thể tính EDA tín hiệu mà không truyền bất kỳ byte tín hiệu nào qua mạng. Gói này hỗ trợ ba mức:

1. `METADATA_ONLY`: không tải signal body; chỉ đọc metadata/HEAD/file listing.
2. `BOUNDED_SAMPLE`: chỉ truyền một tập mẫu có ngân sách dung lượng cố định.
3. `STREAMING_FULL_SCAN`: đọc lần lượt/chunk, ghi summary rồi giải phóng RAM; không giữ toàn bộ corpus trên ổ đĩa, nhưng tổng lượng byte truyền qua mạng có thể vẫn gần kích thước dataset.

Nếu nguồn chỉ phát hành **một archive nén nguyên khối** và không hỗ trợ truy cập từng file/range request, signal-level EDA không thể thực hiện đầy đủ nếu không tải archive hoặc nhờ môi trường gần dữ liệu giải nén phía server.

## Tài liệu nên đọc đầu tiên

1. `docs/plans/PRE_DAY30_KE_HOACH_TRIEN_KHAI.md`
2. `docs/05-data/PRE_DAY30_HUONG_DAN_EDA_DU_LIEU_LON_REMOTE_FIRST.md`
3. `docs/05-data/KIEN_TRUC_HAI_VUNG_LUU_TRU.md`
4. `docs/learning/TOAN_DSP_VA_HE_THONG_CAN_HOC.md`

## Lệnh khởi đầu

```bash
cd /home/duyvd9/massive/projects/semg-fatigue/MyoLab-AI

# Sau khi giải nén pack vào repo bằng unzip -n
bash scripts/dev/bootstrap_pre_day30_storage.sh --dry-run
bash scripts/dev/bootstrap_pre_day30_storage.sh --apply

python scripts/data/check_two_zone_contract.py \
  --config data-platform/configs/pre_day30_storage.local.yaml

bash scripts/dev/run_pre_day30_checks.sh
```

## Trạng thái mặc định

```yaml
training_allowed: false
pooled_training_allowed: false
test_signal_access_allowed: false
clinical_use_allowed: false
motion_lab_transfer_verified: false
mfcv_eligible: false
```
