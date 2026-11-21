"""
AegisShield Security Engine (Superación de ECC AgentShield - Motor Determinista de 5 Capas).
Escanea entradas, salidas y código generado en <5ms aplicando defensa en profundidad:
1. Capa 1: Normalización Unicode NFKC y eliminación de caracteres invisibles de control/formato (Cf, Cc).
2. Capa 2: Normalización de homóglifos cirílicos, griegos y de ancho completo (fullwidth).
3. Capa 3: Decodificación heurística recursiva de payloads Base64 (>=20 chars) y hexadecimales embebidos.
4. Capa 4: Firmas deterministas ampliadas (AEGIS-001..AEGIS-006).
5. Capa 5: Análisis de taint sobre AST de Python (AEGIS-007: eval, exec, os.system, os.popen, pty.spawn, shutil.rmtree('/'), subprocess(..., shell=True)).
"""
import ast
import base64
import binascii
import json
import re
import unicodedata
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple, Set


_HOMOGLYPH_MAP = str.maketrans({
    # Cirílico -> ASCII visual equivalente
    "\u0410": "A", "\u0412": "B", "\u0415": "E", "\u0401": "E", "\u041a": "K",
    "\u041c": "M", "\u041d": "H", "\u041e": "O", "\u0420": "P", "\u0421": "C",
    "\u0422": "T", "\u0423": "Y", "\u0425": "X", "\u0406": "I", "\u0408": "J",
    "\u0405": "S", "\u0474": "V",
    "\u0430": "a", "\u0435": "e", "\u0451": "e", "\u0456": "i", "\u0458": "j",
    "\u043e": "o", "\u0440": "p", "\u0441": "c", "\u0455": "s", "\u0443": "y",
    "\u0445": "x", "\u0501": "d", "\u051b": "q", "\u051d": "w", "\u04bb": "h",
    "\u04cf": "l", "\u0475": "v",
    # Griego -> ASCII visual equivalente
    "\u0391": "A", "\u0392": "B", "\u0395": "E", "\u0396": "Z", "\u0397": "H",
    "\u0399": "I", "\u039a": "K", "\u039c": "M", "\u039d": "N", "\u039f": "O",
    "\u03a1": "P", "\u03a4": "T", "\u03a5": "Y", "\u03a7": "X",
    "\u03b1": "a", "\u03b2": "b", "\u03b5": "e", "\u03b9": "i", "\u03ba": "k",
    "\u03bd": "v", "\u03bf": "o", "\u03c1": "p", "\u03c2": "c", "\u03c4": "t",
    "\u03c5": "u", "\u03c7": "x",
    # Puntuación/guiones engañosos comunes
    "\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2013": "-", "\u2014": "-",
    "\u2212": "-", "\u2044": "/", "\uff0f": "/",
})

_B64_CANDIDATE_RE = re.compile(r"(?<![A-Za-z0-9+/=])[A-Za-z0-9+/]{20,}={0,2}(?![A-Za-z0-9+/=])")
_B64URL_CANDIDATE_RE = re.compile(r"(?<![A-Za-z0-9_-])[A-Za-z0-9_-]{20,}={0,2}(?![A-Za-z0-9_-])")
_HEX_CANDIDATE_RE = re.compile(r"(?<![0-9a-fA-F])(?:0x)?((?:[0-9a-fA-F]{2}){10,})(?![0-9a-fA-F])")
_HEX_ESCAPE_RE = re.compile(r"(?:\\x[0-9a-fA-F]{2}){6,}")


@dataclass
class ThreatFinding:
    rule_id: str
    severity: str       # 'CRITICAL' | 'HIGH' | 'MEDIUM'
    category: str       # 'PROMPT_INJECTION' | 'SECRET_LEAK' | 'DANGEROUS_EXEC' | 'SPARKOS_VIOLATION'
    description: str
    matched_snippet: str


@dataclass
class SecurityScanReport:
    safe: bool
    findings: List[ThreatFinding] = field(default_factory=list)


class AegisShield:
    PATTERNS = [
        (
            "AEGIS-001", "CRITICAL", "PROMPT_INJECTION",
            "Intento de Prompt Injection / Ignorar instrucciones previas",
            re.compile(
                r"("
                r"ignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions?"
                r"|disregard\s+(?:all\s+)?(?:previous|prior|above)\s+(?:instructions?|directives?)"
                r"|olvida\s+(?:todas\s+)?las\s+instrucciones?"
                r"|descarta\s+(?:todas\s+)?las\s+directivas?"
                r"|ignora\s+(?:todas\s+)?las\s+(?:instrucciones?|directivas?)"
                r"|system\s+override(?:\s*:\s*you\s+are\s+now)?"
                r"|override\s+(?:all\s+)?(?:system|previous|prior|safety|security|instructions?|directives?|rules?|guardrails?|aegis)"
                r"|<\|im_start\|>\s*system"
                r"|</system>"
                r"|\bjailbreak\b"
                r"|disable\s+aegis"
                r")",
                re.IGNORECASE,
            ),
        ),
        (
            "AEGIS-002", "CRITICAL", "SECRET_LEAK",
            "Exposición de clave privada, API Token o JWT en texto plano",
            re.compile(
                r"("
                r"BEGIN\s+(?:RSA|OPENSSH|EC|DSA|PGP|ENCRYPTED\s+PRIVATE|PRIVATE)\s+(?:PRIVATE\s+)?KEY"
                r"|sk-[a-zA-Z0-9_-]{20,}"
                r"|AIza[0-9A-Za-z\-_]{35}"
                r"|gh[pousr]_[a-zA-Z0-9]{36}"
                r"|AKIA[0-9A-Z]{16}"
                r"|eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"
                r")"
            ),
        ),
        (
            "AEGIS-003", "CRITICAL", "DANGEROUS_EXEC",
            "Comando destructivo de sistema de archivos, red o base de datos",
            re.compile(
                r"("
                r"rm\s+-[a-zA-Z]*r[a-zA-Z]*f?\s+(?:/\*(?:\s|$)|/(?:\s|$)|~(?:/|\s|$)|\$HOME(?:/|\s|$))"
                r"|rm\s+-[a-zA-Z]*f[a-zA-Z]*r\s+(?:/\*(?:\s|$)|/(?:\s|$)|~(?:/|\s|$)|\$HOME(?:/|\s|$))"
                r"|find\s+/\s+[^\n]*-delete\b"
                r"|\bmkfs\.[a-zA-Z0-9_]+"
                r"|\bdd\s+if=/dev/zero\b"
                r"|DROP\s+DATABASE\s+\w+"
                r"|TRUNCATE\s+TABLE\s+\w+"
                r"|FORMAT\s+C:"
                r"|(?:curl|wget)\s+[^\n|]+\|\s*(?:ba)?sh\b"
                r"|shutil\.rmtree\s*\(\s*['\"]/['\"]\s*\)"
                r")",
                re.IGNORECASE,
            ),
        ),
        (
            "AEGIS-004", "HIGH", "SPARKOS_VIOLATION",
            "Violación REG-001: Uso de PageSetup.Draft = True oculta bordes y logos en impresión Excel",
            re.compile(r"\.Draft\s*=\s*True", re.IGNORECASE),
        ),
        (
            "AEGIS-005", "HIGH", "RESOURCE_EXHAUSTION",
            "Bucle infinito determinista detectado en regex o código fuente (while True sin salida)",
            re.compile(r"while\s+(True|1)\s*:\s*(pass|continue|time\.sleep)", re.IGNORECASE),
        ),
        (
            "AEGIS-006", "HIGH", "ANTI_PATTERN",
            "Violación de robustez: Bloque catch/except silencioso sin re-raise ni logging",
            re.compile(r"except\s*:\s*pass", re.IGNORECASE),
        ),
    ]

    @staticmethod
    def _layer1_normalize_unicode(text: str) -> str:
        """Capa 1: Normalización Unicode NFKC y eliminación de caracteres invisibles Cf/Cc (preservando \\n, \\r, \\t)."""
        nfkc = unicodedata.normalize("NFKC", text)
        out: List[str] = []
        for ch in nfkc:
            cat = unicodedata.category(ch)
            if cat == "Cf":
                continue
            if cat == "Cc" and ch not in ("\n", "\r", "\t"):
                continue
            out.append(ch)
        return "".join(out)

    @staticmethod
    def _layer2_normalize_homoglyphs(text: str) -> str:
        """Capa 2: Reemplazo determinista de homóglifos cirílicos, griegos y de ancho completo."""
        return text.translate(_HOMOGLYPH_MAP)

    @classmethod
    def _normalize_surface(cls, text: str) -> str:
        return cls._layer2_normalize_homoglyphs(cls._layer1_normalize_unicode(text))

    @staticmethod
    def _is_plausible_decoded_text(raw_bytes: bytes) -> str:
        if len(raw_bytes) < 6:
            return ""
        try:
            decoded = raw_bytes.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            return ""
        printable = sum(1 for c in decoded if c.isprintable() or c in ("\n", "\r", "\t"))
        if (printable / len(decoded)) < 0.90:
            return ""
        if not any(c.isalpha() for c in decoded):
            return ""
        return decoded

    @classmethod
    def _layer3_extract_encoded_payloads(cls, text: str, max_depth: int = 3) -> List[str]:
        """Capa 3: Decodificación heurística recursiva de payloads Base64 (>=20 chars) y hex embebidos."""
        decoded_texts: List[str] = []
        seen_candidates: Set[str] = set()
        queue: List[Tuple[str, int]] = [(text, 0)]

        while queue:
            current, depth = queue.pop(0)
            if depth >= max_depth:
                continue

            # Base64 estándar y URL-safe
            b64_tokens: List[str] = []
            for m in _B64_CANDIDATE_RE.finditer(current):
                b64_tokens.append(m.group(0))
            for m in _B64URL_CANDIDATE_RE.finditer(current):
                tok = m.group(0)
                if "-" in tok or tok.endswith("="):
                    b64_tokens.append(tok)

            for tok in b64_tokens:
                key_b = f'b64:{tok}'
                if key_b in seen_candidates:
                    continue
                seen_candidates.add(key_b)
                padded = tok + ("=" * ((4 - len(tok) % 4) % 4))
                raw = None
                try:
                    if "-" in tok or "_" in tok:
                        raw = base64.urlsafe_b64decode(padded)
                    else:
                        raw = base64.b64decode(padded, validate=True)
                except (binascii.Error, ValueError):
                    raw = None
                if raw is not None:
                    decoded = cls._is_plausible_decoded_text(raw)
                    if decoded:
                        norm_dec = cls._normalize_surface(decoded)
                        decoded_texts.append(norm_dec)
                        queue.append((norm_dec, depth + 1))

            # Secuencias hexadecimales continuas (>=20 chars)
            for m in _HEX_CANDIDATE_RE.finditer(current):
                hex_body = m.group(1)
                key_h = f'hex:{hex_body}'
                if key_h in seen_candidates:
                    continue
                seen_candidates.add(key_h)
                try:
                    raw = bytes.fromhex(hex_body)
                except ValueError:
                    continue
                decoded = cls._is_plausible_decoded_text(raw)
                if decoded:
                    norm_dec = cls._normalize_surface(decoded)
                    decoded_texts.append(norm_dec)
                    queue.append((norm_dec, depth + 1))

            # Escapes \xNN
            for m in _HEX_ESCAPE_RE.finditer(current):
                esc = m.group(0)
                key_e = f'esc:{esc}'
                if key_e in seen_candidates:
                    continue
                seen_candidates.add(key_e)
                hex_body = esc.replace("\\x", "")
                try:
                    raw = bytes.fromhex(hex_body)
                except ValueError:
                    continue
                decoded = cls._is_plausible_decoded_text(raw)
                if decoded:
                    norm_dec = cls._normalize_surface(decoded)
                    decoded_texts.append(norm_dec)
                    queue.append((norm_dec, depth + 1))

        return decoded_texts

    @staticmethod
    def _layer5_ast_taint_findings(code_text: str) -> List[ThreatFinding]:
        """Capa 5: Análisis de taint sobre AST de Python para ejecución peligrosa y bucles/except inseguros."""
        findings: List[ThreatFinding] = []
        try:
            tree = ast.parse(code_text)
        except SyntaxError:
            return findings

        dangerous_aliases: Dict[str, str] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                for alias in node.names:
                    local_name = alias.asname or alias.name
                    dangerous_aliases[local_name] = f"{node.module}.{alias.name}"
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    local_name = alias.asname or alias.name
                    dangerous_aliases[local_name] = alias.name

        seen_rules: Set[Tuple[str, str]] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                call_name = ""
                if isinstance(node.func, ast.Name):
                    call_name = dangerous_aliases.get(node.func.id, node.func.id)
                elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                    base = dangerous_aliases.get(node.func.value.id, node.func.value.id)
                    call_name = f"{base}.{node.func.attr}"

                snippet = ast.unparse(node)[:60]
                if call_name in ("eval", "exec", "builtins.eval", "builtins.exec"):
                    key = ("AEGIS-007", snippet)
                    if key not in seen_rules:
                        seen_rules.add(key)
                        findings.append(ThreatFinding(
                            rule_id="AEGIS-007",
                            severity="CRITICAL",
                            category="DANGEROUS_EXEC",
                            description=f"AST Taint: Invocación peligrosa a {call_name}()",
                            matched_snippet=snippet,
                        ))
                elif call_name in ("os.system", "os.popen", "pty.spawn"):
                    key = ("AEGIS-007", snippet)
                    if key not in seen_rules:
                        seen_rules.add(key)
                        findings.append(ThreatFinding(
                            rule_id="AEGIS-007",
                            severity="CRITICAL",
                            category="DANGEROUS_EXEC",
                            description=f"AST Taint: Ejecución de subproceso OS vía {call_name}()",
                            matched_snippet=snippet,
                        ))
                elif call_name == "shutil.rmtree" and node.args:
                    arg0 = node.args[0]
                    if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str) and arg0.value.strip() in ("/", "/*", "~"):
                        key = ("AEGIS-007", snippet)
                        if key not in seen_rules:
                            seen_rules.add(key)
                            findings.append(ThreatFinding(
                                rule_id="AEGIS-007",
                                severity="CRITICAL",
                                category="DANGEROUS_EXEC",
                                description="AST Taint: Eliminación destructiva del sistema de archivos con shutil.rmtree('/')",
                                matched_snippet=snippet,
                            ))
                elif call_name.startswith("subprocess."):
                    has_shell_true = any(
                        kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True
                        for kw in node.keywords
                    )
                    if has_shell_true:
                        key = ("AEGIS-007", snippet)
                        if key not in seen_rules:
                            seen_rules.add(key)
                            findings.append(ThreatFinding(
                                rule_id="AEGIS-007",
                                severity="CRITICAL",
                                category="DANGEROUS_EXEC",
                                description=f"AST Taint: {call_name}(..., shell=True) habilita inyección de shell",
                                matched_snippet=snippet,
                            ))

            elif isinstance(node, ast.While):
                if isinstance(node.test, ast.Constant) and node.test.value in (True, 1):
                    has_exit = any(
                        isinstance(sub, (ast.Break, ast.Return, ast.Raise, ast.Yield, ast.YieldFrom))
                        for sub in ast.walk(node)
                    )
                    if not has_exit:
                        snippet = ast.unparse(node)[:60]
                        key = ("AEGIS-005", snippet)
                        if key not in seen_rules:
                            seen_rules.add(key)
                            findings.append(ThreatFinding(
                                rule_id="AEGIS-005",
                                severity="HIGH",
                                category="RESOURCE_EXHAUSTION",
                                description="Bucle infinito determinista detectado en AST (while True sin break/return)",
                                matched_snippet=snippet,
                            ))

            elif isinstance(node, ast.ExceptHandler):
                if node.type is None and len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    snippet = ast.unparse(node)[:60]
                    key = ("AEGIS-006", snippet)
                    if key not in seen_rules:
                        seen_rules.add(key)
                        findings.append(ThreatFinding(
                            rule_id="AEGIS-006",
                            severity="HIGH",
                            category="ANTI_PATTERN",
                            description="Violación de robustez en AST: except silencioso sin logging ni re-raise",
                            matched_snippet=snippet,
                        ))

        return findings

    @classmethod
    def scan_text(cls, text: str) -> SecurityScanReport:
        if not text:
            return SecurityScanReport(safe=True, findings=[])

        raw_str = str(text)
        normalized = cls._normalize_surface(raw_str)
        decoded_layers = cls._layer3_extract_encoded_payloads(normalized)

        surfaces: List[str] = [raw_str]
        if normalized != raw_str:
            surfaces.append(normalized)
        surfaces.extend(decoded_layers)

        findings: List[ThreatFinding] = []
        seen_rule_ids: Set[str] = set()

        for surface in surfaces:
            for rule_id, sev, cat, desc, regex in cls.PATTERNS:
                if rule_id in seen_rule_ids:
                    continue
                m = regex.search(surface)
                if m:
                    seen_rule_ids.add(rule_id)
                    findings.append(ThreatFinding(
                        rule_id=rule_id,
                        severity=sev,
                        category=cat,
                        description=desc,
                        matched_snippet=m.group(0)[:60],
                    ))

        for surface in surfaces:
            for ast_finding in cls._layer5_ast_taint_findings(surface):
                if ast_finding.rule_id not in seen_rule_ids:
                    seen_rule_ids.add(ast_finding.rule_id)
                    findings.append(ast_finding)

        safe = not any(f.severity in ("CRITICAL", "HIGH") for f in findings)
        return SecurityScanReport(safe=safe, findings=findings)

    @classmethod
    def scan_payload(cls, payload: Any) -> SecurityScanReport:
        raw = json.dumps(payload, ensure_ascii=False) if isinstance(payload, (dict, list)) else str(payload)
        return cls.scan_text(raw)
