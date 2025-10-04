# src/odoc/analyzer.py

import ast
# REMOVED: All imports from the 'ast_tools' library

# Import the new AI module
from . import ai_doc_generator

def analyze_file(file_path: str) -> dict:
    """
    Analyzes a Python file to find classes and standalone functions.
    """
    print(f"🔬 Analyzing {file_path}...")
    with open(file_path, "r", encoding="utf-8") as source_file:
        source_code = source_file.read()

    tree = ast.parse(source_code)
    analysis_results = {"classes": [], "functions": []}

    for node in tree.body:
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
            # Process top-level functions and classes
            _process_node(node, analysis_results)
            
    return analysis_results

def _process_node(node, results_container):
    """Helper to process a node and call AI if needed."""
    if isinstance(node, ast.FunctionDef):
        docstring = ast.get_docstring(node)
        func_info = {
            "name": node.name,
            "args": [arg.arg for arg in node.args.args],
            "docstring": docstring,
            "ai_generated": False
        }

        if not docstring:
            print(f"💬 No docstring for '{node.name}'. Asking AI for help...")
            # CHANGED: Use the built-in ast.unparse() instead of the external library
            source_code = ast.unparse(node)
            ai_docs = ai_doc_generator.generate_docstring_for_code(source_code)
            if ai_docs:
                func_info["docstring"] = ai_docs.get("docstring", "AI failed to generate docstring.")
                func_info["summary"] = ai_docs.get("summary", "")
                func_info["ai_generated"] = True
        
        # Determine where to append the function/method
        if "methods" in results_container:
            results_container["methods"].append(func_info)
        else:
            results_container["functions"].append(func_info)

    elif isinstance(node, ast.ClassDef):
        class_info = {
            "name": node.name,
            "docstring": ast.get_docstring(node) or "No docstring found.",
            "methods": []
        }
        for method_node in node.body:
            if isinstance(method_node, ast.FunctionDef):
                _process_node(method_node, class_info)
        results_container["classes"].append(class_info)