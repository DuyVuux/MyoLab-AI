---
description: 
---

# Operational Workflows (SOPs)

> High-level sequences for complex development tasks.

## System Onboarding

- **Mục tiêu:** Giúp AI hoặc Dev mới nắm bắt dự án trong 30 giây.
- **Quy trình:**
    1. Chạy `/understand` để đảm bảo dữ liệu mới nhất.
    2. Chạy `/understand-onboard` để lấy bức tranh tổng thể.
    3. Mở `/understand-dashboard` để trực quan hóa các module chính.

## Safe Refactor

- **Mục tiêu:** Thay đổi cấu trúc code mà không làm sập hệ thống.
- **Quy trình:**
    1. **Identify:** `/understand-chat` để tìm tất cả các nơi đang phụ thuộc vào code sắp sửa.
    2. **Analyze:** `/understand-explain` trên các module bị ảnh hưởng nhất.
    3. **Execute:** Thực hiện sửa code.
    4. **Verify:** Chạy `/understand-diff` để kiểm tra các tác động ngoài ý muốn.
    5. **Finalize:** Chạy `/understand` để cập nhật lại "bản đồ" tri thức mới.

## Root Cause Analysis (RCA)

- **Mục tiêu:** Truy vết nguyên nhân gốc rễ của bug logic.
- **Quy trình:**
    1. Sử dụng `/understand-chat` để map luồng dữ liệu từ điểm lỗi ngược về nguồn.
    2. Sử dụng `/understand-explain` tại các nút giao (nodes) quan trọng trên đồ thị.
    3. Kiểm tra tính toàn vẹn của Domain bằng `/understand-domain`.