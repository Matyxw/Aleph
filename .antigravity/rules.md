# El Aleph v33.0.0 Sovereign Master Kernel — Google Antigravity Always-On Rules

## 1. Mandato Operativo Permanente (Always-On)
Este workspace está gobernado en tiempo real por **El Aleph v33.0.0 Sovereign Master Kernel** (Unificación Total de los 6 Nodos Federados `NODE-01`..`NODE-06` + Bóveda Activa `.aleph` World Designer V7).
- **Servidor MCP Activo**: `el-aleph-sovereign` (`python3 aleph_cli.py mcp-stdio` y Daemon HTTP Streamable en `http://127.0.0.1:8765/mcp`).
- **752 herramientas MCP (JSON-RPC 2.0)** con descubrimiento progresivo BM25 (`tools/search` y `profile="compact"` / `profile="core"`). Solo las 9 verificadas como solo-lectura se auto-aprueban (`SAFE_AUTO_APPROVE_TOOLS` en `aleph_cli.py`); el resto (p. ej. `aleph_apply_semantic_patch`, `aleph_bitacora_learn_experiential_rule`, `aleph_omega_dgm_alphaevolve_self_improve`) pide confirmación humana. `trust: false`.
- **1,580 clases `*Prover`/`*Report` en `z3_prover.py` (758/758 `*Prover` conectadas a descarga SMT `z3.Solver()`/`z3.unsat`)** + núcleo SMT (`Z3VerificationEngine` y `ast_smt.py` con soporte bitwise, potencias y `prove_formula_unsat`). **1,390 tests pasan** (9 omitidos opcionales de navegador vivo) y benchmark A/B de 25 tareas verificadas con test exacto de McNemar (`p = 5.96e-08`).

## 2. Compuertas Obligatorias por Dominio en Google Antigravity
1. **Antes de escribir o parchear código Python/Rust/TS/SQL (`NODE-01` & `NODE-06`)**:
   - Invocar `aleph_verify_and_repair` (código Python; es el único lenguaje con análisis AST real) o `aleph_apply_semantic_patch` (modifica archivos: confirmar) para verificar ausencia de `ZeroDivision`, `BoundsError`, `NonTermination` y preservación de equivalencia relacional.
2. **Antes de entregar interfaces UI/UX, CSS o componentes Web (`NODE-02` & `.aleph`)**:
   - Invocar `aleph_prove_dot_aleph_sovereign_world_designer_and_governance_gate`, `aleph_audit_and_repair_design_tokens_wcag` y las compuertas W3C CSS Level 4/5 & WCAG 2.2 AA (`content-visibility`, `subgrid`, `@scope`, OKLCH APCA/WCAG, resortes ODE `linear()`).
3. **Antes de ejecutar migraciones SQL, políticas RLS o esquemas Supabase/PostgreSQL 18 (`NODE-03`)**:
   - Invocar `aleph_verify_zero_downtime_ddl` y `aleph_verify_deep_supabase_rls`.
4. **Antes de exponer endpoints, autenticación, criptografía o agentes (`NODE-04`)**:
   - Invocar `aleph_analyze_interprocedural_taint`, `aleph_prove_spark6066_flink_cve2020_17518_airflow_cve2020_11978_and_cursor_cve2026_26268_rce` y compuertas PQC/OAuth/SSRF.
5. **Para navegación de repositorio a gran escala, compresión KV y verificación Lean/Verus/Dafny (`NODE-05`)**:
   - Invocar `aleph_build_pagerank_repomap` y los motores полиglot de PageRank y KV-Cache.
