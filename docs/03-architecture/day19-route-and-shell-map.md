# Route và AppShell map Day 19

```text
AppRouter
├── Public: /login
└── AppShell
    ├── /dashboard
    ├── /use-cases
    ├── /sessions
    ├── /analyses
    ├── /feedback/inbox
    ├── /uc3/feasibility
    └── /uc4/feasibility
```

Compatibility redirects:

```text
/uc1/demo -> /uc1/session/DEMO-UC1-001
/uc2/demo -> /uc2/assessment/DEMO-UC2-001
```

Client-side RoleGuard chỉ điều khiển UX. Backend vẫn phải kiểm tra authorization cho mọi API có dữ liệu hoặc action nhạy cảm.
