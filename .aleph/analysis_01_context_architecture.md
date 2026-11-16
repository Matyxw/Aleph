# ARQUITECTURA PRAGMÁTICA DE CONTEXTO Y EJECUCIÓN: 'EL ALEPH'
## Análisis Técnico de Ingeniería de Arneses de Producción basado en Everything Claude Code (ECC)

> **Documento:** Informe Técnico de Arquitectura — Módulo 01  
> **Destino:** `.aleph\analysis_01_context_architecture.md`  
> **Referencia:** Arquitectura real de Everything Claude Code (`affaan-m/ECC`), Claude Code CLI, Gemini API y arneses de producción  
> **Fecha:** Octubre 2026  
> **Estado:** APROBADO PARA IMPLEMENTACIÓN  

---

## 1. Diagnóstico de Primeros Principios: Descarte de Ilusiones de Hardware

### 1.1 De la "Fantasía de Hardware" a la Realidad del Arnés HTTP
Las iteraciones teóricas previas de "El Aleph" incurrieron en lo que denominamos **Ilusión de Infraestructura**: diseñar un arnés de agentes pretendiendo controlar directamente punteros de memoria física de VRAM, árboles *RadixAttention* de GPU, llamadas de kernel en Ring 0 (`CreateFileW` restrictivo), enclaves de cómputo confidencial (TEE AMD SEV / Intel SGX) y microVMs de Hyper-V.

Cuando se construyen agentes sobre modelos comerciales de frontera (Anthropic Claude 3.5 Sonnet / Opus, Google Gemini 1.5 Pro / Flash, OpenAI GPT-4o), la realidad física del sistema es radicalmente distinta:
1. **Caja Negra Remota:** El modelo de lenguaje reside detrás de balanceadores de carga HTTP/gRPC a cientos de kilómetros. El cliente local **no tiene acceso a la GPU**, no manipula el *KV-cache physical allocator* ni puede arbitrar el hardware del clúster remoto.
2. **Latencia de Red:** La métrica crítica que estrangula el rendimiento no es el acceso a disco local (13 ms en NTFS), sino la latencia de red y el *Time To First Token* (TTFT), que oscila entre **800 ms y 4.500 ms** por roundtrip HTTP.
3. **Restricción de Throughput, no de Memoria Local:** Los cuellos de botella son límites de cuota impone el proveedor (Requests Per Minute - RPM, Tokens Per Minute - TPM), saturación del servidor remoto (códigos HTTP 429 y 529), y degradación de la atención cuando el contexto se infla innecesariamente.

El proyecto de referencia de la industria, **Everything Claude Code (affaan-m/ECC)**, no pretende reinventar el sistema operativo ni simular controladores de dispositivos. ECC es un **sistema de optimización de rendimiento para el arnés del agente**: un middleware pragmático que gobierna el contexto, restringe quirúrgicamente las herramientas por rol, intercepta eventos mediante hooks y formatea contratos estrictos.

```
+───────────────────────────────────────────────────────────────────────────────────+
|                           ARQUITECTURA REAL DE PRODUCCIÓN                         |
|                                                                                   |
|   +────────────────────────────+              HTTP REST / gRPC                    |
|   |    ARNÉS LOCAL (EL ALEPH)  | ◄────────────────────────────────────────────►   |
|   | - Context Budgets & Hooks  |    [Latencia: 800ms - 4500ms | TTFT remoto]      |
|   | - JSON Schema Tool Calling |    [Cuotas: RPM / TPM / Rate Limits 429]         |
|   | - Working Memory en Disco  |                                                  |
|   | - Subagentes Aislados      |                                                  |
|   +─────────────┬──────────────+                                                  |
|                 │                                                                 |
|                 ▼                                                                 |
|   +────────────────────────────+                                                  |
|   | SISTEMA LOCAL (WINDOWS/OS) |                                                  |
|   | - Archivos, Git, Terminal  |                                                  |
|   | - Tests deterministas      |                                                  |
|   +────────────────────────────+                                                  |
+───────────────────────────────────────────────────────────────────────────────────+
```

---

## 2. Presupuestos de Contexto (Context Budgets) y Compactación Estratégica (`/compact`)

### 2.1 La Patología del "Context Rot" y la Falla de la Auto-Compactación
A medida que la ventana de contexto acumula tokens (superando los 100k-160k tokens), ocurren tres degradaciones severas:
1. **Efecto Lost-in-the-Middle y Dilución Atencional:** El modelo pierde precisión para seguir reglas del sistema y confunde dependencias complejas.
2. **Explosión de Costos y Latencia:** En cada turno se re-evalúan decenas de miles de tokens de conversaciones pasadas obsoletas, multiplicando el TTFT.
3. **Auto-compactación Destructiva:** Los arneses ingenuos disparan la compactación cuando el buffer llega a un porcentaje arbitrario (e.g. 95%). Si esto ocurre en medio de una edición multilínea, un refactor activo o una sesión de depuración, la compactación ciega borra variables locales, hipótesis de error no confirmadas y diffs activos, dejando al agente en un estado de amnesia incoherente.

### 2.2 La Solución de ECC: Compactación Multiseñal (`suggest-compact.js`)
ECC implementa una arquitectura de monitoreo pasivo en hooks (`PreToolUse` sobre `Edit` y `Write`) que combina dos señales reales:

```javascript
// Principio de medición en transcript de ECC (suggest-compact.js)
const contextTokens = usage.input_tokens + usage.cache_read_input_tokens + usage.cache_creation_input_tokens;
```

* **Señal Primaria (Tamaño Real de Contexto):** Lee el registro `usage` del transcript de la sesión. Compara la suma real de tokens frente al tamaño de la ventana:
  - Ventana de 200k: Alerta a los **160k tokens**.
  - Ventana de 1M: Alerta a los **250k tokens**.
  - Intervalo de re-aviso: Cada **60k tokens adicionales** de crecimiento.
* **Señal Secundaria (Conteo de Tool Calls):** Dispara a los **50 tool calls** y luego cada **25 tool calls**.
* **Razón Técnica:** El conteo de herramientas es un proxy débil. Dos lecturas de archivos grandes o una respuesta masiva de terminal pueden consumir 80k tokens en 3 llamadas, mientras que 50 llamadas a `grep` apenas consumen 5k tokens. La señal de tokens reales previene el desbordamiento imprevisto.

### 2.3 Fronteras Lógicas de Tarea (Task-Boundary Compaction)
La compactación nunca debe ocurrir durante la ejecución atómica de un paso. Debe ejecutarse **exclusivamente en las fronteras lógicas entre fases**:

| Transición de Fase | Qué se purga del contexto | Qué se preserva en el prompt compacto |
| :--- | :--- | :--- |
| **Post-Exploración $\to$ Pre-Plan** | Salidas completas de `grep`, lecturas de archivos de referencia, intentos de búsqueda fallidos. | Lista canónica de rutas afectadas, interfaces identificadas, restricciones técnicas. |
| **Post-Plan $\to$ Pre-Ejecución** | Discusión de opciones descartadas, alternativas arquitectónicas evaluadas. | Checklist atómico de tareas (`TODO.md`), contratos de interfaz, criterios de aceptación. |
| **Post-Hito $\to$ Pre-Siguiente Hito** | Diffs intermedios ya commiteados, salidas verbosas de linters corregidos. | Estado consolidado del sistema, tests verdes, siguiente hito del checklist. |
| **Post-Debugging $\to$ Pre-Feature** | Stack traces gigantes, hipótesis de fallo refutadas, logs temporales. | Causa raíz identificada, fix aplicado, prueba de regresión añadida. |

### 2.4 Patrón "Working Memory on Disk"
El contexto conversacional de los LLMs debe tratarse como **memoria RAM volátil**, no como almacenamiento principal:
- La fuente de verdad del avance no es el chat, sino el disco: archivos como `task_plan.md`, `state.json` o diarios estructurados.
- Si el contexto se compacta a cero (`/clear` o `/compact`), el agente simplemente lee el archivo de estado en disco y reanuda el trabajo en menos de 500 tokens de contexto inicial sin perder una sola variable.

---

## 3. Inyección Quirúrgica de Herramientas (`allowed-tools`) y Subagentes Especializados

### 3.1 El Problema del "Tool Bloat"
Proporcionar 40 herramientas simultáneas en el System Prompt genera patologías críticas:
1. **Impuesto de Tokens Fijo:** Cada definición de herramienta en formato JSON Schema consume entre 250 y 600 tokens. Un catálogo de 30 herramientas inyecta 10.000 a 15.000 tokens en *cada llamada*, encareciendo la sesión e invalidando caches si hay variaciones.
2. **Confusión y Alucinación de Firma:** A mayor número de herramientas, mayor probabilidad de que el modelo invoque la herramienta incorrecta o mezcle argumentos.
3. **Expansión de la Superficie de Ataque (Prompt Injection):** Si un subagente dedicado a leer documentación externa o analizar issues de GitHub tiene acceso a `Bash` o `Write`, un ataque de inyección indirecta puede ordenar la ejecución de comandos arbitrarios en el sistema anfitrión.

### 3.2 Taxonomía de Subagentes y Confinamiento en ECC
ECC estructura los agentes en definiciones independientes (`agents/<role>.md`) donde el frontmatter YAML impone un confinamiento estricto de capacidades:

```yaml
---
name: architect
description: Especialista en diseño de sistemas y contratos técnicos.
tools: Read, Grep, Glob
model: opus
---
```

```yaml
---
name: security-reviewer
description: Detección y auditoría de vulnerabilidades antes de producción.
tools: Read, Grep, Glob, Bash
model: sonnet
---
```

### 3.3 Matriz de Roles y Asignación de Modelos para 'El Aleph'

| Perfil de Agente | Herramientas Permitidas (`allowed-tools`) | Modelo Óptimo | Justificación de Restricción |
| :--- | :--- | :--- | :--- |
| **Orchestrator / Dispatcher** | `[invoke_subagent, read_file, manage_task]` | Tier Alto (`Opus / Pro`) | Descompone tareas y enruta. No toca código directamente ni ejecuta comandos de shell. |
| **Architect** | `[view_file, search_code, read_url]` | Tier Alto (`Opus / Pro`) | Solo lectura y modelado conceptual. Prohibido `write_file` y `run_command`. |
| **Implementer / Coder** | `[view_file, replace_file_content, write_to_file]` | Tier Medio (`Sonnet / Flash`) | Enfocado puramente en edición quirúrgica de código. Sin acceso irrestricto a shell. |
| **Tester / QA Runner** | `[view_file, run_command(test only)]` | Tier Medio (`Sonnet / Flash`) | Corre suites de test deterministas. No modifica la lógica del código de negocio. |
| **Security Auditor** | `[view_file, search_code, run_command(linters)]` | Tier Alto (`Opus / Pro`) | Ejecuta análisis estático y audita vectores. Prohibido escribir código o saltarse gates. |
| **Linter / Summarizer** | `[view_file]` | Tier Ligero (`Haiku / Flash-Lite`) | Tareas mecánicas de formateo, extracción de esquemas o síntesis de diffs. Costo marginal. |

### 3.4 Aislamiento de Contexto (Context Isolation)
El orquestador no ejecuta el trabajo de los subagentes dentro de su propio hilo. Invoca al subagente en una conversación aislada (`invoke_subagent`). El subagente consume su propio contexto para navegar archivos, correr pruebas y depurar, y devuelve únicamente un **informe sintético final** al orquestador. Esto mantiene el contexto del orquestador limpio y enfocado durante cientos de pasos.

---

## 4. Manejo de APIs Remotas: La Realidad de la Caja Negra HTTP

### 4.1 Características Reales de las APIs de Claude y Gemini
A diferencia de un motor local de inferencia, las APIs comerciales presentan características inmutables que el arnés debe gobernar:
- **Protocolo Stateless:** Cada turno envía la lista completa de mensajes y herramientas (salvo por el uso de Prompt Caching del proveedor).
- **Latencia de Red No Negociable:** Un llamado típico con 50k tokens de entrada y herramientas tarda entre 1.5s y 6s. No existe la latencia de microsegundos de la GPU local.
- **Cuotas Duras de Proveedor:**
  * Rate limits por minuto: Tier 1 suele tener 50 RPM o 40.000 TPM; Tier 4 llega a miles de RPM.
  * Violaciones de cuota devuelven HTTP `429 Too Many Requests` o `529 Overloaded`.

### 4.2 Patrones de Resiliencia y Estabilidad en el Arnés

```
[Llamada de Arnés] ──► [HTTP Request] ──► [Respuesta 200 OK] ──► [Ejecutar Tool]
                             │
                             ├─► [429 / 529 Rate Limit] ──► [Backoff Exponencial + Jitter] ──► Reintentar
                             │
                             ├─► [500 Server Error]     ──► [Circuit Breaker (Max 3)]      ──► Abortar/Fallback
                             │
                             └─► [Timeout > 30s]        ──► [Cancelación limpia socket]    ──► Reintentar
```

1. **Backoff Exponencial con Jitter:**
   $$\text{Espera} = \min(t_{\max}, t_{\text{base}} \times 2^{\text{intento}}) \pm \text{random\_jitter}$$
   Evita el efecto de estampida (*thundering herd*) contra la API del proveedor.
2. **Circuit Breakers Financieros y Operativos:**
   - Detención inmediata si el gasto proyectado de la sesión supera un umbral fijado por el usuario (e.g. $5.00 USD).
   - Detención si se acumulan 3 errores HTTP 500 consecutivos, evitando bucles infinitos de quema de tokens.
3. **Idempotencia de Herramientas:**
   Si una llamada HTTP se corta por timeout de red pero el modelo llegó a ejecutar parcialmente un side-effect en una herramienta, reintentar la llamada puede duplicar mutaciones (e.g. dos `git commit` o dos llamadas de facturación). Las herramientas mutables deben requerir claves de idempotencia o verificación previa de estado.

### 4.3 Alineación Estricta con el Prompt Caching del Proveedor
El Prompt Caching de Anthropic (`cache_control: {"type": "ephemeral"}`) y Gemini Context Caching no son magia: requieren **prefijos de tokens idénticos byte a byte**.

Para lograr tasas de acierto de caché de **80% a 95%**, el arnés debe ordenar el prompt en bloques estrictos:

```
┌─────────────────────────────────────────────────────────────┐
│ BLOQUE 1 (ESTÁTICO GLOBAL): System Prompt Base + Guardrails  │ ◄── Cache Breakpoint 1
├─────────────────────────────────────────────────────────────┤
│ BLOQUE 2 (ESTÁTICO PROYECTO): Tool Definitions JSON Schemas  │ ◄── Cache Breakpoint 2
├─────────────────────────────────────────────────────────────┤
│ BLOQUE 3 (SEMI-ESTÁTICO): Convenciones de repo (CLAUDE.md)  │ ◄── Cache Breakpoint 3
├─────────────────────────────────────────────────────────────┤
│ BLOQUE 4 (DINÁMICO EFÍMERO): Historial de turnos y tools    │ (No cacheable / cola)
└─────────────────────────────────────────────────────────────┘
```

**Regla de Oro:** Nunca inyectar marcas de tiempo variables (`Date.now()`), IDs dinámicos de sesión o instrucciones cambiantes en el Bloque 1 o 2. Hacerlo invalida la caché completa en cada turno, multiplicando el costo por 10x y disparando la latencia.

---

## 5. Tool Calling Nativo: Erradicación Total de Formatos Exóticos

### 5.1 El Fallo de los Formatos de Pipes y Pseudo-JSON
Durante años se intentaron formatos alternativos para invocar herramientas bajo la promesa de ahorrar tokens:
- **Sintaxis de Pipes:** `|CALL|edit_file|path/to/file|10|25|content|`
- **Markdown Blocks:** ````call:tool_name\narg1=val1\narg2=val2````
- **YAML Embebido:** Bloques de YAML no validados en texto plano.

**Por qué colapsaron en producción:**
1. **Ruptura de Delimitadores:** Si el argumento de una herramienta contiene código con pipes (`|`), comillas escapadas o secuencias regex complejas, el parser basado en strings o expresiones regulares colapsa con `ParsingError`.
2. **Ausencia de Decodificación Guiada (Constrained Decoding):** Cuando el modelo genera texto libre simulando un formato exótico, no hay nada a nivel de red neuronal que le impida omitir un parámetro requerido o alucinar un campo inexistente.
3. **Falsa Economía:** El 15% de tokens "ahorrados" en sintaxis se pierde en las siguientes 3 llamadas requeridas para corregir el error de sintaxis que el LLM introdujo.

### 5.2 El Estándar Universal: JSON Schema Nativo (Structured Outputs)
Los motores modernos (Claude API, OpenAI, Gemini) implementan soporte de **Structured Outputs mediante gramáticas formales en el decodificador**:
- Durante la generación del bloque de argumentos, la API enmascara los logits de salida para que sea **matemáticamente imposible** generar un token que viole el JSON Schema declarado.
- Los tipos primitivos (`string`, `integer`, `boolean`, `array`, `object`), los `enum` y la lista de `required` se cumplen al 100% sin excepción.
- La respuesta HTTP devuelve un objeto estructurado que se parsea nativamente en memoria mediante `JSON.parse` o `pydantic.model_validate_json` en menos de **0.05 ms**.

### 5.3 Contrato Formal de Herramienta para 'El Aleph'

```json
{
  "name": "edit_file_atomic",
  "description": "Aplica una modificación contigua a un archivo verificando hash previo.",
  "parameters": {
    "type": "object",
    "properties": {
      "target_file": {
        "type": "string",
        "description": "Ruta absoluta al archivo a modificar."
      },
      "expected_sha256": {
        "type": "string",
        "description": "Hash SHA-256 del contenido actual antes de aplicar el cambio."
      },
      "target_content": {
        "type": "string",
        "description": "Bloque exacto existente a ser reemplazado."
      },
      "replacement_content": {
        "type": "string",
        "description": "Nuevo contenido que reemplazará al bloque objetivo."
      }
    },
    "required": ["target_file", "expected_sha256", "target_content", "replacement_content"],
    "additionalProperties": false
  }
}
```

**Ventajas Mecánicas:**
- `additionalProperties: false` prohíbe campos inventados por el modelo.
- El tipado estricto permite validación instantánea con Pydantic en Python o Zod en TypeScript.
- Cero ambigüedad en caracteres escapados (saltos de línea, comillas dobles y caracteres Unicode se gestionan bajo la especificación estándar RFC 8259).

---

## 6. Plan de Arquitectura y Refactorización para 'El Aleph Pragmático'

Para convertir 'El Aleph' en un motor de clase mundial, eficiente y libre de complejidades accidentales, se define el siguiente mapa de refactorización:

```
+──────────────────────────────────────────────────────────────────────────────────────────+
|                           MAPA DE REFACTORIZACIÓN: EL ALEPH                              |
+────────────────────────────────────────────┬─────────────────────────────────────────────+
| COMPONENTES OBSOLETOS / DESCARTADOS        | REEMPLAZO PRAGMÁTICO DE PRODUCCIÓN          |
+────────────────────────────────────────────┼─────────────────────────────────────────────+
| 1. RadixAttention / Zero-Copy GPU Sharing  | Prompt Caching de Proveedor (Cache Control) |
| 2. Kernel Locks Ring 0 (`CreateFileW`)     | Bloqueos atómicos de archivo temp + rename  |
| 3. TEE AMD SEV / Hyper-V MicroVMs          | Sandboxing por permisos y checkpoints CLI   |
| 4. Deduplicación por Cosine Sim. Embeddings| Hashing determinista + CLI Mechanical Finger|
| 5. Formatos de pipes / pseudo-JSON         | JSON Schema nativo (Structured Outputs)     |
| 6. Auto-compactación reactiva arbitraria   | Compactación estratégica guiada por fases   |
| 7. Catálogo masivo de 30+ tools globales   | Subagentes con `allowed-tools` mínimas      |
+────────────────────────────────────────────┴─────────────────────────────────────────────+
```

### Componentes Inmediatos a Implementar en el Core:
1. **`ContextGovernor`**: Módulo que monitorea el transcript de la sesión, calcula el uso real de tokens acumulados e inyecta la recomendación de `/compact` en las fronteras de hito.
2. **`AgentRegistry`**: Catálogo de especificaciones de agentes (`.md` con frontmatter) que inyecta únicamente las herramientas declaradas en `allowed-tools` según el rol activo.
3. **`HttpResilienceLayer`**: Manejo de peticiones remotas con backoff exponencial, jitter y circuit breakers de cuota/error para Claude y Gemini.
4. **`NativeToolDefinition`**: Generación automática de esquemas JSON compatibles con Anthropic / OpenAI / Gemini a partir de dataclasses tipadas.

---

## 7. Conclusión

El rendimiento de un arnés de IA no se mide por la sofisticación de la jerga que describe su hardware imaginario, sino por su **eficiencia verificable en el mundo real**:
- Menor tiempo total por tarea (reduciendo roundtrips y optimizando el TTFT).
- Cero caídas por errores de parseo sintáctico (adoptando JSON Schema nativo).
- Mínimo costo por sesión (aprovechando el Prompt Caching del proveedor y evitando el context bloat mediante compactación estratégica).
- Máxima seguridad de ejecución (confinando las herramientas estrictamente necesarias para cada subagente).

Este informe establece los fundamentos técnicos inmutables sobre los cuales debe construirse el nuevo motor pragmático de **El Aleph**.
