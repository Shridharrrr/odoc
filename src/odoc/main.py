import typer
import os
from pathlib import Path
from . import analyzer, generator, utils

app = typer.Typer()

@app.command()
def generate(
    path: str = typer.Argument(".", help="The path to a file or directory to document."),
    output_dir: str = typer.Option("docs/api", "--out", "-o", help="Output directory for documentation files."),
):
    """
    Generates documentation files for a Python project.
    """
    typer.secho("🚀 Starting Odoc...", fg=typer.colors.CYAN)
    
    input_path = Path(path)
    output_path = Path(output_dir)
    os.makedirs(output_path, exist_ok=True) # Create the output directory

    project_root = Path.cwd().resolve()
    config = utils.load_config()
    exclude_patterns = config.get("exclude", [])
    
    if input_path.is_dir():
        py_files = utils.find_python_files(input_path, exclude_patterns)
    else:
        py_files = [input_path]

    if not py_files:
        typer.echo("No Python files to document.")
        raise typer.Exit()

    # Generate one file per module
    for file in py_files:
        analysis_data = analyzer.analyze_file(str(file))
        if analysis_data["classes"] or analysis_data["functions"]:
            # Create a clean filename for the markdown file
            relative_path = file.resolve().relative_to(project_root)
            output_filename = f"{relative_path.stem}.md"
            final_output_path = output_path / output_filename
            
            # The data structure for the template is now simpler
            template_data = {
                "file_path": str(relative_path),
                "analysis_data": analysis_data
            }
            generator.generate_docs(template_data, "default/api_page.md.j2", str(final_output_path))

if __name__ == "__main__":
    app()