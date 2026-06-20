from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, Union

from . import ai_doc_generator

FunctionNode = Union[ast.FunctionDef, ast.AsyncFunctionDef]


def analyze_file(
    file_path: str,
    *,
    use_ai: bool = False,
    include_private: bool = False,
    include_source: bool = False,
    ai_model: str = ai_doc_generator.DEFAULT_MODEL,
) -> dict[str, Any]:
    """Analyze a Python file and return structured API documentation data."""
    path = Path(file_path)
    source_code = path.read_text(encoding="utf-8")

    try:
        tree = ast.parse(source_code, filename=str(path))
    except SyntaxError as exc:
        return {
            "module_docstring": "",
            "classes": [],
            "functions": [],
            "constants": [],
            "errors": [f"SyntaxError on line {exc.lineno}: {exc.msg}"],
        }

    results: dict[str, Any] = {
        "module_docstring": ast.get_docstring(tree) or "",
        "classes": [],
        "functions": [],
        "constants": [],
        "errors": [],
    }

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if _is_public(node.name, include_private):
                results["functions"].append(
                    _process_function(
                        node,
                        use_ai=use_ai,
                        include_source=include_source,
                        ai_model=ai_model,
                    )
                )
        elif isinstance(node, ast.ClassDef):
            if _is_public(node.name, include_private):
                results["classes"].append(
                    _process_class(
                        node,
                        use_ai=use_ai,
                        include_private=include_private,
                        include_source=include_source,
                        ai_model=ai_model,
                    )
                )
        elif _is_constant_node(node):
            results["constants"].extend(_process_constants(node))

    return results


def _process_function(
    node: FunctionNode,
    *,
    use_ai: bool,
    include_source: bool,
    ai_model: str,
) -> dict[str, Any]:
    docstring = ast.get_docstring(node)
    func_info: dict[str, Any] = {
        "name": node.name,
        "signature": _signature_for(node),
        "args": [arg.arg for arg in node.args.args],
        "returns": _unparse(node.returns) if node.returns else "",
        "decorators": [_unparse(decorator) for decorator in node.decorator_list],
        "docstring": docstring or "",
        "summary": _first_sentence(docstring or ""),
        "ai_generated": False,
        "is_async": isinstance(node, ast.AsyncFunctionDef),
        "lineno": node.lineno,
        "end_lineno": getattr(node, "end_lineno", node.lineno),
        "has_docstring": bool(docstring),
    }

    if include_source:
        func_info["source"] = _unparse(node)

    if use_ai and not docstring:
        source = func_info.get("source") or _unparse(node)
        ai_docs = ai_doc_generator.generate_docstring_for_code(source, model_name=ai_model)
        if ai_docs:
            func_info["docstring"] = ai_docs.get("docstring", "")
            func_info["summary"] = ai_docs.get("summary", "")
            func_info["ai_generated"] = True

    return func_info


def _process_class(
    node: ast.ClassDef,
    *,
    use_ai: bool,
    include_private: bool,
    include_source: bool,
    ai_model: str,
) -> dict[str, Any]:
    docstring = ast.get_docstring(node)
    class_info: dict[str, Any] = {
        "name": node.name,
        "bases": [_unparse(base) for base in node.bases],
        "decorators": [_unparse(decorator) for decorator in node.decorator_list],
        "docstring": docstring or "",
        "summary": _first_sentence(docstring or ""),
        "methods": [],
        "attributes": [],
        "lineno": node.lineno,
        "end_lineno": getattr(node, "end_lineno", node.lineno),
        "has_docstring": bool(docstring),
    }

    for child in node.body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if _is_public(child.name, include_private) or child.name in {"__init__", "__call__"}:
                class_info["methods"].append(
                    _process_function(
                        child,
                        use_ai=use_ai,
                        include_source=include_source,
                        ai_model=ai_model,
                    )
                )
        elif _is_constant_node(child):
            class_info["attributes"].extend(_process_constants(child))

    return class_info


def _is_public(name: str, include_private: bool) -> bool:
    return include_private or not (name.startswith("_") and not name.startswith("__"))


def _is_constant_node(node: ast.AST) -> bool:
    return isinstance(node, (ast.Assign, ast.AnnAssign))


def _process_constants(node: ast.Assign | ast.AnnAssign) -> list[dict[str, Any]]:
    names: list[dict[str, Any]] = []
    if isinstance(node, ast.Assign):
        targets = node.targets
        annotation = ""
        value = _safe_value(node.value)
    else:
        targets = [node.target]
        annotation = _unparse(node.annotation) if node.annotation else ""
        value = _safe_value(node.value) if node.value else ""

    for target in targets:
        if isinstance(target, ast.Name) and target.id.isupper():
            names.append(
                {
                    "name": target.id,
                    "annotation": annotation,
                    "value": value,
                    "lineno": node.lineno,
                }
            )
    return names


def _signature_for(node: FunctionNode) -> str:
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    signature = f"{prefix} {node.name}({_unparse(node.args)})"
    if node.returns:
        signature += f" -> {_unparse(node.returns)}"
    return signature


def _safe_value(node: ast.AST | None) -> str:
    if node is None:
        return ""
    try:
        value = ast.literal_eval(node)
    except (ValueError, TypeError):
        return _unparse(node)
    return repr(value)


def _first_sentence(text: str) -> str:
    if not text:
        return ""
    normalized = " ".join(text.strip().split())
    return normalized.split(". ")[0].rstrip(".") + "."


def _unparse(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def _process_node(node, results_container):
    """Backward-compatible helper retained for older integrations."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        func_info = _process_function(
            node,
            use_ai=False,
            include_source=False,
            ai_model=ai_doc_generator.DEFAULT_MODEL,
        )
        if "methods" in results_container:
            results_container["methods"].append(func_info)
        else:
            results_container["functions"].append(func_info)
    elif isinstance(node, ast.ClassDef):
        class_info = _process_class(
            node,
            use_ai=False,
            include_private=True,
            include_source=False,
            ai_model=ai_doc_generator.DEFAULT_MODEL,
        )
        results_container["classes"].append(class_info)
