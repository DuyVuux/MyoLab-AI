# Chính sách chất lượng nhãn v0.2

## Mức chất lượng

| Mức | Nguồn | Training mặc định |
|---|---|---:|
| Q0 | Không rõ nguồn | Không |
| Q1 | Cue-only | Không cho clinical model; research có cờ |
| Q2 | Cue + event/kinematics | Có điều kiện |
| Q3 | KTV reviewed | Có điều kiện |
| Q4 | Clinical adjudicated | Ưu tiên |

## Conflict

Khi hai reviewer không đồng thuận:

```text
label_status = disputed
training_eligible = false
```

cho tới adjudication.
