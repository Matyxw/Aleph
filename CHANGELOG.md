# CHANGELOG

## 33.0.0 — Reconstrucción SOTA Integral, Verificación Empírica 100 % y Cero Deuda Técnica

### 1. Oráculo Físico en Chromium/Blink Real y Suite Unificada (`0` Tests Saltados)
- **Oráculo en Vivo Nativo (`aleph_render_oracle.py`, `playwright_layout_runner.mjs`):** Integrado pool persistente de Chromium/Blink real mediante Chrome DevTools Protocol (`Emulation.setDeviceMetricsOverride`) y carga por URI `data:text/html;charset=utf-8` sobre los 6 viewports canónicos (`320px`, `375px`, `768px`, `1024px`, `1440px`, `1920px`). Corregido bug en la detección de co-linearidad de botones en viewports `desktop_*`.
- **Solucionador Analítico Exacto `QF_LRA` (`aleph_smt_layout_verifier.py`):** Implementada resolución exacta por puntos críticos de funciones lineales por tramos (`FluidMeasure.critical_points`) cuando `z3-solver` no está instalado, eliminando el fallo `AttributeError: 'NoneType' object has no attribute 'Solver'`.
- **Compatibilidad Dual Pydantic v1/v2 y Unittest/Pytest (`.aleph/lib/*.py`, `.aleph/tests/*.py`, `aleph_cli.py`):** Añadido soporte completo para `.model_dump()`, `.model_dump_json()`, `.model_validate()`, `.model_fields_set` y validadores de instancia sobre Pydantic v1 y v2. Unificadas las suites `aleph_core/tests` (1.270 tests) y `.aleph/tests` (108 tests) en `python3 aleph_cli.py test` (**1.378 tests pasando en ~13 s, 0 fallos, 0 saltados**).

### 2. Implementación Real de los 8 Pilares SOTA (`omega_continual_learner.py`)
- **HippoRAG 2:** Añadidos embeddings semánticos por proyección aleatoria con signo de trigramas y tokens ($D=64$, similitud coseno) combinados con Okapi BM25, Personalized PageRank ($lpha=0.15$) y prior empírico de Fisher.
- **Titans Associative Memory Matrix:** Implementada matriz paramétrica $M_t \in \mathbb{R}^{16 	imes 16}$ con actualización por regla delta $
abla_M \mathcal{L} = (M_{t-1} k_t - v_t) k_t^	op$, compuerta de decaimiento adaptativa $lpha_t$ y momento $S_t$.
- **EWC Fisher Empírico y Medición de Retención Top-K:** Implementado cálculo analítico de la diagonal de Información de Fisher $F_{ii}$ y medición empírica `measure_topk_retrieval_forgetting` (`Recall@5 = 100.0 %`, `0.0 %` olvido).
- **MemGPT Tiered Memory Pager:** Implementado paginador de 3 niveles (`core_memory`, `recall_buffer` con desalojo por presupuesto de tokens y `archival_memory`).
- **ExpeL Autonomous AST Distillation:** Implementado `distill_rule_from_episodic_trace` para extraer automáticamente reglas `SI → ENTONCES → EVITAR` desde diferencias AST entre código fallido y reparado.
- **Torneo DGM / AlphaEvolve en Vivo y Compuerta AST IFDS Taint:** `run_omega_self_improvement_cycle` ahora ejecuta `Z3VerificationEngine(use_bitvectors=True)` y pruebas en sandbox estéril sobre cada candidato mutante, rechaza entradas vacías (`REJECTED_EMPTY_INPUT_SIGNAL`) y evalúa flujo Taint sobre el AST real (`ASTIFDSDataflowTaintGate`) ignorando comentarios.

### 3. Motores V4, Hooks, Higiene, Privacidad y Empaquetado PEP 621
- **Motores `.aleph/v4_engine/` Completos:** Reconstruidos desde cero `aep_protocol.py` (tramas binarias CRC32/SHA-256 y tokens HMAC), `causal_world_model.py` (SCM de Judea Pearl con cirugía $	ext{do}(X)$, contrafactuales en 3 pasos y VICReg), `holographic_causal_memory.py` (VSA de 10.240 bits con XOR autoinverso y Kanerva SDM) y `pqc_crypto_sealing.py` (anillo ciclotómico FIPS 203 $\mathbb{Z}_{3329}[X]/(X^{256}+1)$ y sellado TPM 2.0 PCR-16).
- **Hooks y Escáner de Limpieza (`.aleph/hooks/*.py`, `scan_cleanliness.py`):** Implementados hooks completos (`PreToolUse`, `PostToolUse` con `SurgicalLogCrusher`, `StopGate` con índice $I_{FE}$ y `UserPromptSubmit`) y auditor de higiene de repositorio.
- **Privacidad, Rutas Portables y Limpieza de Bloat:** Redactados teléfonos, correos y nombres personales residuales en `.aleph/BITACORA_MASTER_VAULT_V33.json` recalculando íntegramente la cadena Merkle SHA-256; reemplazadas todas las rutas locales `C:\Users\...` por rutas relativas portables; purgados del paquete los archivos mutables de runtime (`test_engine_v2.journal.jsonl`, `aleph_bench_v2.journal.jsonl`, `aleph_state.db`, `events.jsonl`) aislando `DATA_DIR` en `aleph_core/config.py`; diferenciados los manifiestos de gobernanza clonados; añadido `pyproject.toml` (PEP 621) y resellado criptográficamente `.aleph-cert.json`.
