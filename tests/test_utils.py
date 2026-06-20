import pytest
import sys
from pathlib import Path
from odocxify import utils

# Mock functionality since we don't want to rely on actual file system for unit logic where possible,
# but for find_python_files using a tmp_path is best.

def test_find_python_files(tmp_path):
    # Create a dummy structure
    d = tmp_path / "subdir"
    d.mkdir()
    p1 = d / "hello.py"
    p1.write_text("print('hello')")
    p2 = d / "ignore_me.py"
    p2.write_text("print('ignore')")
    p3 = d / "not_py.txt"
    p3.write_text("text")

    # Call the function
    files = utils.find_python_files(tmp_path, exclude_patterns=["*ignore_me.py"])
    
    # Assertions
    filenames = [f.name for f in files]
    assert "hello.py" in filenames
    assert "ignore_me.py" not in filenames
    assert "not_py.txt" not in filenames


def test_find_python_files_sorts_and_skips_default_excludes(tmp_path):
    package = tmp_path / "pkg"
    package.mkdir()
    cache = package / "__pycache__"
    cache.mkdir()

    (package / "b.py").write_text("", encoding="utf-8")
    (package / "a.py").write_text("", encoding="utf-8")
    (cache / "cached.py").write_text("", encoding="utf-8")

    files = utils.find_python_files(tmp_path)

    assert [file.name for file in files] == ["a.py", "b.py"]

def test_load_config(monkeypatch, tmp_path):
    # Mock Path.cwd to return tmp_path
    monkeypatch.setattr(Path, "cwd", lambda: tmp_path)
    
    # Case 1: No pyproject.toml
    config = utils.load_config()
    assert config == {}

    # Case 2: Valid pyproject.toml
    toml_content = """
    [tool.odoc]
    exclude = ["tests/*"]
    """
    p = tmp_path / "pyproject.toml"
    p.write_text(toml_content, encoding="utf-8")
    
    config = utils.load_config()
    assert config.get("exclude") == ["tests/*"]


def test_module_doc_path_preserves_directories_and_init(tmp_path):
    root = tmp_path / "project"
    output = tmp_path / "docs"
    package = root / "package"
    package.mkdir(parents=True)
    module = package / "feature.py"
    init = package / "__init__.py"

    assert utils.module_doc_path(module, root, output) == output / "package" / "feature.md"
    assert utils.module_doc_path(init, root, output) == output / "package" / "index.md"

def test_tomllib_import():
    """Ensure tomllib (or tomli) is importable via utils."""
    assert hasattr(utils, "tomllib")
