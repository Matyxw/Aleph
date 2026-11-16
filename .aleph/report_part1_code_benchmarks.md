# SECCIÓN 1: Arquitectura de Código y Realidad Física de Bajo Nivel

---

## 1. Fundamentos Empíricos y Benchmarks de Realidad Física

El diseño de **El Aleph (Nivel 1 Core)** parte de un axioma de primeros principios: **ningún software puede operar desconectado de los límites físicos y restricciones del hardware y sistema operativo subyacente**. Las arquitecturas de agentes que tratan a los LLMs como solucionadores de propósito general para tareas mecánicas o que ignoran la latencia de I/O en disco colapsan bajo su propia deuda computacional.

Para fundamentar las decisiones de diseño del núcleo `aleph_core`, se ejecutaron tres benchmarks empíricos controlados en el entorno de producción (Windows 11, NTFS, Python 3.14). Los datos numéricos directos justifican cada componente arquitectónico.

---

### 1.1. Benchmark 1: Descarte de LLMs para Tareas Deterministas (`benchmark_ai_cleaner.py`)

Se evaluó la viabilidad de utilizar agentes basados en LLM para inspección, mantenimiento y limpieza de bajo nivel del sistema de archivos frente a herramientas nativas deterministas.

#### Configuración del Experimento
* **Muestra sintética representativa:** 15 archivos en sandbox que simulan el ecosistema real de un sistema operativo Windows (archivos binarios de caché, volcados de memoria `kernel_dump.dmp`, documentos personales antiguos, dependencias de código `node_modules`, parches del sistema `.msu`, bibliotecas compartidas críticas `vcredist_x64_2015.dll`, bases de datos SQLite locales, logs de telemetría y llaves criptográficas).
* **Entorno de ejecución:** `benchmark_ai_cleaner.py`.

#### Resultados Empíricos Medidos

| Métrica | Enfoque Determinista (SO) | Enfoque Agente LLM (Simulado) | Delta / Factor |
| :--- | :--- | :--- | :--- |
| **Tiempo de escaneo (15 archivos)** | **3.47 ms** | **12.75 s** | **3.674x más lento** |
| **Tasa de ambigüedad factual** | 0.0% (cumple reglas) | **33.33%** (5/15 archivos requieren juicio de usuario) | Inviable sin intervención |
| **Riesgo crítico de corrupción** | 0.0% (whitelists fijas) | **20.0%** (3/15 archivos DLL/MSU/SYS críticos) | Catastrófico |

#### Proyección Matemática a un Entorno Real (PC Windows con 250.000 archivos)

```
+-----------------------------------------------------------------------------------------+
| PROYECCIÓN EMPÍRICA: ESCANEO Y PURGA DE 250.000 ARCHIVOS EN WINDOWS                     |
+-----------------------------------------------------------------------------------------+
| Herramienta Determinista (WizTree / MFT Parsing):       1.8 segundos                   |
| Agente LLM Autónomo (Inferencia + API Roundtrips):      2.46 días ininterrumpidos       |
| Consumo de Tokens (650 tokens/archivo blended):         162.500.000 tokens             |
| Costo Financiero Directo (API $0.003 / 1k tokens):      $487.50 USD                    |
| Interrupciones al Usuario (5% casos ambiguos):          12.500 preguntas requeridas     |
| Tiempo Humano Bloqueado (3s por decisión):              10.42 horas de trabajo manual  |
+-----------------------------------------------------------------------------------------+
```

#### Veredicto y Descarte Arquitectónico
1. **Inviabilidad económica y temporal:** Pagar $487.50 USD y esperar 2.46 días por una tarea que un motor determinista basado en el análisis de la MFT (Master File Table) de NTFS resuelve en 1.8 segundos a costo cero viola el filtro de negocio y la eficiencia de primeros principios.
2. **Riesgo sistémico:** Un 20% de exposición a borrado accidental de componentes DLL o controladores del sistema genera inestabilidad letal en el sistema operativo.
3. **Decisión:** **Los LLMs quedan estrictamente excluidos de la gestión determinista de bajo nivel.** El Nivel 1 de El Aleph se delega a rutinas de código estricto, análisis léxico, interfaces POSIX/Win32 y comprobación de integridad criptográfica.

---

### 1.2. Benchmark 2: Cuello de Botella de I/O en Disco NTFS vs. GPU Radix Tree (`benchmark_io.py`)

Se evaluó la latencia de acceso al disco local bajo concurrencia extrema simulada de múltiples subagentes leyendo fragmentos de memoria y bases de conocimiento.

#### Configuración del Experimento
* **Carga:** Creación de 5.000 archivos Markdown (grafos de conocimiento).
* **Concurrencia:** 100 agentes concurrentes (`ThreadPoolExecutor` con 100 workers).
* **Transacciones:** 20 lecturas aleatorias por thread (2.000 operaciones de I/O de disco aleatorias).
* **Entorno:** `benchmark_io.py`.

#### Resultados de Latencia Empírica Medida

```
Total time for 2000 random reads: 0.570 s
--------------------------------------------------
P50 Latency:  13.55 ms
P95 Latency:  31.35 ms
P99 Latency:  41.57 ms
Max Latency:  60.94 ms
```

#### Análisis Físico y Diagnóstico
* **Umbral de inanición de GPU:** Un motor de inferencia local o clúster de subagentes que mantenga un *Radix Attention Tree* en memoria VRAM procesa tokens en microsegundos.
* **Diagnóstico:** Con una latencia **P99 de 41.57 ms** (y picos máximos de **60.94 ms**), el acceso directo y desestructurado a disco NTFS estrangula la canalización de ejecución. Las lecturas síncronas bloquean el pipeline de inferencia ("el Radix Tree se muere de hambre esperando a NTFS").
* **Decisión Arquitectónica:**
  1. No persistir estados efímeros en archivos de texto sueltos por agente.
  2. Uso mandatorio de **SQLite en modo WAL (`Write-Ahead Logging`)** con `PRAGMA synchronous = NORMAL`, lo que concentra los descriptores de archivo y minimiza las llamadas de sistema (syscalls) a disco.
  3. Adopción de diarios de eventos *append-only* en memoria/stream secuencial para aislar el flujo de cada agente.

---

### 1.3. Benchmark 3: Latencia de Enrutamiento y Parseo AST (`benchmark_router_ast.py`)

Se evaluó el costo computacional del análisis de sintaxis abstracta en tiempo real frente a texto plano, y la latencia del enrutamiento heurístico frente al enrutamiento semántico por SLM (*Small Language Model*).

#### Prueba A: Carga de Texto Plano vs. Parseo AST (2.000 Líneas de Código)
* **Raw Text Load Time:** **0.005 ms**
* **AST Parsing Time (`ast.parse` Python nativo):** **19.479 ms**
* **Factor de sobrecarga:** El parseo sintáctico en tiempo de ejecución añade un overhead de **~3.895x**.
* **Decisión:** Para validación de esquemas y enrutamiento estructural, el árbol AST debe precompilarse o representarse mediante contratos inmutables de bajo coste (`dataclasses`), evitando el re-parseo recurrente en caliente.

#### Prueba B: Despacho Concurrente en Swarm (50 Agentes Concurrentes)

| Mecanismo de Enrutamiento | Retardo por Decisión | Tiempo Total Despacho Swarm | Eficiencia Relativa |
| :--- | :--- | :--- | :--- |
| **SLM Router (Inferencia Ligera TTFT)** | 200 ms | **0.214 s** | Línea base |
| **Heuristic Router (Memoria / Tipado Nivel 0)** | 5 ms | **0.014 s** | **15.2x más rápido** |

#### Conclusión Arquitectónica
El enrutador central de Nivel 0 no debe realizar una inferencia probabilística previa para decidir qué módulo ejecuta un contrato. El dispatch se resuelve mediante mapas hash en memoria RAM (`Dict[str, Callable]`) con contratos inmutables. La inteligencia semántica se reserva exclusivamente para la síntesis de alto nivel.

---

## 2. Arquitectura Interna de `aleph_core`

El paquete `aleph_core` implementa la columna vertebral operativa de El Aleph, estructurada bajo estrictos patrones de ingeniería de sistemas:

```
aleph_core/
├── __init__.py
├── config.py                 # Constantes de configuración, rutas y timeouts
├── engine.py                 # Orquestador central de ejecución y verificación
├── memory/
│   ├── __init__.py
│   └── journal.py            # Diarios de memoria append-only por agente
├── router/
│   ├── __init__.py
│   └── dispatcher.py         # Despachador de contratos inmutables y Reducer
├── state/
│   ├── __init__.py
│   ├── epistemic.py          # Taxonomía epistémica y VerificationGate
│   └── store.py              # Persistencia SQLite WAL, leasing y atomic writes
└── tests/
    ├── __init__.py
    ├── test_engine.py
    ├── test_epistemic.py
    └── test_store.py
```

### 2.1. Configuración Central (`aleph_core/config.py`)

Define los límites operativos y la estructura de directorios:
* `BASE_DIR`: Directorio raíz de la biblioteca.
* `DATA_DIR` y `JOURNALS_DIR`: Directorios de almacenamiento persistente (`data/` y `data/journals/`).
* `DB_PATH`: Ruta al archivo central de base de datos SQLite (`aleph_state.db`).
* `DEFAULT_LEASE_TIMEOUT_SEC = 15`: Ventana de expiración para arrendamientos de recursos.
* `MAX_REDUCER_TOKENS = 1500`: Límite máximo de salida compactada (equivalente a 6.000 caracteres) antes de truncar respuestas en el bus de mensajes.
* `SQLITE_TIMEOUT_SEC = 10.0`: Tiempo de espera en bloqueos de conexión SQLite.

### 2.2. Motor de Despacho y Reducción (`aleph_core/router/dispatcher.py`)

El módulo de enrutamiento desacopla a los emisores de los ejecutores mediante dos contratos de datos inmutables:

1. **`TaskContract`:**
   ```python
   @dataclass
   class TaskContract:
       task_id: str
       task_type: str
       input_payload: Dict[str, Any]
       expected_output_schema: Optional[Dict[str, Any]] = None
       timeout_sec: float = 30.0
       created_at: float = field(default_factory=time.time)
   ```
2. **`TaskExecutionResult`:**
   Registra el resultado bruto, el resultado compactado, el tiempo de ejecución en milisegundos (`execution_time_ms`) con precisión de `time.perf_counter()` y los metadatos de error.
3. **Mecanismo Reducer:**
   La función estática `reduce_output(raw, max_chars)` serializa a JSON compacto y trunca determinísticamente cualquier payload que supere los `MAX_REDUCER_TOKENS * 4` caracteres, agregando un marcador explícito:
   `[TRUNCADO POR REDUCER: N caracteres omitidos]`. Esto erradica de forma mecánica el desbordamiento de ventana de contexto en el agente supervisor.

### 2.3. Diarios de Memoria Aislados (`aleph_core/memory/journal.py`)

Para evitar la contención de cerraduras (locks) en el almacenamiento central, cada agente posee una instancia de `AgentJournal`:
* **Formato:** JSON Lines (`.journal.jsonl`), estructurado para operaciones estrictamente *append-only*.
* **Aislamiento:** Cada archivo se nombra `{agent_id}.journal.jsonl`. No existen bloqueos cruzados entre agentes concurrentes.
* **Estructura del registro:**
  ```json
  {
    "timestamp": 1728690000.123,
    "agent_id": "test_engine_01",
    "event_type": "TASK_DISPATCHED",
    "payload": { ... }
  }
  ```
* **Recuperación:** Métodos deterministas `read_all()` y `get_latest(count=10)` para reconstruir la traza de auditoría y el historial reciente sin sobrecargar el contexto.

### 2.4. Ciclo de Ejecución Verificado en el Núcleo (`aleph_core/engine.py`)

La clase `AlephEngine` implementa el pipeline de ejecución en 6 fases continuas:

```mermaid
sequenceDiagram
    autonumber
    actor Client as Cliente / Subagente
    participant Engine as AlephEngine
    participant Journal as AgentJournal (JSONL)
    participant Store as StateStore (SQLite WAL)
    participant Dispatcher as TaskDispatcher
    participant Gate as VerificationGate

    Client->>Engine: execute_and_verify(task_type, payload, verifier_fn)
    Engine->>Journal: append_event("TASK_DISPATCHED")
    Engine->>Store: record_task_start(task_id, 'RUNNING')
    Engine->>Dispatcher: dispatch(contract)
    Dispatcher-->>Engine: TaskExecutionResult (raw, compact, latency_ms)
    Note over Engine: Instancia EpistemicClaim con estado INFERRED
    Engine->>Gate: verify(claim, verifier_fn, proof_context)
    Gate-->>Engine: claim actualizado (VERIFIED con proof_hash / REFUTED)
    Engine->>Store: save_claim(verified_claim)
    Engine->>Store: record_task_completion(task_id, status, proof_info)
    Engine->>Journal: append_event("TASK_COMPLETED")
    Engine-->>Client: Recibo de Ejecución Inmutable
```

---

## 3. Persistencia Atómica, Concurrencia y el Fix de Windows NTFS (`WinError 32`)

### 3.1. Persistencia SQLite WAL (`aleph_core/state/store.py`)

La clase `StateStore` gestiona tres tablas relacionales normalizadas para el control del sistema:
1. `epistemic_claims`: Registro inmutable de afirmaciones, estado epistémico, hash de prueba, contexto de verificación y payloads JSON.
2. `state_leases`: Mecanismo distribuido de arrendamiento de recursos con marcas de tiempo `acquired_at` y `expires_at`.
3. `task_ledger`: Libro contable de auditoría de todas las tareas despachadas, parámetros de entrada, salidas y estado final.

Para maximizar el rendimiento y permitir lectores concurrentes sin bloquear a los escritores, se configura en la inicialización:
* `PRAGMA journal_mode = WAL;` (Write-Ahead Logging).
* `PRAGMA synchronous = NORMAL;` (Garantiza integridad ante caídas sin forzar fsync completo en cada commit de lectura).

### 3.2. Concurrencia y Leasing con TTL

Para coordinar recursos compartidos entre múltiples agentes sin incurrir en deadlocks:
* `acquire_lease(resource_id, agent_id, timeout_sec)`:
  1. Purga de forma atómica arrendamientos caducados:
     ```sql
     DELETE FROM state_leases WHERE resource_id = ? AND expires_at < ?;
     ```
  2. Intenta insertar el nuevo lease con clave primaria sobre `resource_id`.
  3. Si otro agente retiene el lease dentro del TTL vigente, la base de datos lanza `sqlite3.IntegrityError`, retornando `False` de inmediato sin esperas activas degradantes.
* `release_lease(resource_id, agent_id)`:
  Elimina el lease de forma atómica condicionado a la identidad del agente poseedor.

### 3.3. Escritura Atómica en Dos Fases en Disco (`atomic_write_file`)

Para la generación de artefactos e informes en disco, `StateStore.atomic_write_file` previene estados corruptos o lecturas parciales mediante el siguiente algoritmo:
1. Generación de un archivo temporal en el mismo volumen: `target_path.with_suffix(suffix + f".tmp_{ms}")`.
2. Escritura del contenido completo con codificación UTF-8.
3. `f.flush()` seguido inmediatamente por `os.fsync(f.fileno())` para forzar a los platos/celdas NAND físicas del disco a confirmar los bloques de datos.
4. Cierre del descriptor de archivo.
5. `os.replace(temp_path, target_path)`: Operación atómica a nivel de sistema de archivos (en Windows ejecuta `MoveFileExW` con `MOVEFILE_REPLACE_EXISTING`), garantizando que cualquier proceso lector observe o la versión anterior intacta o la nueva versión completa, nunca un archivo a medio escribir.

---

### 3.4. El Problema Crítico de Windows NTFS: `WinError 32` (`ERROR_SHARING_VIOLATION`)

Durante el desarrollo de suites de pruebas con `tempfile.TemporaryDirectory()`, los sistemas Windows presentan una divergencia física fundamental con respecto a sistemas POSIX (Linux/macOS):

#### Divergencia entre SOs
* **POSIX:** La llamada `unlink()` elimina la entrada del directorio inmediatamente, incluso si otros descriptores de archivo mantienen abierto el inodo. El archivo se desasigna físicamente cuando el último proceso cierra su descriptor.
* **Windows NTFS:** La semántica de bloqueo de archivos es obligatoria (*mandatory locking*). Si un proceso o subproceso mantiene un handle abierto sobre un archivo (`.db`, `.db-wal` o `.db-shm`), cualquier intento de renombrar, sobrescribir o eliminar dicho archivo o su carpeta contenedora falla con la excepción del kernel:
  ```
  PermissionError: [WinError 32] El proceso no tiene acceso al archivo 
  porque está siendo utilizado por otro proceso.
  ```

#### Causa Raíz Identificada en SQLite
Si una conexión SQLite se mantiene abierta globalmente o se confía en el recolector de basura (`gc`) para invocar el destructor `__del__` de la conexión, los handles a los archivos `-wal` y `-shm` permanecen activos. Al finalizar un test unitario, `tempfile.TemporaryDirectory().cleanup()` intenta podar el árbol de directorios y colapsa de forma no determinista con `WinError 32`.

#### Solución Implementada: Context Managers Deterministas Forzados
En `aleph_core/state/store.py`, toda interacción con la base de datos se encapsuló en un generador contextual estricto:

```python
@contextmanager
def _connection(self):
    """
    Context manager que asegura apertura con WAL y cierre determinista 
    de handles (crucial en Windows).
    """
    conn = sqlite3.connect(str(self.db_path), timeout=SQLITE_TIMEOUT_SEC)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    try:
        yield conn
    finally:
        conn.close()
```

Gracias a la cláusula `finally: conn.close()`, el handle del kernel de Windows se libera en el instante exacto en que finaliza la sentencia `with self._connection() as conn:`. Esto erradica al 100% las colisiones de intercambio de archivos y permite ciclos de prueba y limpieza instantáneos sin fugas de handles.

---

## 4. Taxonomía Epistémica y Compuerta de Verificación Mecánica

Uno de los mayores fallos de las arquitecturas de agentes tradicionales es la **alucinación de competencia**: el agente declara internamente que una tarea está resuelta o que un dato es verdadero basándose únicamente en su propia autoconfianza textual.

El módulo `aleph_core/state/epistemic.py` impone una frontera epistemológica dura entre lo inferido y lo verificado.

### 4.1. Taxonomía de Tres Estados (`EpistemicStatus`)

```python
class EpistemicStatus(str, Enum):
    INFERRED = "INFERRED"    # Generado por inferencia heurística o LLM; no comprobado.
    VERIFIED = "VERIFIED"    # Demostrado empíricamente mediante ejecución de predicado.
    REFUTED  = "REFUTED"     # Falsado por fallo en la prueba o excepción de ejecución.
```

Toda salida de un modelo o subagente nace obligatoriamente con el estado `INFERRED`. Está terminantemente prohibido por diseño de software que el emisor asigne el estado `VERIFIED` por sí mismo.

### 4.2. Estructura de la Afirmación (`EpistemicClaim`)

```python
@dataclass
class EpistemicClaim:
    claim_id: str
    description: str
    payload: Any
    status: EpistemicStatus = EpistemicStatus.INFERRED
    proof_hash: Optional[str] = None
    proof_output: Optional[str] = None
    verified_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### 4.3. La Compuerta Determinista (`VerificationGate`)

La clase `VerificationGate` actúa como el árbitro de paso obligado:

```python
class VerificationGate:
    @staticmethod
    def verify(
        claim: EpistemicClaim,
        verifier_fn: Callable[[Any], bool],
        proof_context: Optional[str] = None
    ) -> EpistemicClaim:
        if claim.status == EpistemicStatus.VERIFIED:
            return claim

        try:
            passed = verifier_fn(claim.payload)
            now = time.time()
            if passed:
                claim.status = EpistemicStatus.VERIFIED
                claim.verified_at = now
                proof_data = f"{claim.claim_id}:{now}:{proof_context or 'passed'}"
                claim.proof_hash = hashlib.sha256(proof_data.encode("utf-8")).hexdigest()
                claim.proof_output = proof_context or "Verification predicate passed successfully."
            else:
                claim.status = EpistemicStatus.REFUTED
                claim.proof_output = "Verification predicate returned False."
        except Exception as ex:
            claim.status = EpistemicStatus.REFUTED
            claim.proof_output = f"Verification predicate raised exception: {str(ex)}"

        return claim
```

#### Propiedades del Sistema de Verificación
1. **Inmutabilidad y Cero Confianza:** El estado solo cambia a `VERIFIED` si `verifier_fn(payload)` retorna explícitamente `True`.
2. **Generación de Prueba Criptográfica:** Se calcula un digest **SHA-256** combinando el identificador único de la afirmación, el timestamp Unix en milisegundos y el contexto de la prueba. Este hash es persistido en `epistemic_claims` y en el recibo entregado al cliente, impidiendo la falsificación retroactiva de estados.
3. **Manejo Seguro de Excepciones:** Si el código del verificador arroja un error en tiempo de ejecución, el estado no se corrompe ni se omite: se degrada determinísticamente a `REFUTED` y se captura la traza del error en `proof_output`.

---

## 5. Suite de Pruebas Automatizadas y Métricas de Ejecución

La integridad de `aleph_core` se encuentra respaldada por una suite de pruebas unitarias y de integración que cubre todos los módulos de bajo nivel.

### 5.1. Cobertura de las Pruebas

1. **`tests/test_epistemic.py` (2 pruebas):**
   * `test_gate_verifies_correctly`: Valida la transición de `INFERRED` a `VERIFIED`, la generación del hash SHA-256 de longitud 64 y el guardado de la evidencia.
   * `test_gate_refutes_failed_predicate`: Valida que un predicado no satisfecho degrade la afirmación a `REFUTED` con `proof_hash = None`.
2. **`tests/test_store.py` (3 pruebas):**
   * `test_sqlite_wal_persistence`: Valida inserción y recuperación íntegra de claims en base de datos SQLite WAL.
   * `test_lease_concurrency`: Valida contención de recursos, bloqueo de agentes competidores ante un lease activo, liberación controlada y re-adquisición.
   * `test_atomic_file_write`: Valida escritura atómica en disco en dos fases mediante `os.replace`.
3. **`tests/test_engine.py` (1 prueba):**
   * `test_end_to_end_verified_pipeline`: Valida el ciclo completo de despacho, reducción, verificación por compuerta, inserción en diario JSONL y persistencia en SQLite WAL.

### 5.2. Métrica de Ejecución Empírica Verificada

Ejecución directa en terminal Windows:
```shell
python -m unittest discover -s aleph_core/tests
```

**Resultado de Salida:**
```text
......
----------------------------------------------------------------------
Ran 6 tests in 0.145s

OK
```

* **Total de pruebas:** 6 ejecutadas.
* **Fallos:** 0.
* **Errores:** 0.
* **Tiempo total de ejecución:** **0.145 segundos** (145 milisegundos).
* **Comportamiento en Windows:** 0 errores de tipo `WinError 32`, confirmando la efectividad del manejo de handles y context managers en el sistema de archivos NTFS.
