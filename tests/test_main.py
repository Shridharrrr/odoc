from typer.testing import CliRunner

from odocxify.main import app

runner = CliRunner()


def test_generate_command_creates_docs(tmp_path):
    project = tmp_path / "project"
    package = project / "pkg"
    package.mkdir(parents=True)
    (package / "mod.py").write_text(
        '''
VALUE = 1

def hello(name: str) -> str:
    """Greet a user."""
    return f"Hello {name}"
''',
        encoding="utf-8",
    )

    docs = tmp_path / "docs"
    result = runner.invoke(app, [str(project), "--out", str(docs)])

    assert result.exit_code == 0
    assert (docs / "pkg" / "mod.md").exists()
    assert (docs / "index.md").exists()
    assert not (tmp_path / "index.md").exists()
    assert "def hello(name: str) -> str" in (docs / "pkg" / "mod.md").read_text(encoding="utf-8")


def test_generate_command_creates_mkdocs_homepage_for_api_output(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "mod.py").write_text(
        '''
def hello():
    """Greet."""
''',
        encoding="utf-8",
    )

    docs_root = tmp_path / "docs"
    result = runner.invoke(app, [str(project), "--out", str(docs_root / "api")])

    assert result.exit_code == 0
    assert (docs_root / "index.md").exists()
    assert "[API Reference](api/index.md)" in (docs_root / "index.md").read_text(encoding="utf-8")
