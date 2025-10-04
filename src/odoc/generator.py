import os
from jinja2 import Environment, FileSystemLoader

def generate_docs(template_data: dict, template_name: str, output_path: str):
    """
    Generates a single Markdown file from a template.
    """
    template_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'templates')
    env = Environment(loader=FileSystemLoader(template_dir), trim_blocks=True, lstrip_blocks=True)
    
    template = env.get_template(template_name)
    rendered_content = template.render(**template_data)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered_content)
    
    print(f"✅ Documentation successfully generated at: {output_path}")