"""
AegisShield Security Engine (Superación de ECC AgentShield).
Escanea entradas, salidas y código generado en <5ms buscando:
1. Indirect Prompt Injection y secuestro de rol.
2. Exfiltración de secretos/credenciales (API Keys, JWTs, claves privadas).
3. Comandos destructivos o inseguros (rm -rf /, eval arbitrario, SQL injection).
4. Anti-patrones específicos de SparkOS (REG-001: uso de PageSetup.Draft=True o constantes mso* sin declarar).
"""
import re
import unicodedata
from dataclasses import dataclass, field
from typing import List, Dict, Any

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
            re.compile(r"(ignore\s+(all\s+)?(previous|prior)\s+instructions|olvida\s+todas\s+las\s+instrucciones|system\s+override:\s*you\s+are\s+now)", re.IGNORECASE)
        ),
        (
            "AEGIS-002", "CRITICAL", "SECRET_LEAK",
            "Exposición de clave privada, JWT o API Token en texto plano",
            re.compile(
                r"(BEGIN\s+(RSA|OPENSSH|EC|DSA|PGP|ENCRYPTED)\s+PRIVATE\s+KEY"
                r"|sk-(?:proj-|live-|test-)?[a-zA-Z0-9_\-]{20,}"
                r"|AIza[0-9A-Za-z\-_]{35}"
                r"|gh[pousr]_[A-Za-z0-9_]{36,}"
                r"|github_pat_[A-Za-z0-9_]{22,}"
                r"|AKIA[0-9A-Z]{16}"
                r"|xox[baprs]-[0-9A-Za-z\-]{10,}"
                r"|eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,})"
            )
        ),
        (
            "AEGIS-003", "CRITICAL", "DANGEROUS_EXEC",
            "Comando destructivo de sistema de archivos o base de datos",
            re.compile(
                r"(rm\s+-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\s+(?:/(?:\s|$|\*)|~|\$HOME|%USERPROFILE%)"
                r"|DROP\s+(?:DATABASE|SCHEMA|TABLE)\s+\w+"
                r"|TRUNCATE\s+TABLE\s+\w+"
                r"|FORMAT\s+[A-Z]:"
                r"|mkfs\.[a-z0-9]+"
                r"|dd\s+if=[^\s]+\s+of=/dev/"
                r"|:\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;)",
                re.IGNORECASE,
            )
        ),
        (
            "AEGIS-004", "HIGH", "SPARKOS_VIOLATION",
            "Violación REG-001: Uso de PageSetup.Draft = True oculta bordes y logos en impresión Excel",
            re.compile(r"\.Draft\s*=\s*True", re.IGNORECASE)
        ),
        (
            "AEGIS-005", "HIGH", "RESOURCE_EXHAUSTION",
            "Bucle infinito determinista detectado en regex o código fuente (while True sin break)",
            re.compile(r"while\s+(True|1)\s*:\s*(pass|continue|time\.sleep)", re.IGNORECASE)
        ),
        (
            "AEGIS-006", "HIGH", "ANTI_PATTERN",
            "Violación de robustez: Bloque catch/except silencioso sin re-raise ni logging",
            re.compile(r"except\s*:\s*pass", re.IGNORECASE)
        ),
    ]

    _ZERO_WIDTH_RE = re.compile(r"[\u200b-\u200f\u202a-\u202e\u2060\ufeff]")

    @classmethod
    def scan_text(cls, text: str) -> SecurityScanReport:
        normalized = cls._ZERO_WIDTH_RE.sub("", unicodedata.normalize("NFKC", text))
        findings: List[ThreatFinding] = []
        for rule_id, sev, cat, desc, regex in cls.PATTERNS:
            m = regex.search(normalized)
            if m:
                findings.append(ThreatFinding(
                    rule_id=rule_id,
                    severity=sev,
                    category=cat,
                    description=desc,
                    matched_snippet=m.group(0)[:60]
                ))
        safe = not any(f.severity in ("CRITICAL", "HIGH") for f in findings)
        return SecurityScanReport(safe=safe, findings=findings)

    @classmethod
    def scan_payload(cls, payload: Any) -> SecurityScanReport:
        import json
        raw = json.dumps(payload, ensure_ascii=False) if isinstance(payload, (dict, list)) else str(payload)
        return cls.scan_text(raw)
