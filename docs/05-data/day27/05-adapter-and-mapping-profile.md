# Adapter và mapping profile

Downstream chỉ nhận canonical signal. Source-specific uncertainty nằm trong mapping profile/adapter.

Required profile fields:

```text
format, glob, delimiter/encoding nếu có,
sampling rate, unit, raw/processed,
channel source fields, canonical order,
subject/session/repetition extraction,
label source.
```

Profile còn `NOT_VERIFIED` hoặc placeholder không được dùng cho canonical conversion.
