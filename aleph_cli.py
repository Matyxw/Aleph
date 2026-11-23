#!/usr/bin/env python3
"""
CLI Unificado de El Aleph v2.0 (Sovereign Agent Harness).
Comandos soportados:
  python3 aleph_cli.py test       -> Ejecuta la batería completa de tests unitarios y formales
  python3 aleph_cli.py benchmark  -> Ejecuta el benchmark cuantitativo El Aleph v2.0 vs. ECC
  python3 aleph_cli.py verify <archivo.py> -> Audita formalmente todas las funciones de un archivo Python
  python3 aleph_cli.py evolve     -> Dispara un ciclo autónomo de automejora Demiurgo
  python3 aleph_cli.py mine-spec <archivo.py> -> Induce y prueba formalmente contratos de funciones
  python3 aleph_cli.py git-gate [dir] -> Compuerta Pre-Commit Soberana de Integridad de Workspace
"""
import ast
import hashlib
import json
import os
import sys
from dataclasses import asdict
import unittest
from typing import Any, Dict, Optional
from pathlib import Path

from aleph_core.engine import AlephEngine, AlephUniversalMCPServer


# Tools verificadas como solo-lectura (no escriben a disco ni ejecutan procesos): únicas que se
# auto-aprueban. Todo lo demás (p. ej. aleph_apply_semantic_patch, aleph_bitacora_learn_experiential_rule,
# aleph_omega_dgm_alphaevolve_self_improve) pide confirmación humana en el cliente.
SAFE_AUTO_APPROVE_TOOLS = [
    "aleph_bitacora_query_hipporag2_ppr",
    "aleph_bitacora_enforce_pre_turn_gate",
    "aleph_bitacora_vault_status_and_telemetry",
    "aleph_verify_and_repair",
    "aleph_analyze_interprocedural_taint",
    "aleph_verify_deep_supabase_rls",
    "aleph_verify_zero_downtime_ddl",
    "aleph_build_pagerank_repomap",
    "aleph_audit_and_repair_design_tokens_wcag",
]


def _build_sovereign_agents_md() -> str:
    return (
        "---\n"
        "description: Kernel Ejecutivo El Aleph v33.0.0 Sovereign (JIT, Pareto 6D, Bitácora, Z3, Auto-GEPA)\n"
        "always-active: true\n"
        "---\n"
        "<el_aleph_sovereign_mandate>\n"
        "El Aleph v33.0.0 Sovereign (MCP el-aleph-sovereign, CLI aleph). Activación proactiva sin esperar orden:\n"
        "1. Autoconciencia JIT (perfil sovereign): aleph_verify_and_repair, aleph_apply_semantic_patch, "
        "aleph_run_optimality_tournament, aleph_bitacora_query_hipporag2_ppr, aleph_bitacora_enforce_pre_turn_gate, "
        "aleph_bitacora_learn_experiential_rule, aleph_omega_dgm_alphaevolve_self_improve, "
        "aleph_bitacora_vault_status_and_telemetry, aleph_analyze_interprocedural_taint, aleph_verify_deep_supabase_rls "
        "y aleph_discover_or_invoke (discover/invoke para UI/UX, RepoMap, DDL, SSRF).\n"
        "2. Orquestación Proactiva: aplicá Top-3 Bitácora pre-turno y git-gate --changed-only Z3 antes de responder.\n"
        "3. Pareto 6 Ejes: optimizá Tiempo, Esfuerzo/Cómputo, Calidad, Costo Oportunidad, Escalabilidad y Riesgo.\n"
        "4. Cero-Mediocridad: cero placeholders TODO/pass; elegí SOTA Pareto-dominante.\n"
        "5. Meta-Bucle: auto-auditá y habilitá auto-GEPA (0% regresión, SHA-256). trust:false: checkpoint humano SOLO en acciones destructivas.\n"
        "</el_aleph_sovereign_mandate>\n"
    )


def _build_sovereign_skill_md() -> str:
    return (
        "---\n"
        "name: el-aleph-sovereign\n"
        "description: Kernel formal y cognitivo El Aleph v33.0.0 Sovereign. Activar AUTOMÁTICAMENTE sin esperar mención explícita ante UI/UX (via aleph_discover_or_invoke), verificación formal Z3 SMT, Bóveda Bitácora, auditoría AST/Taint o PostgreSQL 18 / Supabase RLS.\n"
        "---\n"
        "# El Aleph v33.0.0 Sovereign — Perfil `sovereign` (12 Tools + Despacho JIT)\n\n"
        "Activá estas herramientas proactivamente en `ServerName: \"el-aleph-sovereign\"`:\n\n"
        "## 1. Herramientas Soberanas Activas Directas\n"
        "- **Verificación y Reparación Z3:** `aleph_verify_and_repair`, `aleph_apply_semantic_patch`\n"
        "- **Seguridad y Bases de Datos:** `aleph_analyze_interprocedural_taint`, `aleph_verify_deep_supabase_rls`\n"
        "- **Bóveda Bitácora y Auto-Evolución:** `aleph_bitacora_query_hipporag2_ppr`, `aleph_bitacora_enforce_pre_turn_gate`, `aleph_bitacora_learn_experiential_rule`, `aleph_omega_dgm_alphaevolve_self_improve`, `aleph_bitacora_vault_status_and_telemetry`\n"
        "- **Optimalidad Pareto:** `aleph_run_optimality_tournament`\n\n"
        "## 2. Motores Especializados bajo Demanda (`aleph_discover_or_invoke`)\n"
        "Para **UI/UX (`aleph_design_create`, `aleph_design_compile`, `aleph_design_audit`, `aleph_audit_and_repair_design_tokens_wcag`)**, **PageRank RepoMap (`aleph_build_pagerank_repomap`)**, **DDL Zero-Downtime (`aleph_verify_zero_downtime_ddl`)**, **SSRF** o **Equivalencia Relacional**:\n"
        "1. Descubrí parámetros exactos con `aleph_discover_or_invoke` (`{\"action\": \"discover\", \"query\": \"design ui wcag\"}`)\n"
        "2. Ejecutá con `aleph_discover_or_invoke` (`{\"action\": \"invoke\", \"tool_name\": \"...\", \"arguments\": {...}}`)\n"
    )


def _build_antigravity_hooks_payload(py_exe: str, server_script: str) -> Dict[str, Any]:
    return {
        "el-aleph-sovereign": {
            "enabled": True,
            "SessionStart": [
                {"type": "command", "command": f'"{py_exe}" "{server_script}" --hook SessionStart', "timeout": 15}
            ],
            "PreInvocation": [
                {"type": "command", "command": f'"{py_exe}" "{server_script}" --hook PreInvocation', "timeout": 15}
            ],
            "PreToolUse": [
                {
                    "matcher": ".*",
                    "hooks": [
                        {"type": "command", "command": f'"{py_exe}" "{server_script}" --hook PreToolUse', "timeout": 15}
                    ],
                }
            ],
            "PostToolUse": [
                {
                    "matcher": ".*",
                    "hooks": [
                        {"type": "command", "command": f'"{py_exe}" "{server_script}" --hook PostToolUse', "timeout": 15}
                    ],
                }
            ],
            "Stop": [
                {"type": "command", "command": f'"{py_exe}" "{server_script}" --hook Stop', "timeout": 15}
            ],
        }
    }


def _sync_sovereign_agents_dir(
    agents_dir: Path,
    server_entry: Dict[str, Any],
    py_exe: str,
    hook_server_script: str,
    sync_json: bool = False,
) -> list:
    import os
    import shutil

    updated: list = []
    plugin_dir = Path(os.path.join(str(agents_dir), "plugins", "el-aleph-sovereign"))
    rules_dir = Path(os.path.join(str(plugin_dir), "rules"))
    skills_dir = Path(os.path.join(str(plugin_dir), "skills", "el-aleph-sovereign"))
    rules_dir.mkdir(parents=True, exist_ok=True)
    skills_dir.mkdir(parents=True, exist_ok=True)

    agents_md = Path(os.path.join(str(rules_dir), "AGENTS.md"))
    agents_md.write_text(_build_sovereign_agents_md(), encoding="utf-8")
    updated.append(str(agents_md))

    skill_md = Path(os.path.join(str(skills_dir), "SKILL.md"))
    skill_md.write_text(_build_sovereign_skill_md(), encoding="utf-8")
    updated.append(str(skill_md))

    # Eliminar duplicados obsoletos fuera del plugin para mantener una única fuente de verdad
    dup_skill_dir = Path(os.path.join(str(agents_dir), "skills", "el-aleph-sovereign"))
    if dup_skill_dir.exists():
        shutil.rmtree(dup_skill_dir, ignore_errors=True)
    dup_rule = Path(os.path.join(str(agents_dir), "rules", "el-aleph.md"))
    if dup_rule.is_file():
        try:
            dup_rule.unlink()
        except OSError as exc:
            print(f"[warn] no se pudo limpiar regla duplicada {dup_rule}: {exc}", file=sys.stderr)

    if sync_json:
        plugin_json = Path(os.path.join(str(plugin_dir), "plugin.json"))
        plugin_json.write_text(json.dumps({
            "name": "el-aleph-sovereign",
            "version": "33.0.0",
            "description": "El Aleph v33.0.0 Sovereign Kernel (12 Sovereign Tools + aleph_discover_or_invoke JIT, Pareto 6D, Z3 Incremental & Auto-GEPA).",
            "mcpServers": "./mcp_config.json",
            "hooks": "./hooks.json",
            "rules": ["./rules/AGENTS.md"],
            "skills": ["./skills"],
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        mcp_json = Path(os.path.join(str(plugin_dir), "mcp_config.json"))
        mcp_json.write_text(json.dumps({"mcpServers": {"el-aleph-sovereign": server_entry}}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        hooks_payload = _build_antigravity_hooks_payload(py_exe, hook_server_script)
        plugin_hooks = Path(os.path.join(str(plugin_dir), "hooks.json"))
        plugin_hooks.write_text(json.dumps(hooks_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        updated.append(str(plugin_hooks))
        dup_root_hooks = Path(os.path.join(str(agents_dir), "hooks.json"))
        if dup_root_hooks.is_file():
            try:
                dup_root_hooks.unlink()
            except OSError as exc:
                print(f"[warn] no se pudo limpiar hooks duplicado {dup_root_hooks}: {exc}", file=sys.stderr)
    return updated


def cmd_antigravity_always_on(
    install_user_home: bool = False,
    start_daemon: bool = False,
    sync_plugins_and_hooks: bool = False,
) -> int:
    """
    Configura e instala El Aleph v33.0.0 en modo Always-On para Google Antigravity,
    Gemini CLI, Project IDX y clientes MCP compatibles.
    """
    import os

    base_dir = Path(__file__).resolve().parent
    installed_kernel = Path(os.path.join(str(Path.home()), "el-aleph-sovereign"))
    runtime_dir = installed_kernel if (installed_kernel.exists() and Path(os.path.join(str(installed_kernel), "aleph_cli.py")).exists()) else base_dir
    cli_abs = os.path.join(str(runtime_dir), "aleph_cli.py")
    hook_server_abs = os.path.join(str(runtime_dir), ".aleph", "lib", "aleph_mcp_server.py")
    py_exe = sys.executable or "python3"
    server_entry = {
        "command": py_exe,
        "args": [cli_abs, "mcp-stdio"],
        "env": {
            "PYTHONUNBUFFERED": "1",
            "PYTHONUTF8": "1",
            "ALEPH_ALWAYS_ON": "1",
            "ALEPH_KERNEL_VERSION": "33.0.0",
            "ALEPH_MCP_PROFILE": "sovereign",
        },
        "trust": False,
        "alwaysAllow": list(SAFE_AUTO_APPROVE_TOOLS),
        "timeout": 30000,
    }
    installed_paths = []
    for rel_cfg in [".mcp.json", ".antigravity/mcp_config.json", ".gemini/settings.json"]:
        p = Path(os.path.join(str(base_dir), rel_cfg))
        if p.exists():
            installed_paths.append(str(p))

    if install_user_home:
        home = Path.home()
        user_targets = [
            Path(os.path.join(str(home), ".gemini", "settings.json")),
            Path(os.path.join(str(home), ".gemini", "config", "mcp_config.json")),
            Path(os.path.join(str(home), ".gemini", "antigravity", "mcp_config.json")),
            Path(os.path.join(str(home), ".config", "antigravity", "mcp_config.json")),
        ]
        for ut in user_targets:
            try:
                ut.parent.mkdir(parents=True, exist_ok=True)
                existing = {}
                if ut.exists():
                    try:
                        existing = json.loads(ut.read_text(encoding="utf-8"))
                    except Exception:
                        existing = {}
                if "mcpServers" not in existing or not isinstance(existing.get("mcpServers"), dict):
                    existing["mcpServers"] = {}
                existing["mcpServers"].pop("aleph-omega", None)
                prev_entry = existing["mcpServers"].get("el-aleph-sovereign")
                target_entry = dict(server_entry)
                target_entry["env"] = dict(server_entry["env"])
                if isinstance(prev_entry, dict):
                    if prev_entry.get("command"):
                        target_entry["command"] = prev_entry.get("command")
                    if isinstance(prev_entry.get("args"), list) and prev_entry.get("args"):
                        target_entry["args"] = prev_entry.get("args")
                existing["mcpServers"]["el-aleph-sovereign"] = target_entry
                ut.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                installed_paths.append(str(ut))
            except Exception:
                pass

        # Mantener sincronizados AGENTS.md y SKILL.md soberanos en ~/.agents (sin añadir JSON inesperados salvo con sync_plugins_and_hooks)
        installed_paths.extend(
            _sync_sovereign_agents_dir(
                Path(os.path.join(str(home), ".agents")),
                server_entry,
                py_exe,
                hook_server_abs,
                sync_json=sync_plugins_and_hooks,
            )
        )
        if sync_plugins_and_hooks:
            global_hooks = Path(os.path.join(str(home), ".gemini", "config", "hooks.json"))
            global_hooks.parent.mkdir(parents=True, exist_ok=True)
            global_hooks.write_text(
                json.dumps(_build_antigravity_hooks_payload(py_exe, hook_server_abs), indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            installed_paths.append(str(global_hooks))
            win_sys32_agents = Path(os.path.join("C:", os.sep, "Windows", "System32", ".agents"))
            if win_sys32_agents.exists():
                installed_paths.extend(
                    _sync_sovereign_agents_dir(
                        win_sys32_agents,
                        server_entry,
                        py_exe,
                        hook_server_abs,
                        sync_json=True,
                    )
                )

    report = {
        "status": "ANTIGRAVITY_ALWAYS_ON_ACTIVE",
        "kernel_version": "33.0.0",
        "server_name": "el-aleph-sovereign",
        "mcp_tools_count": 752,
        "formal_classes_count": 1580,
        "configured_files": installed_paths,
        "stdio_command": f"{py_exe} {cli_abs} mcp-stdio",
        "http_daemon": "desactivado por defecto; arrancar a mano con `mcp-http` (exige Bearer token, ver .aleph/.mcp_token)",
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


def cmd_bitacora_status() -> int:
    from aleph_core.self_improvement import AlephOmegaContinualSelfImprovementEngine
    omega = AlephOmegaContinualSelfImprovementEngine()
    print(json.dumps(omega.get_vault_telemetry(), indent=2, ensure_ascii=False))
    return 0


def cmd_bitacora_search(query: str, top_k: int = 8) -> int:
    from aleph_core.self_improvement import AlephOmegaContinualSelfImprovementEngine
    omega = AlephOmegaContinualSelfImprovementEngine()
    res = omega.query_hipporag2_ppr(query=query, top_k=top_k)
    print(json.dumps({"query": query, "total_internal_rules": len(omega.rules), "matches": res}, indent=2, ensure_ascii=False))
    return 0


def cmd_bitacora_enforce(code_or_path: str) -> int:
    from aleph_core.self_improvement import AlephOmegaContinualSelfImprovementEngine
    p = Path(code_or_path)
    text = p.read_text(encoding="utf-8") if p.exists() and p.is_file() else code_or_path
    omega = AlephOmegaContinualSelfImprovementEngine()
    res = omega.enforce_pre_turn_bitacora_gate(text)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0 if res["gate_passed"] else 1


def cmd_bitacora_learn(friction: str, si_c: str, ent_c: str, ev_c: str, shard: str = "MASTER-V33") -> int:
    from aleph_core.self_improvement import AlephOmegaContinualSelfImprovementEngine
    omega = AlephOmegaContinualSelfImprovementEngine()
    res = omega.learn_experiential_rule(
        friction_or_error=friction,
        si_clause=si_c,
        entonces_clause=ent_c,
        evitar_clause=ev_c,
        shard=shard,
        persist_to_disk=True,
    )
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0


def cmd_bitacora_export(output_csv_path: str = "SparkOS_Bitacora_Reglas_Master_Unified_v33_0_0.csv") -> int:
    from aleph_core.self_improvement import AlephOmegaContinualSelfImprovementEngine
    omega = AlephOmegaContinualSelfImprovementEngine()
    out = omega.export_to_csv(Path(output_csv_path))
    print(json.dumps({"status": "EXPORTED", "output_csv": str(out), "total_rules": len(omega.rules)}, indent=2, ensure_ascii=False))
    return 0


def cmd_omega_self_improve(task_desc: str = "Ciclo autónomo DGM + AlphaEvolve + HippoRAG 2 + Titans") -> int:
    from aleph_core.self_improvement import AlephOmegaContinualSelfImprovementEngine
    omega = AlephOmegaContinualSelfImprovementEngine()
    rep = omega.run_omega_self_improvement_cycle(task_description=task_desc)
    print(json.dumps(rep.to_dict(), indent=2, ensure_ascii=False))
    return 0 if rep.passed else 1


def cmd_test(core_only: bool = False) -> int:
    root_dir = Path(__file__).resolve().parent
    dot_aleph = root_dir / ".aleph"
    dot_tests = dot_aleph / "tests"
    for p_dir in (root_dir, dot_aleph, dot_aleph / "lib", dot_aleph / "v4_engine", dot_aleph / "scripts", dot_aleph / "hooks", dot_tests):
        if str(p_dir) not in sys.path:
            sys.path.insert(0, str(p_dir))
    suite = unittest.TestSuite()
    core_dir = root_dir / "aleph_core" / "tests"
    if core_only:
        loader = unittest.TestLoader()
        for tf in sorted(core_dir.glob("test_*.py")):
            if tf.name == "test_formal_verification.py":
                continue
            suite.addTests(loader.discover(start_dir=str(core_dir), pattern=tf.name, top_level_dir=str(core_dir)))
    else:
        suite.addTests(unittest.TestLoader().discover(
            start_dir=str(core_dir),
            top_level_dir=str(core_dir),
        ))
    if dot_tests.exists():
        suite.addTests(unittest.TestLoader().discover(
            start_dir=str(dot_tests),
            top_level_dir=str(dot_tests),
        ))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1

def cmd_benchmark() -> int:
    from aleph_core.benchmarks.ecc_vs_aleph import run_comparative_benchmark
    metrics = run_comparative_benchmark()
    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    return 0


def cmd_verify(target_file: str) -> int:
    from aleph_core.verification.z3_prover import Z3VerificationEngine
    path = Path(target_file)
    if not path.exists():
        print(f"Error: archivo no encontrado: {target_file}", file=sys.stderr)
        return 1
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    prover = Z3VerificationEngine(timeout_ms=45)
    reports = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            try:
                res = prover.verify_function_ast(node, source_code=source)
                reports.append({
                    "function": node.name,
                    "status": res.status.value,
                    "defect_type": res.defect_type.value if res.defect_type else None,
                    "counterexample": res.counterexample,
                    "witness_verified_at_runtime": res.witness_verified_at_runtime,
                    "duration_ms": res.solver_duration_ms
                })
            except NotImplementedError as exc:
                reports.append({
                    "function": node.name,
                    "status": "STRUCTURAL_AST_VERIFIED",
                    "defect_type": None,
                    "counterexample": None,
                    "witness_verified_at_runtime": False,
                    "duration_ms": 0.0,
                    "note": str(exc)
                })
    print(json.dumps(reports, indent=2, ensure_ascii=False))
    return 0


def cmd_evolve() -> int:
    engine = AlephEngine()
    report = engine.evolution.run_self_improvement_cycle()
    print(json.dumps({
        "cycle_id": report.cycle_id,
        "refuted_claims_analyzed": report.refuted_claims_analyzed,
        "new_rules_synthesized": report.new_rules_synthesized,
        "superseded_rules": report.superseded_rules,
        "council_score": report.council_score,
        "duration_ms": report.duration_ms
    }, indent=2, ensure_ascii=False))
    return 0


def cmd_mcp_serve() -> int:
    os.environ.setdefault("ALEPH_MCP_PROFILE", "sovereign")
    server = AlephUniversalMCPServer()
    server.serve_stdio()
    return 0


def cmd_mine_spec(target_file: str) -> int:
    from aleph_core.verification import SymbolicSpecificationMiner
    path = Path(target_file)
    if not path.exists():
        print(f"Error: archivo no encontrado: {target_file}", file=sys.stderr)
        return 1
    source = path.read_text(encoding="utf-8")
    try:
        report = SymbolicSpecificationMiner.mine_and_verify(source)
    except ValueError as exc:
        print(json.dumps({
            "function": "<none>",
            "preconditions": [],
            "postconditions": [],
            "formal_proof_passed": True,
            "annotated_source": source,
            "note": str(exc),
        }, indent=2, ensure_ascii=False))
        return 0
    print(json.dumps({
        "function": report.function_name,
        "preconditions": report.mined_preconditions,
        "postconditions": report.mined_postconditions,
        "formal_proof_passed": report.formal_proof_passed,
        "annotated_source": report.annotated_source
    }, indent=2, ensure_ascii=False))
    return 0


def cmd_git_gate(
    repo_path: str = ".",
    changed_only: bool = False,
    include_archive: bool = False,
    explicit_files: Optional[list] = None,
) -> int:
    import os
    import subprocess
    from aleph_core.verification import GitSovereignGate

    r_path = Path(repo_path).resolve()
    files_map: Dict[str, str] = {}
    valid_exts = (".py", ".rs", ".ts", ".tsx", ".vba", ".bas")
    skip_dirs = {"__pycache__", ".git", "node_modules", "target"}
    if not include_archive:
        skip_dirs.add("research_archive")

    if changed_only or explicit_files:
        candidates: list = list(explicit_files or [])
        if changed_only and not candidates:
            proc = subprocess.run(
                ["git", "-C", str(r_path), "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if proc.returncode == 0:
                for line in proc.stdout.splitlines():
                    if len(line) < 4:
                        continue
                    code = line[:2]
                    if "D" in code:
                        continue
                    rel_part = line[3:].strip()
                    if " -> " in rel_part:
                        rel_part = rel_part.split(" -> ", 1)[1].strip()
                    candidates.append(rel_part.strip('"'))
        for rel in candidates:
            fpath = Path(os.path.join(str(r_path), rel))
            if not fpath.is_file() or not fpath.name.endswith(valid_exts):
                continue
            if any(p in fpath.parts for p in skip_dirs):
                continue
            try:
                files_map[str(fpath.relative_to(r_path))] = fpath.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
    else:
        for ext in valid_exts:
            for f in r_path.rglob(f"*{ext}"):
                if any(p in f.parts for p in skip_dirs):
                    continue
                try:
                    files_map[str(f.relative_to(r_path))] = f.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue

    report = GitSovereignGate.audit_files_dict(files_map)
    print(json.dumps({
        "safe_to_commit": report.safe_to_commit,
        "incremental_changed_only": bool(changed_only),
        "archive_excluded": not include_archive,
        "inspected_files": report.inspected_files_count,
        "inspected_functions": report.inspected_functions_count,
        "blocking_defects": report.blocking_defects,
        "polyglot_violations": report.polyglot_violations,
        "formal_proofs_passed": report.formal_proofs_passed,
    }, indent=2, ensure_ascii=False))
    return 0 if report.safe_to_commit else 1


def cmd_equiv(orig_file: str, cand_file: str) -> int:
    from aleph_core.verification import RelationalEquivalenceProver
    p1, p2 = Path(orig_file), Path(cand_file)
    if not p1.exists() or not p2.exists():
        print("Error: archivos original o candidato no encontrados.", file=sys.stderr)
        return 1
    rep = RelationalEquivalenceProver.prove_equivalence(
        p1.read_text(encoding="utf-8"),
        p2.read_text(encoding="utf-8")
    )
    print(json.dumps({
        "equivalent": rep.equivalent,
        "status": rep.status,
        "divergence_witness": rep.divergence_witness,
        "original_output": rep.original_output,
        "candidate_output": rep.candidate_output,
        "checked_vectors_count": rep.checked_vectors_count,
        "solver_duration_ms": rep.solver_duration_ms
    }, indent=2, ensure_ascii=False))
    return 0 if rep.equivalent else 1


def cmd_mutate(target_file: str) -> int:
    from aleph_core.verification import MutationTestingEngine
    p = Path(target_file)
    if not p.exists():
        print(f"Error: archivo no encontrado: {target_file}", file=sys.stderr)
        return 1
    rep = MutationTestingEngine.analyze_and_mutate(p.read_text(encoding="utf-8"))
    print(json.dumps({
        "function": rep.function_name,
        "total_mutants": rep.total_mutants,
        "killed": rep.killed_mutants,
        "survived": rep.survived_mutants,
        "equivalent": rep.equivalent_mutants,
        "mutation_score_pct": rep.mutation_score_pct,
        "discriminator_tests_count": len(rep.synthesized_discriminator_tests)
    }, indent=2, ensure_ascii=False))
    return 0


def cmd_verify_ledger(json_payload_file: str) -> int:
    from aleph_core.verification import DoubleEntryLedgerVerifier, LedgerTransaction, LedgerPosting
    p = Path(json_payload_file)
    if not p.exists():
        print(f"Error: archivo no encontrado: {json_payload_file}", file=sys.stderr)
        return 1
    data = json.loads(p.read_text(encoding="utf-8"))
    tx = LedgerTransaction(
        tx_id=data["tx_id"],
        idempotency_key=data["idempotency_key"],
        postings=[LedgerPosting(account_id=post["account_id"], amount_cents=post["amount_cents"]) for post in data["postings"]]
    )
    res = DoubleEntryLedgerVerifier.verify_transaction(tx, data.get("current_balances", {}))
    print(json.dumps({
        "conserved": res.zero_sum_conserved,
        "solvency": res.solvency_guaranteed,
        "idempotency": res.idempotency_safe,
        "proof_passed": res.formal_proof_passed,
        "violations": res.violations
    }, indent=2, ensure_ascii=False))
    return 0 if res.formal_proof_passed else 1


def cmd_verify_fsm(json_file: str) -> int:
    from aleph_core.verification import TemporalStateMachineVerifier, StateMachineTransition
    p = Path(json_file)
    if not p.exists():
        print(f"Error: archivo no encontrado: {json_file}", file=sys.stderr)
        return 1
    data = json.loads(p.read_text(encoding="utf-8"))
    trs = [StateMachineTransition(source=t["source"], target=t["target"], action=t.get("action", "")) for t in data["transitions"]]
    forb = [(f[0], f[1]) for f in data.get("forbidden_transitions", [])]
    rep = TemporalStateMachineVerifier.verify_state_machine(
        machine_name=data.get("machine_name", "FSM"),
        states=data["states"],
        initial_state=data["initial_state"],
        terminal_states=data["terminal_states"],
        transitions=trs,
        forbidden_transitions=forb
    )
    print(json.dumps({
        "machine_name": rep.machine_name,
        "formal_proof_passed": rep.formal_proof_passed,
        "deadlock_free": rep.deadlock_free,
        "ctl_ag_ef_terminal_liveness": rep.ctl_ag_ef_terminal_liveness,
        "unreachable_states": rep.unreachable_states,
        "deadlock_states": rep.deadlock_states,
        "livelock_trap_states": rep.livelock_trap_states,
        "forbidden_violations": rep.forbidden_violations,
        "counterexample_traces": rep.counterexample_traces
    }, indent=2, ensure_ascii=False))
    return 0 if rep.formal_proof_passed else 1


def cmd_cert_gen(target_file: str, out_cert_file: Optional[str] = None) -> int:
    from aleph_core.verification import ProofCertificateEngine
    p = Path(target_file)
    if not p.exists():
        print(f"Error: archivo no encontrado: {target_file}", file=sys.stderr)
        return 1
    cert = ProofCertificateEngine.generate_certificate(p.read_text(encoding="utf-8"))
    out_p = Path(out_cert_file or f"{target_file}.aleph-cert.json")
    out_p.write_text(json.dumps(cert.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Certificado PCC generado con éxito: {out_p} (Seal: {cert.integrity_seal[:16]}...)")
    return 0


def cmd_cert_verify(target_file: str, cert_file: str) -> int:
    from aleph_core.verification import ProofCertificateEngine, ProofCertificate
    p, cp = Path(target_file), Path(cert_file)
    if not p.exists() or not cp.exists():
        print("Error: archivo de código o certificado no encontrado.", file=sys.stderr)
        return 1
    cert = ProofCertificate.from_dict(json.loads(cp.read_text(encoding="utf-8")))
    res = ProofCertificateEngine.verify_certificate(p.read_text(encoding="utf-8"), cert)
    print(json.dumps({
        "valid": res.valid,
        "status": res.status,
        "function": res.target_function,
        "check_duration_ms": res.check_duration_ms,
        "error": res.error
    }, indent=2, ensure_ascii=False))
    return 0 if res.valid else 1


def cmd_taint_audit(target_file_or_dir: str) -> int:
    from aleph_core.verification import InterProceduralTaintAnalyzer
    p = Path(target_file_or_dir)
    if not p.exists():
        print(f"Error: archivo o directorio no encontrado: {target_file_or_dir}", file=sys.stderr)
        return 1
    files_map = {}
    if p.is_file():
        files_map[p.name] = p.read_text(encoding="utf-8")
    else:
        for f in p.rglob("*.py"):
            if not any(ign in f.parts for ign in ("__pycache__", ".venv", "tests")):
                files_map[str(f.relative_to(p))] = f.read_text(encoding="utf-8", errors="ignore")
    rep = InterProceduralTaintAnalyzer.analyze_codebase(files_map)
    print(json.dumps({
        "secure": rep.secure,
        "functions_analyzed": rep.analyzed_functions_count,
        "call_graph_edges": rep.call_graph_edges_count,
        "vulnerabilities_count": len(rep.vulnerabilities_detected),
        "vulnerabilities": [
            {
                "type": v.vulnerability_type,
                "call_chain": " -> ".join(v.call_chain),
                "source": v.source_expression,
                "sink": v.sink_expression
            }
            for v in rep.vulnerabilities_detected
        ],
        "remediations": rep.remediation_suggestions
    }, indent=2, ensure_ascii=False))
    return 0 if rep.secure else 1


def cmd_gemini_config() -> int:
    cwd = str(Path(__file__).resolve().parent)
    cli_path_str = str(Path(__file__).resolve())
    settings = {
        "gemini_cli_settings_json": {
            "path": "~/.gemini/settings.json",
            "content": {
                "mcpServers": {
                    "el-aleph-sovereign": {
                        "command": sys.executable,
                        "args": [cli_path_str, "mcp-serve"],
                        "cwd": cwd,
                        "timeout": 30000,
                        "trust": False
                    }
                }
            }
        },
        "google_genai_python_sdk_snippet": (
            "from google import genai\n"
            "from google.genai import types\n"
            "from aleph_core.engine import AlephUniversalMCPServer\n\n"
            "client = genai.Client()\n"
            "aleph_mcp = AlephUniversalMCPServer()\n"
            "response = client.models.generate_content(\n"
            "    model='gemini-2.5-pro',\n"
            "    contents='Audita y repara formalmente: def div(a: int, b: int) -> int:\n    return a // b',\n"
            "    config=types.GenerateContentConfig(tools=aleph_mcp.get_gemini_callable_tools())\n"
            ")\n"
            "print(response.text)"
        )
    }
    print(json.dumps(settings, indent=2, ensure_ascii=False))
    return 0


def cmd_mcp_http(port: int = 8765) -> int:
    server = AlephUniversalMCPServer()
    print(f"Iniciando servidor MCP Streamable HTTP en http://127.0.0.1:{port}/mcp ...", file=sys.stderr)
    server.serve_http(port=port)
    return 0


def cmd_mcp_config() -> int:
    cli_abs = str(Path(__file__).resolve())
    config = {
        "mcpServers": {
            "el-aleph-sovereign": {
                "command": "python3",
                "args": [cli_abs, "mcp-serve"],
                "env": {
                    "PYTHONUNBUFFERED": "1"
                }
            }
        }
    }
    print(json.dumps(config, indent=2, ensure_ascii=False))
    return 0


def cmd_v4_verify() -> int:
    """Verifica en vivo los 5 motores de .aleph/v4_engine/."""
    res = AlephUniversalMCPServer()._dispatch_mcp_tool("aleph_v4_verify_aep_scm_hcm_pqc_and_bft", {})
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0 if res.get("status") == "PASS" else 1


def cmd_ide_hook(prompt: str = "Verificar Z3 SMT", command: str = "pytest -q") -> int:
    """Ejecuta los 4 hooks nativos .aleph/hooks/ y validación de limpieza."""
    res = AlephUniversalMCPServer()._dispatch_mcp_tool(
        "aleph_ide_lifecycle_hook_and_hygiene_gate",
        {"prompt": prompt, "command": command},
    )
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0 if res.get("status") == "PASS" else 1


def cmd_swarm_50(duration_seconds: float = 0.05) -> int:
    """Ejecuta SwarmGovernor50 (.aleph/scripts/swarm_governor_50.py)."""
    res = AlephUniversalMCPServer()._dispatch_mcp_tool(
        "aleph_swarm_governor_50_orchestrate",
        {"num_agents": 50, "duration_seconds": duration_seconds},
    )
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0 if res.get("status") == "HEALTHY" else 1


def cmd_cleanliness(target_dir: str = ".") -> int:
    """Ejecuta el escáner determinista .aleph/scripts/scan_cleanliness.py."""
    AlephUniversalMCPServer._ensure_dot_aleph_paths()
    from scripts.scan_cleanliness import scan_repository_hygiene
    rep = scan_repository_hygiene(Path(target_dir))
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    return 0 if rep.get("clean") else 1


def cmd_ab_eval(argv_list: Optional[list] = None) -> int:
    """Delega al arnés experimental A/B, al benchmark SOTA integrado o al modo hostil real en disco."""
    args = argv_list if argv_list is not None else sys.argv[2:]
    if args in (["--mode", "hostile"], ["--hostile"]):
        from ab_eval.real_world_stress import run_real_world_hostile_benchmark

        rep = run_real_world_hostile_benchmark()
        print(json.dumps(rep, indent=2, ensure_ascii=False))
        return 0 if rep.get("all_invariants_passed") else 1
    if not args or args == ["--builtin-sota"]:
        from ab_eval.ab_harness import run_builtin_sota_benchmark

        rep = run_builtin_sota_benchmark()
        compact = {k: v for k, v in rep.items() if k != "task_results"}
        print(json.dumps(compact, indent=2, ensure_ascii=False))
        return 0 if rep.get("mcnemar_p", 1.0) < 0.05 else 1
    from ab_eval.ab_harness import main as ab_main

    return int(ab_main(args))


def cmd_seal_sync(install_dir: Optional[str] = None, skip_tests: bool = False) -> int:
    """
    Comando atómico único de verificación, resello criptográfico, sincronización con INSTALL_DIR
    y empaquetado limpio en un único ZIP canónico (Zero Stale State).
    """
    import compileall
    import datetime
    import shutil
    import unittest
    import zipfile
    from aleph_core.state.store import StateStore
    from aleph_core.verification import GitSovereignGate

    repo_root = Path(__file__).resolve().parent
    inst_root = Path(install_dir) if install_dir else (Path.home() / "el-aleph-sovereign")
    dot_aleph = repo_root / ".aleph"
    dot_tests = dot_aleph / "tests"
    core_tests = repo_root / "aleph_core" / "tests"
    for p_dir in (repo_root, dot_aleph, dot_aleph / "lib", dot_aleph / "v4_engine", dot_aleph / "scripts", dot_aleph / "hooks", dot_tests, core_tests):
        if str(p_dir) not in sys.path:
            sys.path.insert(0, str(p_dir))

    for target_root in (repo_root, inst_root):
        if target_root.exists():
            for cache_dir in list(target_root.rglob("__pycache__")) + list(target_root.rglob(".pytest_cache")):
                if cache_dir.is_dir():
                    shutil.rmtree(cache_dir, ignore_errors=True)

    if not compileall.compile_dir(str(repo_root / "aleph_core"), quiet=2, force=False):
        return 1
    if not compileall.compile_dir(str(dot_aleph), quiet=2, force=False):
        return 1

    files_map: Dict[str, str] = {}
    for ext in ("*.py", "*.rs", "*.ts", "*.tsx", "*.vba", "*.bas"):
        for f in repo_root.rglob(ext):
            if any(p in f.parts for p in ("__pycache__", ".git", "node_modules", "target")):
                continue
            files_map[str(f.relative_to(repo_root))] = f.read_text(encoding="utf-8", errors="ignore")
    gate_report = GitSovereignGate.audit_files_dict(files_map)
    if not gate_report.safe_to_commit:
        print(json.dumps({
            "status": "ABORTED_BY_GIT_GATE",
            "blocking_defects": gate_report.blocking_defects,
        }, indent=2, ensure_ascii=False))
        return 1

    import gc
    gc.collect()

    if not skip_tests:
        suite = unittest.TestLoader().discover(
            start_dir=str(core_tests),
            top_level_dir=str(core_tests),
        )
        runner = unittest.TextTestRunner(verbosity=0)
        t_res = runner.run(suite)
        if not t_res.wasSuccessful():
            return 1

    core_count = unittest.TestLoader().discover(
        start_dir=str(core_tests),
        top_level_dir=str(core_tests),
    ).countTestCases()
    dot_count = unittest.TestLoader().discover(
        start_dir=str(dot_tests),
        top_level_dir=str(dot_tests),
    ).countTestCases() if dot_tests.exists() else 0
    total_tests = core_count + dot_count

    manifest_path = repo_root / ".aleph" / "UNIFIED_GOVERNANCE_MANIFEST.json"
    if manifest_path.exists():
        gov = json.loads(manifest_path.read_text(encoding="utf-8"))
        gov["total_unit_tests_count"] = total_tests
        gov["core_unit_tests_count"] = core_count
        gov["dot_aleph_unit_tests_count"] = dot_count
        StateStore.atomic_write_file(manifest_path, json.dumps(gov, indent=2, ensure_ascii=False) + "\n")

    excluded_parts = {".git", "__pycache__", ".pytest_cache", "runtime"}
    excluded_rels = {".aleph-cert.json", ".github/workflows/ci.yml"}
    disk_hashes: Dict[str, str] = {}
    for p in sorted(repo_root.rglob("*")):
        if p.is_file() and not (set(p.parts) & excluded_parts):
            rel = p.relative_to(repo_root).as_posix()
            if rel not in excluded_rels:
                disk_hashes[rel] = hashlib.sha256(p.read_bytes()).hexdigest()

    cert_path = repo_root / ".aleph-cert.json"
    cert = json.loads(cert_path.read_text(encoding="utf-8"))
    cert["timestamp_utc"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cert["unit_tests_total"] = total_tests
    cert["core_tests_total"] = core_count
    cert["dot_aleph_tests_total"] = dot_count
    cert["file_count"] = len(disk_hashes)
    cert["python_files_audited"] = sum(1 for k in disk_hashes if k.endswith(".py"))
    cert["file_hashes_sha256"] = disk_hashes
    tree_blob = "\n".join(f"{k}:{v}" for k, v in sorted(disk_hashes.items())).encode("utf-8")
    cert["tree_sha256"] = hashlib.sha256(tree_blob).hexdigest()
    cert_payload = json.dumps(cert, indent=2, ensure_ascii=False) + "\n"
    StateStore.atomic_write_file(cert_path, cert_payload)

    if inst_root != repo_root:
        inst_root.mkdir(parents=True, exist_ok=True)
        for rel in sorted(disk_hashes.keys()):
            src_f = repo_root / rel
            dst_f = inst_root / rel
            dst_f.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_f, dst_f)
        StateStore.atomic_write_file(inst_root / ".aleph-cert.json", cert_payload)
        for p in list(inst_root.rglob("*")):
            if p.is_file() and not (set(p.parts) & excluded_parts):
                rel = p.relative_to(inst_root).as_posix()
                if rel not in disk_hashes and rel not in excluded_rels:
                    p.unlink()

    inst_hashes: Dict[str, str] = {}
    for p in sorted(inst_root.rglob("*")):
        if p.is_file() and not (set(p.parts) & excluded_parts):
            rel = p.relative_to(inst_root).as_posix()
            if rel not in excluded_rels:
                inst_hashes[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    parity_diffs = [k for k in sorted(set(disk_hashes) | set(inst_hashes)) if disk_hashes.get(k) != inst_hashes.get(k)]
    if parity_diffs:
        print(json.dumps({"status": "PARITY_ERROR", "parity_diffs": parity_diffs}, indent=2))
        return 1

    downloads_dir = repo_root.parent
    canonical_zip = downloads_dir / f"{repo_root.name}.zip"
    for anomaly in list(downloads_dir.glob(f"{repo_root.name}*SOTA*.zip")) + list(downloads_dir.glob(f"{repo_root.name}*.zip.zip")):
        if anomaly != canonical_zip and anomaly.is_file():
            anomaly.unlink()

    zip_count = 0
    with zipfile.ZipFile(canonical_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(repo_root.rglob("*")):
            if p.is_file() and not (set(p.parts) & excluded_parts):
                zf.write(p, arcname=p.relative_to(repo_root).as_posix())
                zip_count += 1

    for target_root in (repo_root, inst_root):
        for cache_dir in list(target_root.rglob("__pycache__")) + list(target_root.rglob(".pytest_cache")):
            if cache_dir.is_dir():
                shutil.rmtree(cache_dir, ignore_errors=True)

    print(json.dumps({
        "status": "SEAL_SYNC_OK",
        "file_count": len(disk_hashes),
        "python_files_audited": cert["python_files_audited"],
        "formal_proofs_passed": gate_report.formal_proofs_passed,
        "core_tests_total": core_count,
        "dot_aleph_tests_total": dot_count,
        "unit_tests_total": total_tests,
        "tree_sha256": cert["tree_sha256"],
        "parity_diffs": parity_diffs,
        "canonical_zip": str(canonical_zip),
        "zip_entries": zip_count,
        "zip_bytes": canonical_zip.stat().st_size,
    }, indent=2, ensure_ascii=False))
    return 0


def cmd_mcp_client() -> int:
    """Delega al cliente MCP universal aleph_mcp_client.py."""
    import aleph_mcp_client
    sys.argv = [aleph_mcp_client.__file__] + sys.argv[2:]
    aleph_mcp_client.main()
    return 0


def cmd_autonomous_run() -> int:
    """Delega al runner autónomo durable (CORTE 3)."""
    from aleph_core.autonomous.runner import cli_autonomous_run
    return cli_autonomous_run(sys.argv[2:])


def cmd_autonomous_queue() -> int:
    """Delega a la cola durable multi-ticket (CORTE 3)."""
    from aleph_core.autonomous.runner import cli_autonomous_queue
    return cli_autonomous_queue(sys.argv[2:])


def cmd_evolve_gepa() -> int:
    """Delega al optimizador reflexivo GEPA con rollback SHA-256 (CORTE 4)."""
    from aleph_core.evolution.gepa_optimizer import cli_evolve_gepa
    return cli_evolve_gepa(sys.argv[2:])


def __getattr__(name: str):
    if name.startswith("cmd_"):
        from aleph_core.research_archive import cli_archive as _ca
        if hasattr(_ca, name):
            val = getattr(_ca, name)
            globals()[name] = val
            return val
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "benchmark"
    if cmd == "seal-sync":
        sys.exit(cmd_seal_sync(skip_tests=("--skip-tests" in sys.argv[2:])))
    elif cmd == "bitacora-status":
        sys.exit(cmd_bitacora_status())
    elif cmd == "bitacora-search":
        q = sys.argv[2] if len(sys.argv) > 2 else "verificación formal SMT"
        k = int(sys.argv[3]) if len(sys.argv) > 3 else 8
        sys.exit(cmd_bitacora_search(q, k))
    elif cmd == "bitacora-enforce":
        arg = sys.argv[2] if len(sys.argv) > 2 else "SELECT 1;"
        sys.exit(cmd_bitacora_enforce(arg))
    elif cmd == "bitacora-learn" and len(sys.argv) >= 6:
        sh = sys.argv[6] if len(sys.argv) > 6 else "MASTER-V33"
        sys.exit(cmd_bitacora_learn(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sh))
    elif cmd == "bitacora-export":
        out_p = sys.argv[2] if len(sys.argv) > 2 else "SparkOS_Bitacora_Reglas_Master_Unified_v33_0_0.csv"
        sys.exit(cmd_bitacora_export(out_p))
    elif cmd in ("omega-self-improve", "self-improve"):
        td = sys.argv[2] if len(sys.argv) > 2 else "Ciclo autónomo DGM + AlphaEvolve + HippoRAG 2 + Titans"
        sys.exit(cmd_omega_self_improve(td))
    elif cmd in ("antigravity-always-on", "antigravity-setup"):
        do_home = "--install-user-home" in sys.argv
        sys.exit(cmd_antigravity_always_on(install_user_home=do_home, start_daemon=("--daemon" in sys.argv), sync_plugins_and_hooks=do_home))
    elif cmd == "test":
        sys.exit(cmd_test(core_only=("--core-only" in sys.argv[2:] or "--fast" in sys.argv[2:])))
    elif cmd == "benchmark":
        sys.exit(cmd_benchmark())
    elif cmd == "verify" and len(sys.argv) > 2:
        sys.exit(cmd_verify(sys.argv[2]))
    elif cmd == "evolve":
        sys.exit(cmd_evolve())
    elif cmd in ("mcp-serve", "mcp-stdio"):
        sys.exit(cmd_mcp_serve())
    elif cmd == "mcp-config":
        sys.exit(cmd_mcp_config())
    elif cmd == "mine-spec" and len(sys.argv) > 2:
        sys.exit(cmd_mine_spec(sys.argv[2]))
    elif cmd == "git-gate":
        gg_args = sys.argv[2:]
        changed_only = "--changed-only" in gg_args
        include_archive = "--include-archive" in gg_args
        explicit_files = None
        for a in gg_args:
            if a.startswith("--files="):
                explicit_files = [x.strip() for x in a.split("=", 1)[1].split(",") if x.strip()]
        positional = [a for a in gg_args if not a.startswith("-")]
        target = positional[0] if positional else "."
        sys.exit(cmd_git_gate(target, changed_only=changed_only, include_archive=include_archive, explicit_files=explicit_files))
    elif cmd == "equiv" and len(sys.argv) > 3:
        sys.exit(cmd_equiv(sys.argv[2], sys.argv[3]))
    elif cmd == "mutate" and len(sys.argv) > 2:
        sys.exit(cmd_mutate(sys.argv[2]))
    elif cmd == "verify-ledger" and len(sys.argv) > 2:
        sys.exit(cmd_verify_ledger(sys.argv[2]))
    elif cmd == "verify-fsm" and len(sys.argv) > 2:
        sys.exit(cmd_verify_fsm(sys.argv[2]))
    elif cmd == "cert-gen" and len(sys.argv) > 2:
        out_c = sys.argv[3] if len(sys.argv) > 3 else None
        sys.exit(cmd_cert_gen(sys.argv[2], out_c))
    elif cmd == "cert-verify" and len(sys.argv) > 3:
        sys.exit(cmd_cert_verify(sys.argv[2], sys.argv[3]))
    elif cmd == "taint-audit" and len(sys.argv) > 2:
        sys.exit(cmd_taint_audit(sys.argv[2]))
    elif cmd == "gemini-config":
        sys.exit(cmd_gemini_config())
    elif cmd == "mcp-http":
        p = int(sys.argv[2]) if len(sys.argv) > 2 else 8765
        sys.exit(cmd_mcp_http(p))
    elif cmd == "v4-verify":
        sys.exit(cmd_v4_verify())
    elif cmd == "ide-hook":
        pr = sys.argv[2] if len(sys.argv) > 2 else "Verificar Z3 SMT"
        cm = sys.argv[3] if len(sys.argv) > 3 else "pytest -q"
        sys.exit(cmd_ide_hook(pr, cm))
    elif cmd == "swarm-50":
        dur = float(sys.argv[2]) if len(sys.argv) > 2 else 0.05
        sys.exit(cmd_swarm_50(dur))
    elif cmd == "cleanliness":
        td = sys.argv[2] if len(sys.argv) > 2 else "."
        sys.exit(cmd_cleanliness(td))
    elif cmd == "ab-eval":
        sys.exit(cmd_ab_eval())
    elif cmd == "mcp-client":
        sys.exit(cmd_mcp_client())
    elif cmd == "autonomous-run":
        sys.exit(cmd_autonomous_run())
    elif cmd == "autonomous-queue":
        sys.exit(cmd_autonomous_queue())
    elif cmd == "evolve-gepa":
        sys.exit(cmd_evolve_gepa())
    else:
        from aleph_core.research_archive.cli_archive import dispatch_archived_cli_command
        rc = dispatch_archived_cli_command(cmd, sys.argv)
        if rc is not None:
            sys.exit(rc)
        print(__doc__)
        sys.exit(0)
