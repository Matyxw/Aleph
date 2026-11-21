#!/usr/bin/env python3
"""
.aleph/hooks/user_prompt_submit.py
Hook Nativo: UserPromptSubmit (Tier-0 VSA + BM25 Skill & Domain Routing).
Clasifica el dominio técnico del prompt del usuario e identifica las compuertas formales requeridas.
"""
from __future__ import annotations

import json
from pathlib import Path
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


def _route_jit_compute(prompt: str) -> Dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    try:
        from aleph_core.router.cost_router import SovereignCostRouter
    except ImportError:
        return {}
    alloc = SovereignCostRouter.allocate_dag_compute({"prompt": prompt}, total_token_budget=4096)
    node_alloc = alloc.get("allocations", {}).get("prompt", {})
    return {
        "assigned_compute_tier": node_alloc.get("tier", "TIER_2_LIGHTWEIGHT_SOVEREIGN"),
        "jit_token_budget": int(node_alloc.get("token_budget", 1536)),
        "shannon_entropy_bits": float(node_alloc.get("shannon_entropy_bits", 0.0)),
        "static_catalog_avoided_tokens": max(0, 4096 - int(node_alloc.get("token_budget", 1536))),
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
    out: Dict[str, Any] = {
        "prompt_len": len(prompt),
        "token_count": len(tokens),
        "routed_domains": matched_domains,
        "exit_code": 0,
        "hook": "UserPromptSubmit",
    }
    jit_info = _route_jit_compute(prompt)
    if jit_info:
        out.update(jit_info)
    return out


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
