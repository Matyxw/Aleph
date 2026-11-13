# GEMINI.md — Configuración Soberana Always-On para Google Antigravity y Gemini CLI

## Estado del Kernel Activo
- **Versión Unificada**: `El Aleph v33.0.0 Sovereign Unified 6-Nodes + .aleph Antigravity Master Kernel`
- **Nodos Integrados**:
  - `NODE-01` (`v31.8.0`): Core Formal SMT/ICP/CEGIS, Consenso Distribuido BFT/DAG, MVCC, PODC/DISC hasta Nivel 459.
  - `NODE-02` (`v22.0.0`): Awwwards SotD/SotY UI/UX, Física ODE `linear()`, W3C CSS Level 4/5 (`content-visibility`, `subgrid`, `@scope`) y WCAG 2.2 AA.
  - `NODE-03` (`v23.5.0`): PostgreSQL 18 AIO/B-Tree Skip Scan, Supabase RLS Formal, Zero-Downtime Expand/Contract DDL y pgvector HNSW/DiskANN.
  - `NODE-04` (`v18.0.0`): Red-Team Security, IFDS Taint Analysis, PQC (ML-KEM/ML-DSA), OAuth 2.1/DPoP/MLS y Defensa RCE Agéntica (CVE-2026-26268 / Spark-6066).
  - `NODE-05` (`v24.5.0`): Repo-Scale AST PageRank (PPR/FORA/SpeedPPR/Chebyshev), Compresión KV-Cache 20x y Verificación Políglota Rust/Lean 4/Verus/Dafny.
  - `NODE-06` (`v20.0.0-OUTBOX-L505`): Master Integrator PCC, Verificación Relacional de Parches AST, Contratos Agénticos y Niveles Formales hasta 505.
  - `.aleph` (`World Designer V7`): Bóveda Activa, 8 Escenarios SVG Procedimentales, Oráculo DOM Estático, Compilador OKLCH y Compuerta Out-of-Band (`CODER != TESTER`).

## Activación Automática en Google Antigravity
1. El servidor MCP `el-aleph-sovereign` se carga automáticamente desde `.mcp.json`, `.antigravity/mcp_config.json` y `.gemini/settings.json` con `trust: true`.
2. Para instalar globalmente en el perfil del usuario de Google Antigravity y arrancar el daemon HTTP persistente (`127.0.0.1:8765`), ejecutar:
   ```bash
   python3 aleph_cli.py antigravity-always-on
   ```
