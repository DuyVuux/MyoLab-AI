# Hướng dẫn tích hợp Day 19 vào UI hiện có

1. Không ghi đè `App.jsx`, `UC1Dashboard.jsx`, `UC2Dashboard.jsx` khi chưa diff.
2. Merge `tokens.css` vào design tokens hiện tại, ưu tiên giữ token name canonical.
3. Import `useCaseRoutes.ts` thay cho duplicate route/content arrays.
4. Đưa `AppShell` bao quanh các route đã đăng nhập.
5. Giữ UC1/UC2 hiện có và thêm compatibility redirect.
6. Dùng `mock-api-client.ts` trong development feature flag; production client phải dùng OpenAPI client thật.
7. UC3/UC4 chỉ dùng feasibility pages trong gói này.
