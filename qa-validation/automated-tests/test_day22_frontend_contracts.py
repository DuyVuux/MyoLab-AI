from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WEB_SRC = ROOT / "apps/web-portal/src"
UC1_ROUTE = (
    WEB_SRC
    / "app/(authenticated)/uc1/session/[sessionId]/page.tsx"
)
UC1_COMPONENTS = WEB_SRC / "components/uc1"


def read_required(relative_path: str) -> str:
    path = ROOT / relative_path
    assert path.is_file(), f"Missing required Day 22 artifact: {relative_path}"
    return path.read_text(encoding="utf-8")


def day22_ui_sources() -> list[Path]:
    component_sources = (
        sorted(UC1_COMPONENTS.rglob("*.tsx"))
        if UC1_COMPONENTS.is_dir()
        else []
    )
    return [UC1_ROUTE, *component_sources]


def test_day22_frontend_structure_exists() -> None:
    required = [
        "apps/web-portal/src/schemas/gesture-inference.schema.ts",
        "apps/web-portal/src/schemas/gesture-feedback-context.schema.ts",
        "apps/web-portal/src/lib/latencyMetrics.ts",
        "apps/web-portal/src/lib/uc1-replay-client.ts",
        "apps/web-portal/src/hooks/useUC1Replay.ts",
        "apps/web-portal/src/utils/replayView.ts",
        "apps/web-portal/src/components/uc1/UC1SessionWorkspace.tsx",
        "apps/web-portal/src/components/uc1/GestureHistoryTable.tsx",
        "apps/web-portal/src/app/(authenticated)/uc1/session/[sessionId]/page.tsx",
    ]

    missing = [path for path in required if not (ROOT / path).is_file()]
    assert not missing, "Missing Day 22 frontend files:\n- " + "\n- ".join(missing)


def test_day22_typescript_configs_use_real_next_surface() -> None:
    config_path = ROOT / "qa-validation/configs/day22_tsconfig.json"
    runtime_path = ROOT / "qa-validation/configs/day22_runtime_tsconfig.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    runtime = json.loads(runtime_path.read_text(encoding="utf-8"))

    includes = set(config["include"])
    assert (
        "../../apps/web-portal/src/app/(authenticated)/uc1/**/*.tsx"
        in includes
    )
    assert "../../apps/web-portal/src/hooks/useUC1Replay.ts" in includes
    assert "../../apps/web-portal/src/components/uc1/**/*.tsx" in includes
    assert not any("vendor_stubs" in path for path in includes)
    assert "react-router-dom" not in config_path.read_text(encoding="utf-8")

    runtime_includes = set(runtime["include"])
    assert "../../apps/web-portal/src/lib/latencyMetrics.ts" in runtime_includes
    assert "../../apps/web-portal/src/utils/replayView.ts" in runtime_includes
    assert (
        "../../apps/web-portal/src/schemas/gesture-feedback-context.schema.ts"
        in runtime_includes
    )


def test_real_uc1_route_mounts_day22_workspace_instead_of_inline_mock() -> None:
    source = UC1_ROUTE.read_text(encoding="utf-8")

    assert "UC1SessionWorkspace" in source
    assert "@/components/uc1/" in source
    assert "generateMockSegments" not in source
    assert "MockWorkflowRepository.getSegments" not in source


def test_uc1_session_surface_removes_nondeterministic_and_unsafe_copy() -> None:
    sources = day22_ui_sources()
    combined = "\n".join(path.read_text(encoding="utf-8") for path in sources)
    lowered = combined.casefold()

    forbidden = {
        "date.now(": "deterministic replay must not create time-based IDs",
        "% conf": "engineering confidence must be categorical, not percentage copy",
        "fatigueindex": "the legacy simulated fatigue index must not drive Day 22 UI",
        "real-time": "Day 22 is deterministic offline replay",
        "thời gian thực": "Day 22 must not claim live/real-time behavior",
        "phát hiện dấu hiệu mỏi cơ cao": "UI must not diagnose fatigue",
    }
    violations = [
        f"{token}: {reason}"
        for token, reason in forbidden.items()
        if token in lowered
    ]
    assert not violations, "Unsafe UC1 Day 22 source copy:\n- " + "\n- ".join(
        violations
    )


def test_gesture_history_table_has_accessible_headers_and_caption() -> None:
    source = read_required(
        "apps/web-portal/src/components/uc1/GestureHistoryTable.tsx"
    )

    assert re.search(r"<caption(?:\s|>)", source, flags=re.IGNORECASE)
    assert re.search(
        r"\bscope\s*=\s*[\"']col[\"']",
        source,
        flags=re.IGNORECASE,
    )


def test_uc1_workspace_does_not_nest_main_landmarks() -> None:
    sources = day22_ui_sources()
    nested_main_sources = [
        str(path.relative_to(ROOT))
        for path in sources
        if re.search(r"<main(?:\s|>)", path.read_text(encoding="utf-8"))
    ]

    assert not nested_main_sources, (
        "AppShell already owns the main landmark; remove nested <main> from:\n- "
        + "\n- ".join(nested_main_sources)
    )


def test_exact_window_feedback_uses_server_provenance() -> None:
    inference_schema = read_required(
        "apps/web-portal/src/schemas/gesture-inference.schema.ts"
    )
    feedback_schema = read_required(
        "apps/web-portal/src/schemas/gesture-feedback-context.schema.ts"
    )

    assert "modelVersion" in inference_schema
    assert "resultHashSha256" in inference_schema
    assert "window.modelVersion" in feedback_schema
    assert "window.resultHashSha256" in feedback_schema
    assert "gesture-replay-v0.1-not-validated" not in feedback_schema
    assert "`result:${window.windowId}`" not in feedback_schema


def test_day22_frontend_does_not_import_react_router() -> None:
    offenders = [
        str(path.relative_to(ROOT))
        for path in day22_ui_sources()
        if "react-router-dom" in path.read_text(encoding="utf-8")
    ]
    assert not offenders, "Next App Router surface imports react-router-dom: " + ", ".join(
        offenders
    )


def test_feedback_controls_use_existing_action_rbac() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in day22_ui_sources()
    )

    assert "canPerformAction" in combined
    assert "submit_feedback" in combined
    assert "useAuth" in combined
