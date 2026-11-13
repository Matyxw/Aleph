#!/usr/bin/env python3
"""Escáner determinista de limpieza Zero-Literal, Zero-Placeholder y Seguridad AST."""
import ast
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List

_TODO_RE = re.compile(r"\b(?:TODO|FIXME|XXX|HACK)\b")
_HARDCODED_USER_RE = re.compile(r"C:\\\\?Users\\\\?Lucas\s+cardozo", re.IGNORECASE)
_SHELL_TRUE_RE = re.compile(r"\bshell\s*=\s*True\b")


def scan_source_cleanliness(source_text: str, filename: str = "<memory>") -> Dict[str, Any]:
    """Audita un archivo fuente respecto a placeholders AST, transition:all y rutas locales."""
    has_transition_all = "transition: all" in source_text or "transition:all" in source_text
    has_todo = bool(_TODO_RE.search(source_text))
    has_hardcoded_user = bool(_HARDCODED_USER_RE.search(source_text))
    has_shell_true = bool(_SHELL_TRUE_RE.search(source_text))
    ast_placeholders: List[str] = []

    if filename.endswith(".py") or filename == "<memory>":
        try:
            tree = ast.parse(source_text)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    body = node.body
                    # Ignorar docstring inicial si existe
                    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
                        body = body[1:]
                    if len(body) == 1 and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and body[0].value.value is Ellipsis:
                        ast_placeholders.append(f"L{body[0].lineno}: Ellipsis stub en {node.name}")
                    elif len(body) == 1 and isinstance(body[0], ast.Pass):
                        ast_placeholders.append(f"L{body[0].lineno}: pass stub en {node.name}")
                elif isinstance(node, ast.ExceptHandler):
                    if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                        ast_placeholders.append(f"L{node.body[0].lineno}: except: pass silencioso")
                elif isinstance(node, ast.Raise) and isinstance(node.exc, (ast.Name, ast.Call)):
                    exc_name = node.exc.id if isinstance(node.exc, ast.Name) else getattr(node.exc.func, "id", "")
                    if exc_name == "NotImplementedError":
                        ast_placeholders.append(f"L{node.lineno}: NotImplementedError")
        except SyntaxError:
            pass

    clean = not (has_transition_all or has_todo or has_hardcoded_user or has_shell_true or ast_placeholders)
    return {
        "clean": clean,
        "zero_transition_all": not has_transition_all,
        "zero_todo": not has_todo,
        "zero_hardcoded_user": not has_hardcoded_user,
        "zero_shell_true": not has_shell_true,
        "ast_placeholders": ast_placeholders,
    }


def scan_repository(root: Path) -> Dict[str, Any]:
    """Recorre archivos Python del repositorio excluyendo artefactos de caché."""
    findings: List[Dict[str, Any]] = []
    files_scanned = 0
    for py_file in Path(root).rglob("*.py"):
        if any(p in py_file.parts for p in ("__pycache__", ".git", "tests")):
            continue
        files_scanned += 1
        text = py_file.read_text(encoding="utf-8", errors="ignore")
        res = scan_source_cleanliness(text, filename=py_file.name)
        if not res["clean"] and res["ast_placeholders"]:
            findings.append({"file": str(py_file), "issues": res["ast_placeholders"]})
    return {"files_scanned": files_scanned, "clean": len(findings) == 0, "findings": findings}


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent.parent
    print(json.dumps(scan_repository(target), indent=2, ensure_ascii=False))
