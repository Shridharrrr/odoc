import tomllib  
from pathlib import Path

def find_python_files(start_path: Path, exclude_patterns: list[str]) -> list[Path]:
    """Finds all .py files recursively, respecting exclude patterns."""
    all_files = list(start_path.rglob("*.py"))
    
    # Filter out excluded files
    filtered_files = []
    for file in all_files:
        if not any(file.match(pattern) for pattern in exclude_patterns):
            filtered_files.append(file)
            
    return filtered_files

def load_config() -> dict:
    """Loads Odoc configuration from pyproject.toml."""
    try:
        pyproject_path = Path.cwd() / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
        return pyproject_data.get("tool", {}).get("odoc", {})
    except FileNotFoundError:
        return {}