from __future__ import annotations

import json
import os

from dotenv import load_dotenv

DEFAULT_MODEL = "gemini-2.5-flash-lite"


def generate_docstring_for_code(
    source_code: str,
    *,
    model_name: str = DEFAULT_MODEL,
    api_key: str | None = None,
) -> dict | None:
    """
    Use Gemini to generate documentation for a Python code snippet.

    AI support is deliberately lazy: importing odocxify should never fail just
    because a developer has not configured an API key.
    """
    load_dotenv()
    resolved_api_key = api_key or os.getenv("GOOGLE_API_KEY")
    if not resolved_api_key:
        return None

    try:
        import google.generativeai as genai
    except ImportError:
        return None

    genai.configure(api_key=resolved_api_key)
    model = genai.GenerativeModel(model_name)

    prompt = f"""
    You are an expert Python programmer creating high-quality documentation.
    Analyze the following Python code snippet and generate a comprehensive docstring for it.

    Code Snippet:
    ```python
    {source_code}
    ```

    Return a single JSON object with these keys:
    - "docstring": A clear, concise docstring explaining what the function does.
    - "summary": A one-sentence plain-English summary.

    Rules:
    - Do not include the function signature in your response.
    - Only return raw JSON with no surrounding text or markdown.
    """

    try:
        response = model.generate_content(prompt)
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_text)
    except Exception as exc:
        print(f"Error calling AI model: {exc}")
        return None
