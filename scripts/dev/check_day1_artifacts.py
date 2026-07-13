from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
required_files = [
    "README.md",
    "docs/00-executive/executive-blueprint.md",
    "docs/00-executive/stakeholder-decision-log.md",
    "docs/00-executive/assumptions-and-open-questions.md",
    "docs/01-product/intended-use-statement.md",
    "docs/01-product/product-boundaries.md",
    "docs/01-product/mvp-definition-of-done.md",
    "docs/01-product/backlog/day1-backlog.md",
    "docs/03-architecture/high-level-architecture.md",
    "docs/03-architecture/adr/ADR-0001-clinical-intelligence-not-device.md",
    "docs/03-architecture/adr/ADR-0002-offline-first-before-realtime.md",
    "docs/07-security-compliance/medical-disclaimer.md",
    "reports/wording/prohibited-claims.md",
    "reports/wording/clinical-interpretation-phrases.md",
    "product/ux/copy/demo-rewrite-notes.md",
    "ops/cadence/day1-self-review.md",
    "qa-validation/requirements/day1-acceptance-criteria.md",
]

must_include = [
    "Clinical Intelligence",
    "not",
    "quality",
    "abstention",
    "human",
    "MFCV",
]

missing = []
weak_content = []
for rel in required_files:
    path = ROOT / rel
    if not path.exists():
        missing.append(rel)
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    if rel in {
        "README.md",
        "docs/00-executive/executive-blueprint.md",
        "docs/01-product/intended-use-statement.md",
        "docs/01-product/product-boundaries.md",
    }:
        absent = [term for term in must_include if term.lower() not in text.lower()]
        if absent:
            weak_content.append((rel, absent))

if missing:
    print("MISSING FILES:")
    for item in missing:
        print(f" - {item}")
if weak_content:
    print("\nWEAK CONTENT:")
    for rel, absent in weak_content:
        print(f" - {rel}: missing terms {absent}")

if missing or weak_content:
    raise SystemExit(1)

print("Day 1 artifact check PASSED.")
print(f"Checked {len(required_files)} required files under: {ROOT}")
