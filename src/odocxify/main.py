from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import typer

from . import analyzer, generator, utils

app = typer.Typer(no_args_is_help=False, help="Generate Markdown API documentation for Python projects.")


@app.command()
def generate(
    path: str = typer.Argument(".", help="The path to a file or directory to document."),
    output_dir: str = typer.Option("docs/api", "--out", "-o", help="Output directory for documentation files."),
    include_private: bool = typer.Option(False, "--private", help="Include private names that start with _."),
    use_ai: bool = typer.Option(False, "--ai", help="Use Gemini to draft missing docstrings when GOOGLE_API_KEY is set."),
    ai_model: str = typer.Option("gemini-2.5-flash-lite", "--ai-model", help="Gemini model used with --ai."),
    template_dir: Optional[str] = typer.Option(None, "--template-dir", help="Optional directory containing custom Jinja templates."),
    clean: bool = typer.Option(False, "--clean", help="Delete old Markdown files in the output directory before generating."),
    fail_on_empty: bool = typer.Option(False, "--fail-on-empty", help="Exit with an error if no documentable API is found."),
):
    """Generate documentation files for a Python project."""
    typer.secho("Starting Odoc...", fg=typer.colors.CYAN)

    input_path = Path(path).resolve()
    output_path = Path(output_dir).resolve()
    project_root = input_path if input_path.is_dir() else input_path.parent
    config = utils.load_config(project_root)
    exclude_patterns = config.get("exclude", [])

    if clean and output_path.exists():
        for markdown_file in output_path.rglob("*.md"):
            markdown_file.unlink()

    os.makedirs(output_path, exist_ok=True)
    py_files = utils.find_python_files(input_path, exclude_patterns)

    if not py_files:
        typer.secho("No Python files to document.", fg=typer.colors.YELLOW)
        raise typer.Exit(code=1 if fail_on_empty else 0)

    generated_modules = []

    for file in py_files:
        typer.echo(f"Analyzing {file.relative_to(project_root)}")
        analysis_data = analyzer.analyze_file(
            str(file),
            use_ai=use_ai,
            include_private=include_private,
            ai_model=ai_model,
        )
        if not _has_documentable_items(analysis_data):
            continue

        relative_path = file.resolve().relative_to(project_root)
        final_output_path = utils.module_doc_path(file, project_root, output_path)
        doc_link = final_output_path.relative_to(output_path)

        template_data = {
            "file_path": str(relative_path),
            "module_name": _module_name(relative_path),
            "analysis_data": analysis_data,
        }
        generator.generate_docs(
            template_data,
            "default/api_page.md.j2",
            str(final_output_path),
            template_dir=template_dir,
        )
        generated_modules.append(
            {
                "file_path": str(relative_path),
                "module_name": template_data["module_name"],
                "doc_path": doc_link,
                "class_count": len(analysis_data["classes"]),
                "function_count": len(analysis_data["functions"])
                + sum(len(class_info["methods"]) for class_info in analysis_data["classes"]),
                "constant_count": len(analysis_data["constants"])
                + sum(len(class_info["attributes"]) for class_info in analysis_data["classes"]),
            }
        )
        typer.secho(f"Generated {final_output_path}", fg=typer.colors.GREEN)

    generator.generate_index(generated_modules, str(output_path))
    if output_path.name == "api":
        generator.generate_site_index(generated_modules, str(output_path.parent), output_path.name)

    if not generated_modules:
        typer.secho("No public classes, functions, or constants were found.", fg=typer.colors.YELLOW)
        raise typer.Exit(code=1 if fail_on_empty else 0)

    typer.secho(f"Done. Generated {len(generated_modules)} page(s) in {output_path}", fg=typer.colors.GREEN)


def _has_documentable_items(analysis_data: dict) -> bool:
    return bool(
        analysis_data["classes"]
        or analysis_data["functions"]
        or analysis_data["constants"]
        or analysis_data["errors"]
    )


def _module_name(relative_path: Path) -> str:
    parts = list(relative_path.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


if __name__ == "__main__":
    app()
