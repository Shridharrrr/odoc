from __future__ import annotations

import sys
from fnmatch import fnmatch
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

DEFAULT_EXCLUDES = [
    ".git/*",
    ".hg/*",
    ".mypy_cache/*",
    ".pytest_cache/*",
    ".ruff_cache/*",
    ".tox/*",
    ".venv/*",
    "venv/*",
    "__pycache__/*",
    "*/__pycache__/*",
    "build/*",
    "dist/*",
    "site/*",
]


def find_python_files(start_path: Path, exclude_patterns: list[str] | None = None) -> list[Path]:
    """Find .py files recursively while respecting glob-style exclude patterns."""
    start_path = start_path.resolve()
    patterns = [*DEFAULT_EXCLUDES, *(exclude_patterns or [])]

    if start_path.is_file():
        if start_path.suffix == ".py" and not is_excluded(start_path, start_path.parent, patterns):
            return [start_path]
        return []

    files = []
    for file in start_path.rglob("*.py"):
        if not is_excluded(file, start_path, patterns):
            files.append(file)
    return sorted(files)


def is_excluded(path: Path, root: Path, patterns: list[str]) -> bool:
    """Return True when path matches any configured exclude pattern."""
    absolute = path.resolve()
    try:
        relative = absolute.relative_to(root.resolve())
    except ValueError:
        relative = absolute

    candidates = {
        relative.as_posix(),
        absolute.as_posix(),
        path.name,
    }
    return any(fnmatch(candidate, pattern) for pattern in patterns for candidate in candidates)


def load_config(project_root: Path | None = None) -> dict:
    """Load Odoc configuration from pyproject.toml."""
    root = project_root or Path.cwd()
    try:
        pyproject_path = root / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
        return pyproject_data.get("tool", {}).get("odoc", {})
    except FileNotFoundError:
        return {}


def module_doc_path(file: Path, project_root: Path, output_dir: Path) -> Path:
    """Return the Markdown path for a Python file, preserving package directories."""
    try:
        relative = file.resolve().relative_to(project_root.resolve())
    except ValueError:
        relative = Path(file.name)

    if relative.name == "__init__.py":
        relative = relative.with_name("index.py")

    return output_dir / relative.with_suffix(".md")
