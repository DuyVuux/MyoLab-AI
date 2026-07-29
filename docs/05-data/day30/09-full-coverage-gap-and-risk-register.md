# Coverage gap và risk register

| Risk | Evidence | Control |
|---|---|---|
| EDA chưa bao phủ toàn bộ subjects | 29/43 và 9/25 theo báo cáo | phân biệt smoke/full baseline |
| CH4 chưa rõ | std thấp hơn nhiều | quarantine + sensitivity |
| Source shortcut | amplitude/channel count khác | separate models; pooled blocked |
| Sampling mismatch | 2048/2000 | native-rate primary |
| Ontology mismatch | 17/10 | computed intersection |
| Cross-day mismatch | chỉ GRABMyo có | regime tách riêng |
| Hidden leakage | overlapping windows/scaler | split-first, inner-fold fitting |
