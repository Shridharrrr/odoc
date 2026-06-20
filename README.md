# Odoc

**Odoc** (Odocxify) is a Markdown API documentation generator for Python projects. It works from static analysis by default and can optionally use Gemini to draft missing docstrings.

## Features

- Static analysis for modules, functions, async functions, classes, methods, decorators, return types, constants, and class attributes.
- Markdown output that preserves package directory structure and includes an API index.
- Optional AI mode for missing docstrings with `--ai`.
- Configurable excludes via `pyproject.toml`.
- Built for MkDocs, but the generated Markdown works anywhere.

## Installation

```bash
pip install odocxify
```

Or using Poetry:

```bash
poetry add odocxify
```

## Usage

Generate docs for the current project:

```bash
odoc .
```

This writes Markdown files to `docs/api`.

Useful options:

```bash
odoc --help
odoc src/ --out docs/api --clean
odoc src/ --private
odoc src/ --ai
```

AI mode is optional. To use it, create a `.env` file or environment variable:

```env
GOOGLE_API_KEY=your_gemini_api_key
```

## Configuration

Configure `odoc` in `pyproject.toml`:

```toml
[tool.odoc]
exclude = [
    "tests/*",
    "setup.py",
    "docs/*"
]
```

## License

MIT
