# src/odoc/ai_doc_generator.py

import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file.")

genai.configure(api_key=API_KEY)

def generate_docstring_for_code(source_code: str) -> dict | None:
    """
    Uses the Gemini API to generate documentation for a snippet of Python code.

    Args:
        source_code: The raw source code of a function or method.

    Returns:
        A dictionary with docstring info, or None if it fails.
    """
    # CHANGED: Use the latest recommended model name
    model = genai.GenerativeModel('gemini-2.0-flash')

    prompt = f"""
    You are an expert Python programmer creating high-quality documentation.
    Analyze the following Python code snippet and generate a comprehensive docstring for it.

    **Code Snippet:**
    ```python
    {source_code}
    ```

    **Your Task:**
    Return a single JSON object with the following keys:
    - "docstring": A clear, concise docstring explaining what the function does.
    - "summary": A one-sentence, plain-English summary of the function's algorithm or purpose.

    **Rules:**
    - Do not include the function signature in your response.
    - Only return the raw JSON object, with no surrounding text or markdown.
    """

    try:
        response = model.generate_content(prompt)
        # Clean up the response to extract only the JSON part
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_text)
    except Exception as e:
        print(f"Error calling AI model: {e}")
        return None