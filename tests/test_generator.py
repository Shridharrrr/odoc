from odocxify import generator


def test_generate_index(tmp_path):
    generator.generate_index(
        [
            {
                "file_path": "pkg/mod.py",
                "module_name": "pkg.mod",
                "doc_path": tmp_path.joinpath("pkg/mod.md").relative_to(tmp_path),
                "class_count": 1,
                "function_count": 2,
                "constant_count": 3,
            }
        ],
        str(tmp_path),
    )

    content = (tmp_path / "index.md").read_text(encoding="utf-8")
    assert "# API Reference" in content
    assert "[`pkg.mod`](pkg/mod.md)" in content
    assert "| [`pkg.mod`](pkg/mod.md) | 1 | 2 | 3 |" in content


def test_generate_site_index(tmp_path):
    generator.generate_site_index(
        [
            {
                "module_name": "pkg.mod",
                "doc_path": tmp_path.joinpath("api/pkg/mod.md").relative_to(tmp_path / "api"),
                "class_count": 1,
                "function_count": 2,
                "constant_count": 0,
            }
        ],
        str(tmp_path),
    )

    content = (tmp_path / "index.md").read_text(encoding="utf-8")
    assert "# Odoc Documentation" in content
    assert "[API Reference](api/index.md)" in content
    assert "[`pkg.mod`](api/pkg/mod.md)" in content
