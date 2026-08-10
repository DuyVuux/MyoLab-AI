from __future__ import annotations
from pathlib import Path

def scan_project_files(root_dir: Path, extra_skip_dirs: set[str] | None = None) -> list[Path]:
    """Scans the project directory, skipping specified directories and honoring specific whitelists."""
    skip_dirs = {"__pycache__", ".pytest_cache", ".venv", "env", ".git", "node_modules", "raw", "datasets", "experiments", "fixtures"}
    if extra_skip_dirs:
        skip_dirs.update(extra_skip_dirs)
        
    found_files = []
    
    for path in root_dir.rglob("*"):
        if not path.is_file():
            continue
        
        # Check if file is in a skipped directory
        is_skipped = False
        for parent in path.parents:
            if parent.name in skip_dirs:
                is_skipped = True
                break
        
        if is_skipped:
            continue
            
        found_files.append(path)
        
    return found_files
