---
name: flutter-theme-migration
description: Comprehensive workflow and checklist for migrating Flutter apps to a dynamic Light/Dark theme. Ensures zero hardcoded colors across all UI levels without missing sub-widgets.
---

# 🎨 Flutter Theme Migration & Stress Fix Protocol

## 1. Core Principle: "Deep Audit, Not Surface Fix"
When tasked with implementing or fixing a Dark/Light Theme for a screen, **never stop at the top-level Widget**. Modern Flutter apps are highly modular. You must recursively audit and refactor all sub-components, dialogs, bottom sheets, and raw widgets imported into the main screen.

## 2. The Strict Validation Rule (Zero Hardcoded Colors)
Before considering a theme migration task "Done", you MUST run a project-wide or feature-wide `grep_search` to guarantee the eradication of all static color declarations.
**Forbidden Patterns:**
- `Colors.white`, `Colors.black`, `Colors.grey`, etc.
- `Color(0xFF...)` or `Color.fromARGB(...)`
- `Colors.transparent` is the ONLY exception when logically required.

## 3. The Migration Workflow

### Phase 1: Establish the Source of Truth
Determine the project's design token architecture.
- Does it use standard `Theme.of(context).colorScheme`?
- Does it use a custom semantic dictionary (e.g., `AppTheme.of(context).resources`)?
**Action:** Inject this source of truth at the top of the `build` method for *every* widget modified.

### Phase 2: Recursive Sub-Widget Identification
Do not wait for the user to point out missed widgets.
1. Read the main screen's `build` method.
2. List all custom widgets, dialog calls (`showDialog`, `showModalBottomSheet`), and tabs.
3. Open every single dependent file.

### Phase 3: Targeted Replacement Areas (The Blind Spots)
Always thoroughly check these highly susceptible components:
- **Scaffolds & Containers:** `backgroundColor`, `color`.
- **AppBars:** `backgroundColor`, `foregroundColor`, `bottom` borders.
- **Typography:** `TextStyle(color: ...)` across titles, subtitles, and hints.
- **Form Controls:** 
  - `InputDecoration` (borders, fill colors, hint colors).
  - `DropdownButtonFormField` (`dropdownColor`, icons).
- **Modals & Dialogs:** Nested builders in `showDialog` often construct their own `Dialog` or `Container` with hardcoded `Colors.white`.
- **Dividers & Borders:** `Divider(color: ...)`, `Border.all(color: ...)`.
- **Interactive Elements:** `ElevatedButton.styleFrom`, Checkboxes, Segmented Controls.

### Phase 4: Self-Verification
Before replying to the user, execute:
```bash
grep -rnw 'lib/features/your_feature' -e 'Colors\.' -e 'Color(0x'
```
If this command returns unhandled static colors, **do not hand over the task**. Fix them immediately.

## 4. Execution Mindset (The "Do It Once, Do It Right" Standard)
- **Proactive rather than Reactive:** Act as a Senior Architectural Reviewer. Anticipate where previous engineers might have lazily hardcoded `Colors.white` and root it out.
- **Semantic Mapping:** Map colors not based on their original hex value, but on their semantic purpose (`cardBackgroundFillColorDefault`, `textFillColorSecondary`, etc.).

---
*Generated based on systematic lessons learned from persistent UI debugging iterations.*
