from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


IGNORED_INFRA_DIRS = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "env",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "dist",
        "build",
    }
)


@dataclass(frozen=True)
class FamilyRule:
    family_id: str
    patterns: tuple[re.Pattern[str], ...]


RULES = (
    FamilyRule("LA-05", (re.compile(r"gesture", re.I), re.compile(r"grabmyo.*baseline", re.I), re.compile(r"14[-_]?feature", re.I))),
    FamilyRule("LA-06", (re.compile(r"personalization", re.I), re.compile(r"few[-_]?shot", re.I))),
    FamilyRule("LA-07", (re.compile(r"confidence", re.I), re.compile(r"calibration.*abstention", re.I))),
    FamilyRule("LA-08", (re.compile(r"fatigue[_-]?context", re.I), re.compile(r"fatigue.*evidence", re.I))),
    FamilyRule("LA-09", (re.compile(r"fatigue.*classifier", re.I), re.compile(r"binary.*fatigue", re.I))),
    FamilyRule("LA-10", (re.compile(r"mfcv", re.I), re.compile(r"conduction[_-]?velocity", re.I))),
    FamilyRule("LA-11", (re.compile(r"taskc", re.I), re.compile(r"quantitative", re.I), re.compile(r"co[-_]?contraction", re.I))),
    FamilyRule("LA-12", (re.compile(r"cross[-_]?dataset", re.I), re.compile(r"transfer", re.I))),
    FamilyRule("LA-15", (re.compile(r"apps/web-portal", re.I),)),
    FamilyRule("LA-19", (re.compile(r"lower[-_]?limb.*(20|roadmap)", re.I), re.compile(r"20[-_]?day.*lower", re.I))),
    FamilyRule("LA-20", (re.compile(r"pre[-_]?day41", re.I),)),
    FamilyRule("LA-17", (re.compile(r"model[_-]?registry", re.I), re.compile(r"environment[-_]?lock", re.I), re.compile(r"reproduc", re.I))),
    FamilyRule("LA-03", (re.compile(r"preprocess", re.I), re.compile(r"windowing", re.I))),
    FamilyRule("LA-04", (re.compile(r"\b(rms|mav|mdf|mnf)\b", re.I),)),
    FamilyRule("LA-16", (re.compile(r"human[-_]?review", re.I), re.compile(r"review.*audit", re.I))),
    FamilyRule("LA-13", (re.compile(r"offline.*pipeline", re.I), re.compile(r"run_offline_pipeline", re.I))),
    FamilyRule("LA-14", (re.compile(r"common-schemas", re.I), re.compile(r"openapi", re.I))),
    FamilyRule("LA-02", (re.compile(r"\bqc\b", re.I), re.compile(r"signal[_-]?quality", re.I), re.compile(r"abstention_reason", re.I))),
    FamilyRule("LA-01", (re.compile(r"csv.*adapter", re.I), re.compile(r"source_record", re.I), re.compile(r"ingest", re.I))),
)

LEGACY_HINT = re.compile(
    r"(day([2-9]|[12][0-9]|3[0-9]|40)|pre[-_]?day41|gesture|fatigue|mfcv|personalization|cross[-_]?dataset|taskc|quantitative|model[_-]?registry|lower[-_]?limb)",
    re.I,
)


def tracked_files(root: Path) -> list[Path] | None:
    if not (root / ".git").exists():
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    names = [name for name in result.stdout.decode("utf-8").split("\0") if name]
    return [Path(name) for name in names]


def walk_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            dirname for dirname in dirnames if dirname not in IGNORED_INFRA_DIRS
        )
        current = Path(current_root)
        relative_parts = current.relative_to(root).parts
        if any(part in {"raw", "datasets"} for part in relative_parts):
            dirnames[:] = []
            continue
        for filename in sorted(filenames):
            files.append((current / filename).relative_to(root))
    return files


def classify(path: Path) -> str | None:
    text = path.as_posix()
    for rule in RULES:
        if any(pattern.search(text) for pattern in rule.patterns):
            return rule.family_id
    return None


def audit(paths: Iterable[Path]) -> dict[str, object]:
    classified: dict[str, list[str]] = {}
    unclassified: list[str] = []
    candidates = 0
    for path in sorted(paths, key=lambda item: item.as_posix()):
        text = path.as_posix()
        family = classify(path)
        if family:
            classified.setdefault(family, []).append(text)
            candidates += 1
        elif LEGACY_HINT.search(text):
            unclassified.append(text)
            candidates += 1
    return {
        "schema_version": "1.0",
        "candidate_count": candidates,
        "classified_family_count": len(classified),
        "classified": classified,
        "unclassified_candidates": unclassified,
        "unclassified_count": len(unclassified),
        "repo_confirmation_complete": len(unclassified) == 0 and candidates > 0,
        "note": "Classification is path-based triage. Human review must confirm semantic disposition before GO_FOR_DAY_08.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit tracked/current legacy asset paths for DAY07.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    paths = tracked_files(root)
    source = "git_ls_files"
    if paths is None:
        paths = walk_files(root)
        source = "os_walk_fallback"

    report = audit(paths)
    report["scan_source"] = source
    report["root"] = str(root)

    output = args.output
    if not output.is_absolute():
        output = root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "candidate_count": report["candidate_count"],
        "unclassified_count": report["unclassified_count"],
        "scan_source": source,
        "output": str(output),
    }, sort_keys=True))

    if args.strict and not report["repo_confirmation_complete"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
