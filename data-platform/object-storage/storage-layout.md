# Object Storage Layout Specification — MyoLab-AI

Tài liệu này định nghĩa cấu trúc phân cấp lưu trữ cho hệ thống Object Storage (MinIO / AWS S3) trong hệ sinh thái **MyoLab-AI**.

---

## 1. Bucket Hierarchy

| Bucket Name | Quyền truy cập | Mục đích | Lifecycle Policy |
| :--- | :--- | :--- | :--- |
| `myolab-raw-vault` | Read-only / WORM | Lưu trữ file raw gốc (Noraxon MR4, PhysioNet WFDB, Zenodo ZIP). Bất biến (Immutable). | Không xóa |
| `myolab-lakehouse` | Internal Services | Lưu trữ Bronze, Silver, Gold Parquet và Feature Tables. | Retention theo version |
| `myolab-artifacts` | Public / Authorized | Lưu trữ Model weights, Evaluation reports, ROC curves, Handoff ZIPs. | 365 days |
| `myolab-scratch` | Read / Write | Cache trung gian, chunk blocks khi streaming EDA. | Auto-expire sau 7 ngày |

---

## 2. Đường dẫn Object Key Chuẩn

### `myolab-raw-vault/`
```text
myolab-raw-vault/
├── clinical/
│   └── vinmec/
│       └── session_{session_id}/
│           ├── raw_signal_{signal_id}.csv
│           └── session_metadata.json
└── external/
    ├── grabmyo-v1.1.0/
    │   └── session_{session_id}_participant_{sub_id}.dat
    ├── mendeley-4channel-hand-gesture-v2/
    │   └── raw_{gesture_id}_trial_{trial_id}.mat
    └── hyser-v2.0.0/
```

### `myolab-lakehouse/`
```text
myolab-lakehouse/
├── bronze/
│   └── {source}/
│       └── {dataset_id}/
│           └── year={YYYY}/month={MM}/
│               └── {record_id}_bronze.parquet
├── silver/
│   └── normalized/
│       └── {dataset_id}/
│           └── {record_id}_filtered.parquet
└── gold/
    ├── feature_tables/
    │   └── version={version}/
    │       └── {view_id}.parquet
    └── longitudinal/
        └── patient_{patient_id}/
            └── metrics_history.parquet
```

### `myolab-artifacts/`
```text
myolab-artifacts/
├── models/
│   └── {model_id}/
│       ├── model.joblib
│       ├── feature_manifest.json
│       └── calibration_bundle.joblib
└── evidence/
    └── {gate_id}/
        ├── gate_decision.yaml
        └── evaluation_summary.json
```
