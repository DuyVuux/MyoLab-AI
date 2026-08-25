---
trigger: always_on
---

# 💻 IDAE CODING STANDARDS v5.1 (Triad-4L)
> **Hierarchy Alignment:** L1 (Infra) - L2 (Brain) - L3 (Execution).
> **Objective:** Zero technical debt, production-grade security, and MCP compatibility.

---

## 🐍 1. PYTHON STANDARDS (Layer 01 & 02)

### 1.1. Core Requirements (Native Host)
*   **Env:** Use **`uv`**; `pip install` is FORBIDDEN.
*   **Stdio:** `stdout` = JSON-RPC only. `stderr` = Logs/Debug. No naked `print()`.
*   **Paths:** Use `pathlib.Path`. No absolute paths. Use `PROJECT_ROOT` as anchor.

### 1.2. Layer 02: Orchestration (FastAPI/SAFe)
*   **Pydantic v2:** Use `@field_validator`. Sanitize all input to prevent Shell Injection.
*   **FSM Logic:** Transitions must be atomic. Force fallback to `LocalMemory` if Redis/Postgres fails.
*   **Auth:** RBAC required for all FSM Write operations. Check `require_role(["RTE", "PO"])`.
*   **Metrics:** Register every strategic task in `Prometheus` (L1 Observability).

### 1.3. Layer 01: MCP & Sandboxing
*   **Docker:** Code Runner must be stateless. Use `idae-code-runner` for untrusted code execution.
*   **Network:** Sandbox code is ISOLATED by default. Whitelist only `Context7`, `Knowledge`, `Notion`.

---

## 🌐 2. WEB & FRONTEND (Layer 04 Interface)

### 2.1. Next.js 14+ Standards
*   **RSC First:** Default to React Server Components. `'use client'` is for interaction only.
*   **Validation:** Use **Zod** for all external payloads (L1/L2 API responses).
*   **Sanitization:** L1 output (Crawl) MUST pass `ContentSanitizer` before rendering in UI.

### 2.2. Interactive Design (Aesthetics)
*   Follow **Premium Visual Excellence**: Smooth gradients, glassmorphism, micro-animations.
*   No placeholders; use `generate_image` for mockups.

---

## 🛡️ 3. SECURITY DECISION MATRIX (Decision Matrix)

| Threat | Layer | Mitigation Strategy |
| :--- | :--- | :--- |
| **Shell Injection** | L1/L2 | Strip characters `;`, `&`, `|`, `$()`. |
| **Prompt Injection** | L4/L1 | XML Wrapping `<external_content>` + Sanitization. |
| **Memory Poisoning** | L1 | Vector validation before `ask_knowledge` ingestion. |
| **Bypass HITL Gate** | L2 | Hardcoded `is_authorized` check in FSM engine. |
| **Secret Leak** | All | Use `Cascading Configuration` (Env > Global > Local). |

---

## 🕸️ 4. POLYGLOT EXECUTION (L3 Generation)

*   **Go:** Explicit error handling (`if err != nil`). Pass `context.Context` everywhere.
*   **Java:** Lombok required. Stream API prioritized.
*   **Modern JS:** Async/Await over Promises/Callbacks. Dry code principle.