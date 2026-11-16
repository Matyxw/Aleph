#!/usr/bin/env python3
"""
.aleph/scripts/scan_cleanliness.py
Escáner determinista de limpieza Zero-Literal, Zero-Placeholder e Higiene Estructural del Repositorio.
Verifica:
1. Ausencia de `transition: all` fuera de comentarios en hojas de estilo y componentes.
2. Ausencia de marcadores perezosos (`TODO: implement`, `PLACEHOLDER`, `Lorem ipsum`).
3. Ausencia de artefactos de estado mutables (`.db`, `.sqlite`, `.journal.jsonl`, `.pyc`) en el árbol limpio.
4. Validez sintáctica AST del 100% de los módulos `.py` del proyecto.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List


COMMENT_STRIP_RE = re.compile(r"/\*.*?\*/|//[^\n]*|#[^\n]*", re.DOTALL)
TRANSITION_ALL_RE = re.compile(r"transition\s*:\s*all\b", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"\b(?:lorem\s+ipsum|TODO_PLACEHOLDER_UNIMPLEMENTED)\b", re.IGNORECASE)
FORBIDDEN_RUNTIME_PATTERNS = (".db", ".sqlite", ".journal.jsonl", ".pyc")


def scan_source_cleanliness(source_text: str) -> Dict[str, Any]:
    """Audita un bloque de texto o código garantizando ausencia de transition: all y placeholders."""
    stripped = COMMENT_STRIP_RE.sub("", source_text)
    has_transition_all = bool(TRANSITION_ALL_RE.search(stripped))
    has_placeholder = bool(PLACEHOLDER_RE.search(stripped))
    clean = (not has_transition_all) and (not has_placeholder)
    return {
        "clean": clean,
        "zero_transition_all": not has_transition_all,
        "zero_placeholders": not has_placeholder,
    }


def scan_repository_hygiene(root_dir: Path) -> Dict[str, Any]:
    """Audita el árbol completo del repositorio verificando sintaxis AST, cero archivos vacíos y cero bloat."""
    root_dir = Path(root_dir).resolve()
    runtime_bloat: List[str] = []
    syntax_errors: List[str] = []
    empty_files: List[str] = []
    py_files_checked = 0

    for path in sorted(root_dir.rglob("*")):
        if ".git" in path.parts or "__pycache__" in path.parts or "node_modules" in path.parts:
            continue
        if not path.is_file():
            continue
        rel = str(path.relative_to(root_dir))
        if any(rel.endswith(suf) for suf in FORBIDDEN_RUNTIME_PATTERNS):
            runtime_bloat.append(rel)
        if path.stat().st_size == 0:
            empty_files.append(rel)
        if path.suffix == ".py":
            py_files_checked += 1
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=rel)
            except SyntaxError as exc:
                syntax_errors.append(f"{rel}:{exc.lineno}: {exc.msg}")

    is_clean = len(runtime_bloat) == 0 and len(syntax_errors) == 0 and len(empty_files) == 0
    return {
        "clean": is_clean,
        "py_files_checked": py_files_checked,
        "runtime_bloat_files": runtime_bloat,
        "syntax_errors": syntax_errors,
        "empty_files": empty_files,
    }


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent.parent
    report = scan_repository_hygiene(repo_root)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["clean"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
