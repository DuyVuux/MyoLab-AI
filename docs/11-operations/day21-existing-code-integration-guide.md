# Hướng dẫn tích hợp Day 21 không ghi đè file cũ

1. Giữ nguyên `day20_app.py` và `AppRouter.tsx` đang chạy.
2. Mount router từ `routes/analysis_jobs.py` vào application factory hiện tại.
3. Thêm route fragment từ `Day21AnalysisRoutes.tsx` bằng cách copy riêng phần `<Route>`; không thay cả router.
4. Thay deterministic runtime bằng `SubprocessOfflineAnalysisRuntime` chỉ khi Day 15 CLI và Day 17 builder đã có trong repo.
5. Trong production, worker tự cập nhật stage; endpoint `/advance` chỉ tồn tại khi feature flag dev bật.
