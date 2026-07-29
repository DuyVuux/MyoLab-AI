# Kiến trúc hai vùng lưu trữ cho MyoLab-AI

## 1. Đường dẫn khóa

```yaml
repo_root: /home/duyvd9/massive/projects/semg-fatigue/MyoLab-AI
data_root: /home/duyvd9/massive/projects/semg-fatigue/myolab-ai-data
```

Điều kiện hình học filesystem:

```text
repo_root != data_root
data_root không phải con của repo_root
repo_root không phải con của data_root
```

## 2. ZONE 1 — Git control plane

ZONE 1 là **control plane**, không phải data lake.

```text
MyoLab-AI/
├── ai-core/configs/
├── data-platform/
│   ├── configs/
│   ├── datasets/external/<dataset_id>/
│   └── object-storage/
├── docs/05-data/
├── packages/common-schemas/
├── qa-validation/evidence/pre-day30/
├── scripts/data/
└── scripts/dev/
```

### Nội dung được commit

- source record và license record;
- config không chứa secret;
- remote object catalog **đã rút gọn**, không chứa token;
- schema;
- parser/EDA code;
- hash của catalog/split/evidence;
- summary nhỏ;
- report và decision.

### Nội dung cấm commit

```text
*.zip *.7z *.rar *.tar *.gz
*.mat *.h5 *.hdf5 *.wfdb *.dat
raw waveform CSV/Parquet/NPY/NPZ/Zarr
remote cache
credential/token/cookie
model artifact
```

Không dựa duy nhất vào extension; script còn kiểm kích thước và các path pattern.

## 3. ZONE 2 — data plane

ZONE 2 là **data plane**, nơi dữ liệu có thể lớn và lifecycle khác Git.

```text
myolab-ai-data/
├── external/
│   ├── mendeley-4channel-hand-gesture-v2/
│   └── grabmyo-v1.1.0/
├── shared/
│   ├── cache/
│   ├── temporary/
│   └── logs/
└── README_LOCAL_DATA.md
```

Mỗi dataset:

```text
<dataset>/
├── source-metadata/
│   ├── retrieval-receipt.yaml
│   └── remote-objects.input.csv
├── remote-catalog/
│   ├── remote-catalog.json
│   └── remote-catalog.sha256
├── cache/
│   ├── blocks/
│   └── downloads/
├── acquired/
├── extracted/
├── normalized/
├── metadata/
├── splits/
├── derived/
└── evidence/
```

## 4. Quy tắc ownership

| Artifact | ZONE 1 | ZONE 2 | SSOT |
|---|---:|---:|---|
| Code/schema/config | Có | Có thể tham chiếu | ZONE 1 |
| Source/license record | Có | Snapshot tùy chọn | ZONE 1 |
| Remote object catalog đầy đủ | Rút gọn/hash | Có | ZONE 2 |
| Raw/archive | Không | Có điều kiện | ZONE 2 |
| Cache | Không | Có, xóa được | ZONE 2 |
| Metadata index lớn | Hash/ref | Có | ZONE 2 |
| Evidence đầy đủ | Compact subset | Có | ZONE 2 |
| Readiness decision | Có | Có | Hai bản phải cùng hash |

## 5. Không dùng symlink raw vào repo

Symlink có thể khiến tooling, backup hoặc IDE vô tình quét dữ liệu lớn. Ưu tiên config absolute path. Nếu bắt buộc có pointer, dùng file text ignored:

```text
.local-data-root
```

Nội dung:

```text
/home/duyvd9/massive/projects/semg-fatigue/myolab-ai-data
```

## 6. Cache budget

Ví dụ:

```yaml
cache:
  max_bytes: 10737418240  # 10 GiB
  eviction: lru
  checksum_on_complete_object: true
  partial_block_trust: temporary_only
```

Cache không phải source of truth. Xóa cache không được làm mất provenance hoặc readiness decision.

## 7. Backup

- ZONE 1: Git remote + release archive.
- ZONE 2 source/acquired: backup theo checksum nếu đã tải toàn bộ.
- ZONE 2 cache/temp: không cần backup.
- Evidence và split/test seal: phải backup.
- Không backup PHI lên nơi không được phê duyệt; public datasets vẫn phải theo license.
