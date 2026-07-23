# Kiến trúc frontend và mock integration

```text
React pages
    ↓
Typed mock API client
    ↓
Stable frontend contracts
    ↓
Deterministic mock service / optional FastAPI mock
    ↓
Fixed synthetic fixtures
```

Component không được import trực tiếp mutable fixture store. Sau này có thể thay `mock-api-client.ts` bằng HTTP client mà không đổi page contract.
