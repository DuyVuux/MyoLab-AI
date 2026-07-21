# Acceptance Criteria — Day 5

- [ ] `preprocess_v0.1.yaml` hợp lệ và có version.
- [ ] Pipeline block khi QC không cho phép.
- [ ] Không nội suy NaN/Inf.
- [ ] Band-pass 20–400 Hz dùng Butterworth SOS và `sosfiltfilt`.
- [ ] Notch 50 Hz chỉ chạy khi có `POWERLINE_NOISE_HIGH`.
- [ ] Resampling, rectification và envelope bị tắt.
- [ ] Time axis, sample count, channel identity và unit được giữ nguyên.
- [ ] Output arrays read-only trong in-memory contract.
- [ ] Output summary không chứa raw arrays.
- [ ] Golden, powerline warning và QC-fail fixtures có hành vi đúng.
- [ ] Output hash deterministic.
- [ ] JSON evidence khớp schema.
- [ ] Tất cả markdown Day 5 viết bằng tiếng Việt.
- [ ] `bash scripts/dev/run_day5_checks.sh` trả exit code 0.
