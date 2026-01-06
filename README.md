# Odoc

**Odoc** (Odocxify) is an intelligent, AI-powered documentation generator for Python projects. It uses Google's Gemini models to automatically generate comprehensive docstrings and API documentation for your code.

## Features

- 🧠 **AI-Powered**: Uses Gemini 2.5 Flash Lite for high-quality, context-aware docstrings.
- 📦 **Automated**: Scans your project for Python files and generates Markdown documentation.
- ⚙️ **Configurable**: Exclude files/directories via `pyproject.toml`.
- 🚀 **Modern**: Built with `typer`, `jinja2`, and `mkdocs` in mind.

## Installation

```bash
pip install odocxify
```

Or using Poetry:

```bash
poetry add odocxify
```

## Usage

1. **Set up your API Key**:
   Create a `.env` file in your project root:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key
   ```

2. **Run Odoc**:
   ```bash
   odoc .
   ```
   This will generate documentation for all Python files in the current directory and save them to `docs/api`.

3. **Options**:
   ```bash
   odoc --help
   odoc src/ --out my_docs/
   ```

## Configuration

You can configure `odoc` in your `pyproject.toml`:

```toml
[tool.odoc]
exclude = [
    "tests/*",
    "setup.py"
]
```

## License

MIT
