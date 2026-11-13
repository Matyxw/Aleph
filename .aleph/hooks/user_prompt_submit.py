#!/usr/bin/env python3
"""Hook Nativo: UserPromptSubmit (HippoRAG 2 PPR Bitácora Routing + Defensa Prompt Injection)."""
from pathlib import Path
import sys
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from aleph_core.engine import get_shared_omega_engine
from aleph_core.security.aegis_shield import AegisShield


def evaluate_user_prompt(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Filtra intentos de secuestro de rol con AegisShield e inyecta reglas Bitácora pertinentes."""
    prompt = str(payload.get("prompt") or payload.get("user_prompt") or "")
    sec_report = AegisShield.scan_text(prompt)
    if not sec_report.safe:
        return {
            "prompt_len": len(prompt),
            "allowed": False,
            "matched_rule_ids": [],
            "security_findings": [f.rule_id for f in sec_report.findings],
            "exit_code": 2,
            "hook": "UserPromptSubmit",
        }

    omega = get_shared_omega_engine()
    ranked = omega.query_hipporag2_ppr(prompt or "general", top_k=5) if prompt.strip() else []
    rule_ids = [item.get("canon_id") for item in ranked if item.get("canon_id")]
    return {
        "prompt_len": len(prompt),
        "allowed": True,
        "matched_rule_ids": rule_ids,
        "security_findings": [],
        "exit_code": 0,
        "hook": "UserPromptSubmit",
    }
