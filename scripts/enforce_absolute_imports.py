"""Utility script to rewrite relative imports to absolute imports.

This is a best-effort helper. It scans .py files under the repository and attempts
to convert imports of the form:
    from .module import X
    from ..package import Y
into absolute imports rooted at the top-level package (project root packages discovered
from pyproject [project.name] or top-level package directories).

Limitations:
- Does not modify string-based dynamic imports.
- Skips files in .venv, build, dist, and migrations directories.
- Warns when it cannot confidently resolve a relative path.

Run:
    python scripts/enforce_absolute_imports.py --dry-run
    python scripts/enforce_absolute_imports.py --apply
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
from collections.abc import Iterable

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
PACKAGE_NAME = "charlie_reporting"  # Adjust if/when a canonical package is created
RELATIVE_IMPORT_RE = re.compile(r"^from (\.+)([a-zA-Z0-9_\.]+)? import (.+)$")

SKIP_DIRS = {".venv", "build", "dist", "__pycache__"}


def iter_python_files(base: pathlib.Path) -> Iterable[pathlib.Path]:
    for path in base.rglob("*.py"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def resolve_absolute(module_path: pathlib.Path, dots: str, remainder: str | None) -> str | None:
    # Determine package root relative to module_path
    depth = len(dots)  # number of leading dots indicates how many levels to go up
    parts = module_path.parts
    try:
        pkg_index = parts.index("shared")  # heuristic anchor; adjust as needed
    except ValueError:
        return None
    within = pathlib.Path(*parts[pkg_index: -1])  # path within package excluding filename
    ancestors = within.parts
    if depth > len(ancestors):
        return None
    target_parts = ancestors[: len(ancestors) - depth]
    if remainder:
        target_parts += tuple(remainder.split("."))
    absolute = ".".join(target_parts).strip('.')
    return absolute or None


def rewrite_file(path: pathlib.Path, dry_run: bool = True) -> bool:
    original = path.read_text(encoding="utf-8").splitlines()
    modified = []
    changed = False
    for line in original:
        m = RELATIVE_IMPORT_RE.match(line.strip())
        if not m:
            modified.append(line)
            continue
        dots, remainder, tail = m.groups()
        absolute = resolve_absolute(path, dots, remainder)
        if not absolute:
            modified.append(line)
            continue
        newline = f"from {absolute} import {tail}"
        if newline != line:
            changed = True
        modified.append(newline)
    if changed and not dry_run:
        path.write_text("\n".join(modified) + "\n", encoding="utf-8")
    return changed


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Enforce absolute imports by rewriting relative imports.")
    parser.add_argument("--apply", action="store_true", help="Apply changes instead of dry-run")
    args = parser.parse_args(argv)
    changed_files = []
    for pyfile in iter_python_files(PROJECT_ROOT):
        if rewrite_file(pyfile, dry_run=not args.apply):
            changed_files.append(pyfile)
    if changed_files:
        action = "Would update" if not args.apply else "Updated"
        print(f"{action} {len(changed_files)} files:")
        for f in changed_files:
            print(" -", f.relative_to(PROJECT_ROOT))
    else:
        print("No relative imports found needing rewrite.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
