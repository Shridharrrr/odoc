from __future__ import annotations

import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


def _environment(template_dir: str | None = None) -> Environment:
    default_template_dir = os.path.join(os.path.dirname(__file__), "..", "..", "templates")
    search_paths = [path for path in [template_dir, default_template_dir] if path]
    return Environment(
        loader=FileSystemLoader(search_paths),
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=select_autoescape(disabled_extensions=("md", "j2")),
    )


def generate_docs(
    template_data: dict,
    template_name: str,
    output_path: str,
    *,
    template_dir: str | None = None,
) -> None:
    """Generate a single Markdown file from a template."""
    env = _environment(template_dir)
    template = env.get_template(template_name)
    rendered_content = template.render(**template_data)

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(_clean_markdown(rendered_content), encoding="utf-8")


def generate_index(modules: list[dict], output_dir: str) -> None:
    """Generate the API index page inside the output directory."""
    destination = Path(output_dir) / "index.md"
    destination.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# API Reference",
        "",
        "This section is generated from the Python source code.",
        "",
    ]
    if not modules:
        lines.append("No public Python API was found.")
    else:
        lines.extend(
            [
                "| Module | Classes | Functions | Constants |",
                "| --- | ---: | ---: | ---: |",
            ]
        )
        for module in modules:
            lines.append(
                "| "
                f"[`{module['module_name']}`]({module['doc_path'].as_posix()}) "
                f"| {module['class_count']} "
                f"| {module['function_count']} "
                f"| {module['constant_count']} |"
            )

    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_site_index(modules: list[dict], docs_root: str, api_dir_name: str = "api") -> None:
    """Generate docs/index.md so MkDocs has a real homepage at /."""
    destination = Path(docs_root) / "index.md"
    destination.parent.mkdir(parents=True, exist_ok=True)

    module_count = len(modules)
    class_count = sum(module["class_count"] for module in modules)
    function_count = sum(module["function_count"] for module in modules)

    lines = [
        "# Odoc Documentation",
        "",
        "Generated API documentation for this Python project.",
        "",
        "## Project API",
        "",
        f"- [API Reference]({api_dir_name}/index.md)",
        f"- Modules documented: **{module_count}**",
        f"- Classes documented: **{class_count}**",
        f"- Functions documented: **{function_count}**",
        "",
    ]

    if modules:
        lines.extend(["## Modules", ""])
        for module in modules:
            lines.append(
                f"- [`{module['module_name']}`]({api_dir_name}/{module['doc_path'].as_posix()})"
            )

    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _clean_markdown(content: str) -> str:
    """Trim generated Markdown while keeping normal paragraph spacing."""
    cleaned_lines = []
    blank_seen = False

    for line in content.strip().splitlines():
        if line.strip():
            cleaned_lines.append(line.rstrip())
            blank_seen = False
        elif not blank_seen:
            cleaned_lines.append("")
            blank_seen = True

    return "\n".join(cleaned_lines).strip() + "\n"
