# Tích hợp runtime Day 21

```text
Session/Import/Mapping/Calibration/QC
→ Analysis handoff
→ AnalysisJob
→ Offline runtime adapter
→ Day 15 analysis package
→ Day 17 canonical summary
→ Frontend polling/timeline
```

Prototype dùng deterministic runtime. `SubprocessOfflineAnalysisRuntime` là adapter sẵn để gọi pipeline Day 15 và summary builder Day 17 khi source manifest đã được đăng ký phía server.
