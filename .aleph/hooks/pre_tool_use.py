#!/usr/bin/env python3
"""
.aleph/hooks/pre_tool_use.py
Hook Nativo: PreToolUse (ASTGuard, AegisShield & Z3 Formal Gate).
Audita comandos de shell, escrituras en archivos y parches de código antes de ejecutar una herramienta.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional


DESTRUCTIVE_SHELL_PATTERNS = (
    r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f?\s+/(?:\s|$)",
    r"\bgit\s+push\s+--force\b",
    r"\bgit\s+reset\s+--hard\b",
    r"\bmkfs\.",
    r"\bdd\s+if=/dev/",
    r":\(\)\s*\{\s*:\|:&\s*\};:",
    r"\bchmod\s+-R\s+777\s+/",
)

FORBIDDEN_CODE_PATTERNS = (
    (r"transition\s*:\s*all\b", "Uso prohibido de 'transition: all' detectado en CSS."),
    (r"\bVACUUM\s+FULL\b", "Uso prohibido de 'VACUUM FULL' detectado en SQL."),
)


def _scan_with_aegis_shield(text: str) -> List[str]:
    """Ejecuta el escudo determinista de 5 capas (NFKC, homóglifos, Base64/Hex, firmas y AST taint)."""
    if not text:
        return []
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    try:
        from aleph_core.security.aegis_shield import AegisShield
    except ImportError:
        return []
    rep = AegisShield.scan_text(text)
    if rep.safe:
        return []
    return [f"AegisShield [{f.rule_id} - {f.category}]: {f.description}" for f in rep.findings]


UI_EXTENSIONS = (".html", ".css", ".scss", ".tsx", ".jsx", ".vue", ".svelte", ".astro")

UI_ANTI_SLOP_PATTERNS = (
    (r"\blorem\s+ipsum\b", "AI Slop UI bloqueado: placeholder lorem-ipsum prohibido en interfaz."),
    (r"(?://|/\*)\s*\.\.\.\s*(?:rest\s+of|existing|más|remaining)", "Código UI truncado perezoso bloqueado (marcador ellipsis rest-of/existing)."),
    (r"//\s*resto\s+del\s+c[oó]digo\b", "Código UI truncado perezoso bloqueado (comentario resto-del-codigo)."),
    (r"TODO\s*:\s*implement\s+UI\b", "Placeholder bloqueado (implement-UI pendiente)."),
    (r"//\s*add\s+remaining\b", "Código UI incompleto bloqueado (add-remaining)."),
    (
        r"\btransition(?:-property)?\s*:[^;{}\n]*\b(?:width|height|top|left|right|bottom|margin(?:-(?:top|right|bottom|left))?|padding(?:-(?:top|right|bottom|left))?)\b",
        "Layout Thrashing 60-120 FPS bloqueado: animá solo propiedades GPU-composited (transform, opacity).",
    ),
)


def _is_ui_target(file_path_str: str, payload: Dict[str, Any]) -> bool:
    fp_lower = file_path_str.replace("\\", "/").lower()
    if re.search(r"(?:^|/)(?:tests?|__tests__)/|\.(?:test|spec)\.[a-z]+$", fp_lower):
        return False
    if fp_lower.endswith((".py", ".md", ".json")):
        return False
    if fp_lower.endswith(UI_EXTENSIONS):
        return True
    lang = str(payload.get("language", "") or "").lower()
    return lang in ("html", "css", "scss", "tsx", "jsx", "vue", "svelte", "astro")


def _validate_python_ast_fragment(code_content: str, payload: Dict[str, Any]) -> Optional[str]:
    """
    Valida sintaxis AST de Python soportando tanto archivos completos como fragmentos parciales
    indentados (`old_string`/`new_string`, métodos de clase o ramas `elif`/`else`/`except`).
    """
    import textwrap

    file_path_str = str(payload.get("file_path", payload.get("Path", "")) or "")
    old_str = str(payload.get("old_string", payload.get("Target", "")) or "")
    if file_path_str and old_str:
        fp = Path(file_path_str)
        if fp.is_file():
            try:
                disk_src = fp.read_text(encoding="utf-8", errors="replace")
            except OSError:
                disk_src = ""
            if old_str in disk_src:
                reconstructed = disk_src.replace(old_str, code_content, 1)
                try:
                    ast.parse(reconstructed)
                    return None
                except SyntaxError as exc:
                    return f"Python AST SyntaxError at line {exc.lineno}: {exc.msg}"

    try:
        ast.parse(code_content)
        return None
    except SyntaxError as orig_exc:
        dedented = textwrap.dedent(code_content)
        candidates = [dedented]
        stripped_head = dedented.lstrip()
        if stripped_head.startswith(("elif ", "else:")):
            candidates.append("if True:\n    pass\n" + dedented)
        elif stripped_head.startswith(("except", "finally:")):
            candidates.append("try:\n    pass\n" + dedented)

        for cand in candidates:
            try:
                ast.parse(cand)
                return None
            except SyntaxError:
                continue
        return f"Python AST SyntaxError at line {orig_exc.lineno}: {orig_exc.msg}"


def evaluate_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    cmd = str(payload.get("command", ""))
    code_content = str(
        payload.get("code", payload.get("content", payload.get("new_string", payload.get("Replacement", ""))))
    )
    reasons: List[str] = []

    blocked = ("rm -rf /" in cmd) or ("git push --force" in cmd)
    for pat in DESTRUCTIVE_SHELL_PATTERNS:
        if re.search(pat, cmd):
            blocked = True
            reasons.append(f"Destructive command pattern matched: {pat}")

    aegis_cmd_findings = _scan_with_aegis_shield(cmd)
    if aegis_cmd_findings:
        blocked = True
        reasons.extend(aegis_cmd_findings)

    if code_content:
        for pat, msg in FORBIDDEN_CODE_PATTERNS:
            if re.search(pat, code_content, re.IGNORECASE):
                blocked = True
                reasons.append(msg)

        file_path_str = str(payload.get("file_path", payload.get("Path", "")) or "")
        if _is_ui_target(file_path_str, payload):
            for pat, msg in UI_ANTI_SLOP_PATTERNS:
                if re.search(pat, code_content, re.IGNORECASE):
                    blocked = True
                    reasons.append(msg)

        aegis_code_findings = _scan_with_aegis_shield(code_content)
        if aegis_code_findings:
            blocked = True
            reasons.extend(aegis_code_findings)

        if payload.get("language") == "python" or file_path_str.endswith(".py"):
            ast_err = _validate_python_ast_fragment(code_content, payload)
            if ast_err:
                blocked = True
                reasons.append(ast_err)

    return {
        "allowed": not blocked,
        "exit_code": 2 if blocked else 0,
        "hook": "PreToolUse",
        "reasons": reasons,
    }


def main() -> int:
    raw = sys.stdin.read().strip() if not sys.stdin.isatty() else "{}"
    try:
        payload = json.loads(raw or "{}")
    except json.JSONDecodeError:
        payload = {"command": raw}
    res = evaluate_pre_tool_use(payload)
    sys.stdout.write(json.dumps(res, ensure_ascii=False) + "\n")
    return int(res["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
