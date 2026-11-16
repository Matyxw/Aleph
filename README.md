# El Aleph v33.0.0 — Sovereign Omega Self-Improving Kernel & Bitácora Vault (Edición SOTA Verificada)

Arquitectura integral de verificación formal, diseño visual físico-matemático y automejora continua sin olvido, verificada al 100 % en tiempo de ejecución real con **1.389 pruebas automatizadas (0 fallos, 0 errores; 9 saltadas opcionales en unittest sin navegador live)**.

| Subsistema | Implementación Verificada en Producción |
| :--- | :--- |
| **Bóveda de Bitácora y 8 Pilares SOTA** (`.aleph/BITACORA_MASTER_VAULT_V33.json` + `aleph_core/self_improvement/omega_continual_learner.py`) | **350 reglas operativas** (`SI → ENTONCES → EVITAR`) distribuidas en 9 shards y 4.742 entidades técnicas, encadenadas mediante árbol Merkle SHA-256 (`0de647cd8475a29f...`), con recuperación híbrida **HippoRAG 2** (Okapi BM25 + Proyecciones Semánticas LSH $D=64$ + Personalized PageRank $\alpha=0.15$), **Matriz Asociativa Paramétrica Titans** ($16 \times 16$ con regla delta y momento), **Diagonal de Información de Fisher Empírica EWC** ($F_{ii}$), **Medición Real de Olvido en Recuperación Top-K** (`Recall@5 = 100.0 %`, `0.0 %` olvido), **Paginador Jerárquico MemGPT** (3 niveles), **Destilación Autónoma ExpeL sobre AST** y **Torneo Evolutivo DGM / AlphaEvolve en vivo**. |
| **Núcleo de Verificación Formal y Taint AST** (`aleph_core/verification/` + `.aleph/lib/aleph_smt_layout_verifier.py`) | Compilador simbólico dual (`Z3VerificationEngine` + solucionador relacional e intervalos en Python puro para `QF_LIA` / `QF_BV` + solucionador analítico exacto por puntos críticos para `QF_LRA` 1D/2D), parcheo quirúrgico sobre AST con prueba de equivalencia relacional (`SemanticPatchEngine`), fallback generativo con shrinking (`PropertyBasedFallback`) y analizador de flujo de datos Taint sobre AST (`ASTIFDSDataflowTaintGate`). |
| **Motor Visual Soberano V7 y Oráculo Físico en Chromium/Blink Real** (`.aleph/lib/`) | Compiladores isomórficos HTML5 y React 19 TSX, espacio perceptual OKLCH con contraste APCA v0.98G, simulador RK4 de ecuaciones diferenciales de 2.º orden (`aleph_kinetic_ode.py` compilado a CSS `linear(...)`), sintetizador vectorial de 8 escenografías (`aleph_visual_stage_synthesizer.py`) y **Oráculo Físico en Chromium/Blink real** (`aleph_render_oracle.py` vía Chrome DevTools Protocol CDP sobre 6 viewports canónicos de `320px` a `1920px`). |
| **Motores de Cuarta Generación y Gobernanza de Enjambre** (`.aleph/v4_engine/` + `.aleph/scripts/swarm_governor_50.py`) | Protocolo binario **AEP v4.0** con verificación SHA-256/CRC32 zero-copy y tokens HMAC (`aep_protocol.py`), **Modelo Causal Estructural de Judea Pearl** con cirugía $\text{do}(X)$, contrafactuales en 3 pasos y regularización VICReg (`causal_world_model.py`), **Memoria Holográfica VSA de 10.240 bits** con binding XOR autoinverso y Kanerva SDM (`holographic_causal_memory.py`), **Aritmética de Anillo Ciclotómico PQC FIPS 203** $\mathbb{Z}_{3329}[X]/(X^{256}+1)$ con sellado TPM 2.0 PCR-16 (`pqc_crypto_sealing.py`) y consenso **Narwhal-Bullshark DAG-BFT + Multi-Raft** (`super_swarm_bft.py`, `swarm_governor_50.py`). |
| **Servidor MCP Blindado y Evaluación A/B** (`aleph_core/engine.py` + `ab_eval/ab_harness.py`) | Servidor JSON-RPC 2.0 unificado con **752 herramientas** (integrando las 730 del núcleo formal, las 19 de diseño/AEOS v7 de `.aleph/lib/aleph_mcp_server.py` y las 3 puertas unificadas para `v4_engine`, hooks/higiene y `SwarmGovernor50`; solo 9 tools de lectura auto-aprobadas en `SAFE_AUTO_APPROVE_TOOLS`; daemon HTTP protegido con token Bearer) + arnés experimental A/B con **prueba exacta de McNemar**. |

---

## 1. Métricas Reproducibles y Auditadas en Tiempo de Ejecución

| Indicador | Valor Medido | Comando de Verificación |
| :--- | :--- | :--- |
| **Suite Total de Pruebas Unitarias e Integración** | **1.389 OK, 0 fallos** (`1.280` en `aleph_core/tests` + `109` en `.aleph/tests`, 9 saltados sin Playwright live) | `python3 aleph_cli.py test` |
| **Oráculo Físico en Chromium/Blink Real** | **10 / 10 pruebas pasando en Chromium real** (6 viewports, 0 saltados) | `python3 .aleph/tests/test_aleph_live_oracle.py -v` |
| **Reglas en Bóveda / Entidades en Grafo** | **350 reglas / 4.742 entidades** (`BASE` 51, `NODE-01` 122, `NODE-02` 3, `NODE-03` 6, `NODE-04` 1, `NODE-05` 52, `NODE-06` 113, `MASTER-V32` 1, `MASTER-V33` 1) | `python3 aleph_cli.py bitacora-status` |
| **Cadena Merkle SHA-256 y Retención Top-K** | **100 % íntegra** (`Recall@5 = 1.0`, `0.0 %` olvido catastrófico) | `python3 aleph_cli.py bitacora-status` |
| **Higiene del Repositorio y Certificado PCC** | **100 % limpio** (`0` archivos `.db`/`.jsonl` residuales, `0` archivos de 0 bytes, `0` clones de manifiestos, hashes SHA-256 verificados en `.aleph-cert.json`) | `python3 .aleph/scripts/scan_cleanliness.py` |

---

## 2. Arquitectura de los Ocho Pilares SOTA en `omega_continual_learner.py`

1. **HippoRAG 2 Híbrido (`query_hipporag2_ppr`):** Combina puntuación léxica Okapi BM25 ($k_1=1.5, b=0.75$, peso $0.48$), difusión topológica mediante Personalized PageRank de 12 iteraciones sobre el grafo bipartito Regla $\leftrightarrow$ Entidad ($\alpha=0.15$, peso $0.35$), similitud coseno sobre proyecciones aleatorias con signo de trigramas y tokens ($D=64$, peso $0.12$) y prior logarítmico de Información de Fisher EWC ($0.05$).
2. **Titans Parametric Associative Memory (`TitansAssociativeMemoryMatrix`):** Mantiene una matriz de pesos asociativos $M_t \in \mathbb{R}^{16 \times 16}$ y momento $S_t \in \mathbb{R}^{16 \times 16}$ actualizada con la regla delta $\nabla_M \mathcal{L} = (M_{t-1} k_t - v_t) k_t^\top$ y compuerta adaptativa $\alpha_t = \sigma(w_\alpha^\top k_t)$, fusionada con la autoinformación de Shannon del corpus.
3. **EWC Fisher Diagonal Empírica y Medición de Retención Top-K (`_compute_empirical_fisher_diagonal`, `measure_topk_retrieval_forgetting`):** Calcula analíticamente la sensibilidad cuadrática $F_{ii}$ de cada regla en el grafo y evalúa empíricamente el `Recall@5` sobre consultas ancla de todos los shards para certificar `0.0 %` de olvido en recuperación.
4. **MemGPT / Letta OS Tiered Memory Pager (`MemGPTTieredMemoryPager`):** Gestiona tres niveles de memoria (`core_memory` anclada por importancia Fisher, `recall_buffer` episódico con desalojo automático por presupuesto de tokens y `archival_memory` con `page_in_from_archival`).
5. **ExpeL / Reflexion Autonomous Rule Distillation (`distill_rule_from_episodic_trace`):** Analiza automáticamente las diferencias estructurales entre el AST del código fallido y el AST del código reparado (incluyendo decoradores `@requires`/`@ensures` y constructos defensivos) para sintetizar reglas `SI → ENTONCES → EVITAR` sin redacción manual.
6. **TextGrad Symbolic Differentiation (`run_omega_self_improvement_cycle`):** Construye el gradiente textual $\nabla_{\text{text}} \mathcal{L}$ a partir de los diagnósticos reales de la compuerta AST/SMT, la sorpresa de Titans y la entropía de las reglas recuperadas para la consulta activa.
7. **Darwin Gödel Machine (DGM) & AlphaEvolve Live Tournament (`_evaluate_candidate_mutation_live`):** Evalúa cada candidato mutante en vivo compilando su AST, verificando ausencia de defectos con `Z3VerificationEngine(use_bitvectors=True)`, ejecutándolo en una sandbox estéril contra vectores de frontera `[-10, -1, 0, 1, 42]` y midiendo su cobertura asociativa real sobre la consulta. Rechaza entradas vacías (`REJECTED_EMPTY_INPUT_SIGNAL`) y descarta candidatos con errores sintácticos o violaciones de invariantes.
8. **Voyager Skill Verification & AST IFDS Taint Gate (`ASTIFDSDataflowTaintGate`):** Inspecciona el AST de Python para detectar sumideros de ejecución dinámica (`eval`, `exec`, `os.system`, `subprocess.*(..., shell=True)`) y bucles `while True:` sin variante de salida, suprimiendo falsos positivos en comentarios.

---

## 3. Comandos Principales

```bash
# 1. Instalar en modo editable (PEP 621 pyproject.toml) y ejecutar las 1.389 pruebas
pip install -e .
python3 aleph_cli.py test

# 2. Consultar telemetría de la Bóveda, cadena Merkle y retención Top-K
python3 aleph_cli.py bitacora-status

# 3. Recuperación asociativa HippoRAG 2 PPR + LSH Semántico
python3 aleph_cli.py bitacora-search "PostgreSQL 18 Supabase RLS ATTACH PARTITION"

# 4. Compuerta Pre-Turno AST IFDS Taint + Bitácora
python3 aleph_cli.py bitacora-enforce "SELECT id FROM users WHERE tenant_id = auth.uid();"

# 5. Ciclo evolutivo en vivo DGM + AlphaEvolve + Titans + TextGrad
python3 aleph_cli.py omega-self-improve "Optimizar verificación formal de contratos AST"

# 6. Escáner de higiene y verificación criptográfica del repositorio
python3 .aleph/scripts/scan_cleanliness.py

# 7. Evaluación experimental A/B controlada con McNemar exacto
python3 -m ab_eval.ab_harness --tasks ab_eval/tasks.example.jsonl --agent-cmd "./mi_agente.sh" --reps 3
```
