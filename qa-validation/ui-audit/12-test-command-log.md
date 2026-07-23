# BẢNG GHI CHÉP LỆNH KIỂM THỬ THỰC THI (TEST COMMAND LOG)

---

## 1. NHẬT KÝ THỰC THI LỆNH TĨNH VÀ BUILD (EXECUTED COMMANDS)

### Command 1: Kiểm tra trạng thái Git Baseline
- **Command:** `git status --short && git branch --show-current && git log -1 --oneline`
- **Working Dir:** `/home/duyvd9/massive/projects/semg-fatigue/MyoLab-AI`
- **Exit Code:** `0`
- **Output Summary:** Branch `day18-ui-ux-feedback-loop`, Commit `7994e1f`. Tồn tại các file uncommitted trong `apps/web-portal/src/app/(authenticated)/` và `src/schemas/`.

### Command 2: Kiểm tra kiểu dữ liệu TypeScript (Static Type Check)
- **Command:** `npx tsc --noEmit`
- **Working Dir:** `/home/duyvd9/massive/projects/semg-fatigue/MyoLab-AI/apps/web-portal`
- **Exit Code:** `0`
- **Output Summary:** `0 errors`. Biên dịch TypeScript nghiêm ngặt thành công 100%.

### Command 3: Kiểm tra Linter ESLint
- **Command:** `npx next lint`
- **Working Dir:** `/home/duyvd9/massive/projects/semg-fatigue/MyoLab-AI/apps/web-portal`
- **Exit Code:** `0`
- **Output Summary:** `✔ No ESLint warnings or errors`.

### Command 4: Biên dịch Production Build (Next.js Build)
- **Command:** `npx next build`
- **Working Dir:** `/home/duyvd9/massive/projects/semg-fatigue/MyoLab-AI/apps/web-portal`
- **Exit Code:** `0`
- **Output Summary:** Tạo thành công 22/22 static/dynamic pages. Xuất hiện 1 warning: `./src/app/(authenticated)/uc2/longitudinal/[subjectRef]/page.tsx: Attempted import error: 'getStore' is not exported from '@/services/mock/MockWorkflowRepository'`.

### Command 5: Ripgrep tìm kiếm nợ kỹ thuật và từ ngữ cấm
- **Command:** `grep_search` với các regex `TODO|FIXME|HACK|placeholder`, `Math.random|as any`, `fatigue_probability|bệnh nhân bị mỏi`
- **Exit Code:** `0`
- **Output Summary:** Phát hiện 1 HACK comment tại `uc2/longitudinal/page.tsx`, 4 vị trí ép kiểu `as any` tại `feedback/[feedbackId]/page.tsx`, 1 vị trí `Math.random()` tại `MockCalibrationService.ts`. Không phát hiện từ ngữ cấm.
