#!/usr/bin/env python3
"""
.aleph/hooks/user_prompt_submit.py
Hook Nativo: UserPromptSubmit (Tier-0 VSA + BM25 Skill & Domain Routing).
Clasifica el dominio técnico del prompt del usuario e identifica las compuertas formales requeridas.
"""
from __future__ import annotations

import json
import re
import sys
from typing import Any, Dict, List


DOMAIN_KEYWORDS: Dict[str, List[str]] = {
    "NODE-01_FORMAL_SMT": ["z3", "smt", "prover", "invariant", "requires", "ensures", "ast", "bft", "raft"],
    "NODE-02_UI_UX_DESIGN": ["css", "html", "react", "oklch", "apca", "bento", "layout", "wcag", "subgrid", "spring"],
    "NODE-03_POSTGRES_DB": ["postgres", "sql", "supabase", "rls", "ddl", "index", "partition", "pgvector", "vacuum"],
    "NODE-04_SECURITY_PQC": ["security", "oauth", "token", "hmac", "pqc", "taint", "ssrf", "xss", "injection"],
    "NODE-05_PAGERANK_REPO": ["pagerank", "repomap", "kv-cache", "rust", "miri", "verus", "lean", "chebyshev"],
}


def evaluate_user_prompt(payload: Dict[str, Any]) -> Dict[str, Any]:
    prompt = str(payload.get("prompt", ""))
    lower_prompt = prompt.lower()
    matched_domains: List[str] = []
    for domain, kws in DOMAIN_KEYWORDS.items():
        if any(kw in lower_prompt for kw in kws):
            matched_domains.append(domain)
    if not matched_domains:
        matched_domains.append("GENERAL_SOVEREIGN_ENGINEERING")

    tokens = re.findall(r"[A-Za-z0-9_:\-\.]{3,}", prompt)
    return {
        "prompt_len": len(prompt),
        "token_count": len(tokens),
        "routed_domains": matched_domains,
        "exit_code": 0,
        "hook": "UserPromptSubmit",
    }


def main() -> int:
    raw = sys.stdin.read().strip() if not sys.stdin.isatty() else "{}"
    try:
        payload = json.loads(raw or "{}")
    except json.JSONDecodeError:
        payload = {"prompt": raw}
    res = evaluate_user_prompt(payload)
    sys.stdout.write(json.dumps(res, ensure_ascii=False) + "\n")
    return int(res["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
