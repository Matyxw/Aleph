# ESPECIFICACIÓN DE INGENIERÍA: INTEGRACIÓN FORMAL SMT (MICROSOFT Z3) EN EL ALEPH

> **Documento:** `spec_smt_formal_verification.md`  
> **Subsistema:** El Aleph // AST Guard & Formal Verification Engine  
> **Estado:** PRODUCCIÓN VERIFICADA Y PROBADA  
> **Fecha:** Octubre 2026  
> **Dependencias:** `z3-solver >= 4.12.0`, `hypothesis >= 6.100.0`, `ast` nativo  

---

## 1. De la Verificación Empírica a la Certeza Matemática Absoluta

### 1.1 El Teorema de Dijkstra y el Límite del Testing Empírico
El testing tradicional (unit tests, mutation testing, exit codes) evalúa un subconjunto finito de vectores de entrada:
$$\mathcal{D}_{\text{eval}} \subset \mathcal{D}_{\text{input}}, \quad |\mathcal{D}_{\text{eval}}| \ll |\mathcal{D}_{\text{input}}| = 2^{64 \times k}$$
Según el principio fundacional de Edsger Dijkstra:
> *"Program testing can be used to show the presence of bugs, but never to show their absence."*

El Aleph trasciende este límite reduciendo la corrección de programas a un problema de satisfacibilidad módulo teorías (SMT):
$$\text{Correctness}(\mathcal{P}, \text{Pre}, \text{Post}) \iff \neg \exists \vec{x} \in \mathcal{D}_{\text{input}}: \big(\text{Pre}(\vec{x}) \land \text{VC}(\mathcal{P}, \vec{x}) \land \neg \text{Post}(\vec{x})\big)$$
$$\iff \text{UNSAT}\big(\text{Pre} \land \text{VC} \land \neg \text{Post}\big)$$

Si el solver Z3 retorna **UNSAT**, el programa está matemáticamente garantizado libre de defectos para la totalidad del dominio de entrada ($2^{64}$ posibilidades por variable).  
Si el solver retorna **SAT**, Z3 sintetiza un **modelo concreto $\mathcal{M}$ (contraejemplo)** que demuestra formalmente la existencia del defecto.

---

## 2. Arquitectura de Integración en el Pipeline de El Aleph

```
                     ┌───────────────────────────────────────────┐
                     │          AST Guard (Entrada)              │
                     └─────────────────────┬─────────────────────┘
                                           │
                                           ▼
                     ┌───────────────────────────────────────────┐
                     │        AST Contract Extractor             │
                     │  • @requires (Precondiciones P)           │
                     │  • @ensures (Poscondiciones Q)            │
                     │  • @invariant (Invariantes de Estado I)   │
                     │  • Refined Types (Annotated[T, Pred])     │
                     └─────────────────────┬─────────────────────┘
                                           │
                                           ▼
                     ┌───────────────────────────────────────────┐
                     │    VCGen & SSA Symbolic Transformer       │
                     │  • Transformación Single Static Assign.   │
                     │  • Path Conditions por bifurcación        │
                     │  • Metas de Seguridad (Safety Goals)      │
                     └─────────────────────┬─────────────────────┘
                                           │
                                           ▼
                     ┌───────────────────────────────────────────┐
                     │    Microsoft Z3 SMT Solver Engine         │
                     │  • Teorías: QF_LIA, QF_BV, QF_AX          │
                     │  • Tácticas: simplify, solve-eqs, smt     │
                     │  • Timeout Duro: 40 ms                    │
                     └───────────────┬───────────────────────────┘
                                     │
           ┌─────────────────────────┼─────────────────────────┐
           ▼                         ▼                         ▼
   ┌───────────────┐         ┌───────────────┐         ┌───────────────┐
   │     UNSAT     │         │      SAT      │         │ TIMEOUT/UNKN  │
   │  (Proven Safe)│         │(Defect Found) │         │   (Fallback)  │
   └───────┬───────┘         └───────┬───────┘         └───────┬───────┘
           │                         │                         │
           ▼                         ▼                         ▼
   EpistemicStatus:          Synthesize Witness        Property-Based
   FORMALLY_PROVEN           Concrete Inputs           Testing (PBT)
   Proof Hash persistido     Runtime Sandbox Replay    Hypothesis Fuzzing
   en SQLite WAL (0 def)     Confirm True Positive     (200 iteraciones)
                             (0.0% False Positives)    PBT_VERIFIED
```

---

## 3. Extracción de Contratos Formables

### 3.1 Sintaxis Unificada Python / TypeScript
1. **Python:**
   ```python
   @requires("b != 0")
   @ensures("result * b == a")
   def safe_div(a: int, b: int) -> int:
       return a // b
   ```
2. **TypeScript:**
   ```typescript
   /**
    * @requires b !== 0
    * @ensures result * b === a
    */
   function safeDiv(a: number, b: number): number {
       return Math.floor(a / b);
   }
   ```
3. **Tipos Refinados:**
   ```python
   Port = Annotated[int, "v >= 1 and v <= 65535"]
   ```

---

## 4. Demostración Formal de los 5 Defectos Críticos

| Defecto Crítico | Condición de Inseguridad (Búsqueda SAT) | Teoría SMT | Garantía Formal |
| :--- | :--- | :--- | :--- |
| **División por Cero** | $\text{Pre} \land \text{PC} \land (divisor = 0)$ | QF_LIA / QF_BV | Imposibilidad matemática de `ZeroDivisionError` |
| **Desbordamiento Numérico** | $\text{Pre} \land \text{PC} \land \neg \text{BVAddNoOverflow}(a, b)$ | QF_BV (32/64 bits) | Cero wrapping o truncamiento inesperado |
| **Desreferencia Nula** | $\text{Pre} \land \text{PC} \land (obj = 0)$ | QF_LIA / Punteros | Cero `AttributeError` / `NoneType dereference` |
| **Acceso Fuera de Rango** | $\text{Pre} \land \text{PC} \land \neg(0 \le idx < len(arr))$ | QF_LIA + Arrays | Cero `IndexError` en listas o buffers |
| **Invariante de Estado** | $I(s) \land \text{Pre}(args) \land \text{Step}(s, s') \land \neg I(s')$ | Inducción LIA/BV | Preservación estricta de invariantes de negocio |

---

## 5. Estrategia de Decidibilidad y Timeouts (<50 ms)

1. **Restricción de Fragmento:** Exclusión estricta de lógica de primer orden no acotada con alternancia de cuantificadores ($\forall \exists$). Todas las fórmulas operan en fragmentos libres de cuantificadores (QF).
2. **Pipeline de Tácticas Z3:**
   ```python
   tactic = z3.Then('simplify', 'solve-eqs', 'bit-blast', 'smt')
   ```
3. **Timeout en C++ Nativo:** `solver.set("timeout", 40)` (40 ms duros).
4. **Fallback a Hypothesis:** Si el solver excede 40 ms o devuelve `unknown`, se ejecuta automáticamente `PropertyBasedFallback` ejecutando 100-200 vectores generativos en <300 ms.

---

## 6. Política Cero Falsos Positivos (0.0% False Positive Rate)

El mayor veneno de los analizadores estáticos clásicos es la tasa de falsos positivos, que destruye la confianza y satura a los agentes.  
En El Aleph, **ningún defecto se reporta al Coder Agent sin validación de testigo ejecutable**:
1. Z3 genera el modelo $\mathcal{M} = \{x: 10, y: 0\}$.
2. El motor sintetiza un archivo de prueba Python/TS temporal (`test_counterexample_witness_*`).
3. El test se ejecuta dentro del runtime real.
4. **Criterio de Aceptación:**
   - Si el runtime lanza la excepción real (`ZeroDivisionError`, `IndexError`): Se confirma como **True Positive (100% real)**.
   - Si el runtime no falla (por supuestos de abstracción incompletos): El reporte se descarta de la alerta al Coder y se encola para refinamiento de invariantes.
   - **Tasa de falsos positivos entregados al usuario = 0.0%.**
