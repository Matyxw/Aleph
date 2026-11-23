"""
Controlador Ejecutivo Pre-Flight de El Aleph (Ronda 6):
- Matriz de Decisión Multivariable (Pareto 6 Ejes) determinista (< 50 ms, 0 tokens LLM).
- Autoconciencia JIT de herramientas (perfil sovereign 12 tools + patrón BM25 discover).
- Auto-Recall Top-3 de reglas activas Bitácora / CANONICAL_RULES sin cargar research_archive.
- Síntesis compacta executive_brief <= 320 tokens BPE (sin Context Rot).
"""
from __future__ import annotations

import json
import logging
import os
import re
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from aleph_core.router.cost_router import SovereignCostRouter
from aleph_core.router.dispatcher import estimate_bpe_tokens

_LOG = logging.getLogger(__name__)

SOVEREIGN_12_TOOLS: Tuple[str, ...] = (
    "aleph_verify_and_repair",
    "aleph_apply_semantic_patch",
    "aleph_run_optimality_tournament",
    "aleph_bitacora_query_hipporag2_ppr",
    "aleph_bitacora_enforce_pre_turn_gate",
    "aleph_bitacora_learn_experiential_rule",
    "aleph_omega_dgm_alphaevolve_self_improve",
    "aleph_bitacora_vault_status_and_telemetry",
    "aleph_prove_omega_continual_self_improvement_hipporag2_titans_zero_forgetting_and_bitacora_vault",
    "aleph_analyze_interprocedural_taint",
    "aleph_verify_deep_supabase_rls",
    "aleph_discover_or_invoke",
)

_BASELINE_RULES: Tuple[Dict[str, str], ...] = (
    {"rule_id": "REG-001", "category": "Seguridad", "directive": "Validar contratos AST/Z3 y guardas antes de ejecutar."},
    {"rule_id": "REG-002", "category": "Routing", "directive": "Routing asimétrico Tier 0..3 ($0 en Gemini 4)."},
    {"rule_id": "REG-006", "category": "Código", "directive": "Exigir terminación en bucles y cero except silencioso."},
    {"rule_id": "REG-007", "category": "Arquitectura", "directive": "Torneo Pareto: implementar solución SOTA #1."},
)

_DESTRUCTIVE_RE = re.compile(
    r"\b(?:rm\s+-rf|drop\s+table|truncate\s+table|delete\s+from|git\s+push\s+--force|format\s+[a-z]:)\b",
    re.IGNORECASE,
)

_UI_FILE_EXTS = (".html", ".css", ".scss", ".tsx", ".jsx", ".vue", ".svelte", ".astro")
_UI_INTENT_RE = re.compile(
    r"(?:\b(?:ui|ux|frontend|interfaz|dise[nñ]o|design|landing|dashboard|componente|css|html|scss|"
    r"tailwind|react|next\.?js|svelte|astro|solidjs|three\.?js|webgl|webgpu|glsl|shader|"
    r"gsap|lenis|figma|oklch|wcag|bento|swiftui|flutter|portfolio|awwwards|soty|"
    r"keyframes|viewport)\b|p[aá]gina\s+web|web\s+app)",
    re.IGNORECASE,
)
_AVANT_GARDE_RE = re.compile(
    r"\b(?:awwwards|soty|lujo|luxury|inmersiv|immersive|webgl|webgpu|glsl|shader|"
    r"three\.?js|r3f|gsap|lenis|scrolltrigger|portfolio|lanzamiento|launch|3d)\b",
    re.IGNORECASE,
)
_HYPER_SPEED_RE = re.compile(
    r"\b(?:trading|terminal|orderbook|m[eé]dic|clinic|telemetr|baja\s+latencia|"
    r"low\s+latency|sub-ms|high\s+density|alta\s+densidad|tabla\s+masiva|monitoring)\b",
    re.IGNORECASE,
)
_STOP_SUFFIXES = {"de", "del", "la", "el", "los", "las", "y", "o", "en", "con", "para", "por", "a", "si"}


def _clean_word_truncate(text: str, max_chars: int = 58) -> str:
    clean = " ".join(str(text or "").split())
    if len(clean) <= max_chars:
        return clean
    clipped = clean[:max_chars]
    if " " in clipped:
        clipped = clipped.rsplit(" ", 1)[0]
    words = clipped.rstrip(" ,;:-").split(" ")
    while len(words) > 3 and (words[-1].lower().strip(".,;:") in _STOP_SUFFIXES or words[-1].startswith("(")):
        words.pop()
    return " ".join(words).rstrip(" ,;:-(")


def _classify_design_turn(safe_prompt: str, files: List[str]) -> Tuple[bool, Optional[str], Optional[str]]:
    has_ui_file = any(str(f).lower().endswith(_UI_FILE_EXTS) for f in files)
    has_ui_intent = bool(_UI_INTENT_RE.search(safe_prompt))
    if not (has_ui_file or has_ui_intent):
        return False, None, None
    if _AVANT_GARDE_RE.search(safe_prompt):
        return True, "AVANT_GARDE_SOTY", "R3F/WebGPU-TSL+HDRI+GSAP+shadcn/@react-bits"
    if _HYPER_SPEED_RE.search(safe_prompt):
        return True, "HYPER_SPEED", "Astro/Svelte5 o SolidJS + CSS @layer Zero-Jank"
    return True, "ELITE_PRODUCT", "React19+OKLCH+shadcn/@react-bits+Spring"


def _tokenize(text: str) -> set:
    if not text:
        return set()
    return set(re.findall(r"[a-z0-9_]{3,}", text.lower()))


def _load_candidate_rules(root_path: Path) -> List[Dict[str, str]]:
    if root_path is None:
        return [dict(r) for r in _BASELINE_RULES]
    collected: Dict[str, Dict[str, str]] = {}
    for base_r in _BASELINE_RULES:
        bid = str(base_r.get("rule_id", ""))
        collected[bid] = dict(base_r)

    canon_file = Path(os.path.join(str(root_path), ".aleph", "rules", "CANONICAL_RULES.json"))
    if canon_file.exists():
        try:
            raw = json.loads(canon_file.read_text(encoding="utf-8"))
            for item in raw.get("rules", []):
                if isinstance(item, dict) and item.get("id"):
                    rid = str(item.get("id", ""))
                    collected[rid] = {
                        "rule_id": rid,
                        "category": str(item.get("category", "governance")),
                        "directive": str(item.get("directive", item.get("title", "")))[:180],
                    }
        except Exception as exc:
            _LOG.debug("Skipping canonical rules load: %s", exc)

    evo_db = Path(os.path.join(str(root_path), ".aleph", "runtime", "session_evolution.db"))
    if evo_db.exists():
        conn = None
        try:
            conn = sqlite3.connect(str(evo_db), timeout=1.0)
            rows = conn.execute(
                "SELECT rule_id, category, if_condition, then_action FROM algorithmic_rules "
                "WHERE status = 'Activa' ORDER BY confidence DESC, hit_count DESC LIMIT 24"
            ).fetchall()
            for row in rows:
                rid = str(row[0])
                collected[rid] = {
                    "rule_id": rid,
                    "category": str(row[1]),
                    "directive": _clean_word_truncate(str(row[3] or row[2]), 120),
                }
        except Exception as exc:
            _LOG.debug("Skipping runtime evolution db recall: %s", exc)
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception as close_exc:
                    _LOG.debug("Close sqlite error ignored: %s", close_exc)
    return list(collected.values())


def _recall_top_rules(prompt_lower: str, root_path: Path, limit: int = 3) -> List[Dict[str, str]]:
    q_tokens = _tokenize(prompt_lower)
    rules = _load_candidate_rules(root_path)
    scored: List[Tuple[int, str, Dict[str, str]]] = []
    for r in rules:
        blob = f"{r.get('rule_id', '')} {r.get('category', '')} {r.get('directive', '')}".lower()
        overlap = len(q_tokens & _tokenize(blob))
        bonus = 1 if r.get("rule_id") in ("REG-001", "REG-006", "REG-007") else 0
        scored.append((overlap * 10 + bonus, str(r.get("rule_id", "")), r))
    scored.sort(key=lambda item: (-item[0], item[1]))
    top: List[Dict[str, str]] = []
    for _, _, r in scored[: max(1, limit)]:
        top.append({
            "rule_id": str(r.get("rule_id", "")),
            "category": str(r.get("category", "")),
            "directive": _clean_word_truncate(str(r.get("directive", "")), 140),
        })
    return top


def _select_jit_tools(
    prompt_lower: str,
    changed_files: List[str],
    is_design_turn: bool = False,
) -> Tuple[List[str], Optional[str]]:
    selected: List[str] = []
    bm25_hint: Optional[str] = None

    def _add(name: str) -> None:
        if name in SOVEREIGN_12_TOOLS and name not in selected:
            selected.append(name)

    if is_design_turn:
        _add("aleph_discover_or_invoke")
        bm25_hint = "aleph_design_create aleph_design_compile aleph_design_audit aleph_audit_and_repair_design_tokens_wcag"
    if any(k in prompt_lower for k in ("rls", "supabase", "postgres", "sql", "ddl", "schema", "migration")):
        _add("aleph_verify_deep_supabase_rls")
    if any(k in prompt_lower for k in ("taint", "ssrf", "xss", "security", "seguridad", "injection", "auth", "token", "secret")):
        _add("aleph_analyze_interprocedural_taint")
        _add("aleph_bitacora_enforce_pre_turn_gate")
    if any(k in prompt_lower for k in ("z3", "smt", "bug", "error", "fix", "repar", "fail", "contract", "invariant", "verify", "test")):
        _add("aleph_verify_and_repair")
    if any(k in prompt_lower for k in ("refactor", "patch", "edit", "modif", "cambiar", "implement")):
        _add("aleph_apply_semantic_patch")
    if any(k in prompt_lower for k in ("arquitect", "sota", "pareto", "optim", "compar", "benchmark", "strategy")):
        _add("aleph_run_optimality_tournament")
    if any(k in prompt_lower for k in ("gepa", "learn", "evol", "bitacora", "regla", "rule", "memory")):
        _add("aleph_bitacora_query_hipporag2_ppr")
        _add("aleph_omega_dgm_alphaevolve_self_improve")
    if not is_design_turn and any(k in prompt_lower for k in ("fsm", "ledger", "equivalence")):
        _add("aleph_discover_or_invoke")
        bm25_hint = "relational_equivalence | fsm_ledger"

    if changed_files and "aleph_verify_and_repair" not in selected:
        _add("aleph_verify_and_repair")
    if not selected:
        _add("aleph_bitacora_enforce_pre_turn_gate")
        _add("aleph_verify_and_repair")
    return selected[:4], bm25_hint


class ExecutivePreflight:
    """Controlador Ejecutivo Pre-Flight con Matriz Pareto 6 Ejes, Autoconciencia JIT y Auto-Recall Bitácora."""

    MAX_BRIEF_BPE_TOKENS = 320

    @classmethod
    def analyze(
        cls,
        prompt: str,
        repo_root: Optional[str] = None,
        changed_files: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        t0 = time.perf_counter_ns()
        safe_prompt = "" if prompt is None else str(prompt)
        prompt_lower = safe_prompt.lower()
        files = [str(f) for f in (changed_files or [])]
        root_path = Path(repo_root) if repo_root else Path(__file__).resolve().parents[2]

        alloc = SovereignCostRouter.allocate_dag_compute({"prompt": safe_prompt}, total_token_budget=4096)
        node_alloc = alloc.get("allocations", {}).get("prompt", {})
        tier = str(node_alloc.get("tier", "TIER_2_LIGHTWEIGHT_SOVEREIGN"))
        selected_model = str(node_alloc.get("selected_model", "gemini-4-neon"))
        variant = str(node_alloc.get("gemini4_variant", "Neon"))
        token_budget = int(node_alloc.get("token_budget", 1536))
        entropy_bits = float(node_alloc.get("shannon_entropy_bits", 0.0))

        is_destructive = bool(_DESTRUCTIVE_RE.search(safe_prompt))
        is_urgent = any(k in prompt_lower for k in ("rápido", "rapido", "urgente", "hotfix", "asap", "quick", "ahora"))
        is_deep = any(k in prompt_lower for k in ("z3", "rls", "arquitect", "pareto", "distrib", "concurren", "dag", "sota", "security"))

        if is_destructive:
            risk_level = "HIGH_CRITICAL_CHECKPOINT"
        elif files or is_deep:
            risk_level = "MEDIUM_GUARDED"
        else:
            risk_level = "LOW_SAFE"

        if len(files) > 3 or any(k in prompt_lower for k in ("multi", "dag", "worktree", "distrib", "pipeline", "repo")):
            scalability_scope = "DISTRIBUTED_DAG_WORKTREE"
        elif len(files) >= 1 or any(k in prompt_lower for k in ("archivo", "módulo", "modulo", "refactor", "module", "hook")):
            scalability_scope = "MULTI_FILE_MODULE"
        else:
            scalability_scope = "SINGLE_SYMBOL_LOCAL"

        if is_urgent and not is_destructive and not is_deep:
            time_urgency, urgency_score = "FAST_DIRECT", 0.90
        elif is_deep or scalability_scope == "DISTRIBUTED_DAG_WORKTREE":
            time_urgency, urgency_score = "DEEP_VERIFIED", 0.45
        else:
            time_urgency, urgency_score = "BALANCED_ITERATIVE", 0.65

        if risk_level == "LOW_SAFE" and tier == "TIER_0_DETERMINISTIC_AST_CAS":
            quality_gate = "AST_SMOKE"
            opp_cost = "SKIP_HEAVY_PROVERS"
            discarded = ["full_repo_z3_scan", "multi_agent_tournament"]
        elif scalability_scope == "DISTRIBUTED_DAG_WORKTREE" or "sota" in prompt_lower or "pareto" in prompt_lower:
            quality_gate = "FULL_Z3_CEGIS_AND_PARETO"
            opp_cost = "FULL_FORMAL_INVESTMENT"
            discarded = ["unverified_fast_patch"]
        else:
            quality_gate = "INCREMENTAL_Z3_GIT_GATE"
            opp_cost = "SELECTIVE_INCREMENTAL_VERIFY"
            discarded = ["research_archive_full_scan"]

        if is_destructive:
            execution_strategy = "GUARDED_HUMAN_CHECKPOINT"
        elif tier == "TIER_0_DETERMINISTIC_AST_CAS" and risk_level == "LOW_SAFE":
            execution_strategy = "DIRECT_TIER0_FAST_PATH"
        elif quality_gate == "FULL_Z3_CEGIS_AND_PARETO":
            execution_strategy = "DAG_WORKTREE_PARETO_TOURNAMENT"
        else:
            execution_strategy = "PROACTIVE_SOVEREIGN_VERIFIED"

        pareto_matrix_6d: Dict[str, Any] = {
            "time_urgency": {"mode": time_urgency, "score": urgency_score},
            "compute_tier": {
                "tier": tier,
                "selected_model": selected_model,
                "variant": variant,
                "token_budget": token_budget,
                "shannon_entropy_bits": entropy_bits,
            },
            "quality_gate": quality_gate,
            "opportunity_cost": {"mode": opp_cost, "discarded_steps": discarded},
            "scalability_scope": scalability_scope,
            "risk_level": {
                "level": risk_level,
                "requires_human_confirmation": is_destructive,
            },
        }

        is_design_turn, design_mode, design_stack_hint = _classify_design_turn(safe_prompt, files)
        tools_selected, bm25_hint = _select_jit_tools(prompt_lower, files, is_design_turn=is_design_turn)
        recalled_rules = _recall_top_rules(prompt_lower, root_path, limit=3)

        rule_tags = "; ".join(
            f"{r.get('rule_id')}: {_clean_word_truncate(str(r.get('directive', '')), 56)}" for r in recalled_rules
        )
        tools_csv = ", ".join(tools_selected)
        discover_note = f" | BM25:{bm25_hint}" if bm25_hint else ""
        brief_lines = [
            f"[EXEC] strategy={execution_strategy} | tier={variant}({selected_model}) | gate={quality_gate}",
            f"[PARETO-6D] urgency={time_urgency} scope={scalability_scope} risk={risk_level} opp={opp_cost}",
            f"[JIT-TOOLS] {tools_csv}{discover_note}",
            f"[BITACORA-TOP3] {rule_tags}",
        ]
        if is_design_turn and design_mode:
            if design_mode == "AVANT_GARDE_SOTY":
                skills_tag = "design-taste-frontend+impeccable+awwwards-animations+r3f-skills+threejs-shaders+review-animations"
            elif design_mode == "ELITE_PRODUCT":
                skills_tag = "design-taste-frontend+impeccable+emil-design-eng+review-animations"
            else:
                skills_tag = "design-taste-frontend+impeccable"
            brief_lines.insert(
                2,
                f"[DESIGN] mode={design_mode} | skills={skills_tag} | stack={design_stack_hint}",
            )
        executive_brief = "\n".join(brief_lines)
        while estimate_bpe_tokens(executive_brief) > cls.MAX_BRIEF_BPE_TOKENS and "\n" in executive_brief:
            lines_cur = executive_brief.splitlines()
            if len(lines_cur[-1]) > 48:
                lines_cur[-1] = _clean_word_truncate(lines_cur[-1], int(len(lines_cur[-1]) * 0.8))
                executive_brief = "\n".join(lines_cur)
            else:
                break

        bpe_tokens = estimate_bpe_tokens(executive_brief)
        latency_ms = round((time.perf_counter_ns() - t0) / 1_000_000.0, 3)

        return {
            "pareto_matrix_6d": pareto_matrix_6d,
            "proactive_tools_selected": tools_selected,
            "bitacora_rules_recalled": recalled_rules,
            "execution_strategy": execution_strategy,
            "is_design_turn": is_design_turn,
            "design_mode": design_mode,
            "design_stack_hint": design_stack_hint,
            "executive_brief": executive_brief,
            "executive_brief_bpe_tokens": bpe_tokens,
            "bm25_discover_pattern": bm25_hint,
            "analysis_latency_ms": latency_ms,
        }
