# Input contract Day 29

Day 29 không đọc raw GRABMyo bằng schema suy đoán. Nó nhận **canonical record index** từ lớp ingestion/mapping của Day 27-equivalent.

## Required metadata columns

| Cột | Ý nghĩa |
|---|---|
| `record_id` | ID immutable của record |
| `subject_id` | group key người tham gia |
| `day_id` | ngày/session thu |
| `session_id` | session cụ thể |
| `repetition_id` | lần lặp atomic |
| `source_label` | nhãn gốc |
| `canonical_label` | ontology dự án |
| `partition` | train/validation/test |
| `signal_path` | canonical signal path |
| `sampling_rate_hz` | sampling rate đã xác minh |
| `signal_unit` | V/mV/uV... đã xác minh |
| `channel_count` | số kênh observed/expected |

Signal path của test có thể tồn tại trong sealed manifest nhưng không được đưa vào EDA index visible.
