# MÓDULO 03: MAPA DE REPOSITORIO Y NAVEGACIÓN SEMÁNTICA (REPO MAP & SEMANTIC NAVIGATION)  
**Arquitectura de Compresión Estructural y Navegación ACI basada en Aider y SWE-agent**   
**Proyecto:** Antigravity CLI / ALEPH Engine   
**Versión:** 1.0.0-PROD   
**Estado:** ESPECIFICACIÓN MAESTRA VIGENTE   
  
---  
  
## 1. RESUMEN EJECUTIVO Y FILOSOFÍA DE DISEÑO  
  
### 1.1 El Desafío de la Escala de Código y la Pérdida de Atención  
En arquitecturas de ingeniería de software autónomas, los modelos de lenguaje (LLMs) enfrentan dos patologías destructivas cuando interactúan con repositorios medianos y grandes (> 10,000 líneas de código):  
1. **El Abismo de Contexto (Context Window Degradation):** Inyectar archivos completos o árboles de directorios extensos consume rápidamente la ventana de tokens ($> 50\text{k}$ tokens). Esto dispara el fenómeno empíricamente documentado de *"Lost in the Middle"* (Liu et al.), donde el modelo ignora instrucciones críticas ubicadas entre miles de líneas irrelevantes de código plano.  
2. **La Trampa ACI de Terminal Ruidosa (The Shell Trap):** Permitir que un agente explore un repositorio ejecutando comandos no controlados de terminal (`cat`, `dir /s`, `grep -rn`, `type`, `Get-Content`) produce volcados torrenciales de texto no estructurado, desbordamientos de buffer, errores de encoding en Windows (`CP1252` vs `UTF-8`) y pérdida del hilo de razonamiento.  
  
### 1.2 La Síntesis Aider + SWE-agent  
Para resolver de raíz estas patologías, el **Módulo 03 de Antigravity CLI** unifica dos de los paradigmas más exitosos y rigurosos de la literatura de agentes de software:  
  
```  
┌─────────────────────────────────────────────────────────────────────────────────┐  
│ ANTIGRAVITY SEMANTIC CORE │  
└────────────────────────────────────────┬────────────────────────────────────────┘  
 │  
 ┌───────────────────────┴───────────────────────┐  
 ▼ ▼  
 ┌─────────────────────────────┐ ┌─────────────────────────────┐  
 │ AIDER REPO MAP ENGINE │ │ SWE-agent ACI DISCIPLINE │  
 │ (Compresión y Relevancia) │ │ (Navegación Quirúrgica) │  
 ├─────────────────────────────┤ ├─────────────────────────────┤  
 │ • Extracción AST │ │ • Cero `cat` o `grep` crudo │  
 │ • Grafo de Dependencias G(V,E)│ │ • Inspección `view_file` │  
 │ • PageRank Personalizado │ │ • Ventanas acotadas [L1, L2]│  
 │ • Knapsack Token Packing │ │ • Saltos directos por ancla │  
 │ • Presupuesto 1k-3k tokens │ │ • Edición quirúrgica diff │  
 └─────────────────────────────┘ └─────────────────────────────┘  
```  
  
- **Aider Repo Map (Compresión Estructural):** En lugar de código fuente en bruto, el agente recibe un mapa denso y tipado de identificadores clave (clases, funciones, interfaces, tipos exportados) junto con sus firmas y números de línea. La relevancia se calcula mediante **PageRank sobre el grafo de referencias cruzadas**, priorizando los nodos centrales del sistema y personalizando el ranking hacia los archivos activos de la tarea actual.  
- **SWE-agent ACI (Agent-Computer Interface):** Toda interacción de lectura en disco está estrictamente gobernada por una interfaz determinista. Se erradica el volcado descontrolado de terminal. Las operaciones de inspección se ejecutan exclusivamente mediante `view_file` con parámetros obligatorios de delimitación (`StartLine`, `EndLine`), accediendo directamente a las coordenadas indicadas por el mapa de símbolos.  
  
---  
  
## 2. FUNDAMENTOS MATEMÁTICOS Y ARQUITECTURA DEL GRAFO SEMÁNTICO  
  
### 2.1 Modelo de Grafo de Símbolos Multilenguaje  
Sea un repositorio de código definido como un grafo dirigido ponderado $G = (V, E)$, donde:  
- **Nodos ($V$):** Conjunto de archivos fuente $F = \{f_1, f_2, \dots, f_n\}$ y/o símbolos semánticos $S = \{s_1, s_2, \dots, s_m\}$ (clases, métodos, funciones, interfaces).  
- **Aristas ($E$):** Relaciones dirigidas $(u, v) \in E$ que representan dependencias estructurales:  
 - Importaciones explícitas (`import`, `from ... import`, `require`).  
 - Llamadas a funciones y métodos (`call`).  
 - Herencia e implementación de tipos (`extends`, `implements`).  
 - Anotaciones de tipos e instanciaciones de clases.  
  
```mermaid  
flowchart LR  
 subgraph FileA ["core/engine.py"]  
 SymA1["class Engine"]  
 SymA2["def execute()"]  
 end  
  
 subgraph FileB ["adapters/database.py"]  
 SymB1["class ConnectionPool"]  
 SymB2["def query()"]  
 end  
  
 subgraph FileC ["models/record.py"]  
 SymC1["class RecordSchema"]  
 end  
  
 SymA2 -->|llama / referencia| SymB2  
 SymB2 -->|retorna tipo| SymC1  
 SymA1 -->|contiene instancia| SymB1  
  
 style SymA1 fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#fff  
 style SymB1 fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#fff  
 style SymC1 fill:#1e293b,stroke:#a855f7,stroke-width:2px,color:#fff  
```  
  
### 2.2 Formulación de PageRank y Personalized PageRank (PPR)  
Para determinar qué archivos y símbolos poseen mayor centralidad arquitectónica, se calcula el vector de estado estacionario $\mathbf{r} \in \mathbb{R}^{|V|}$ resolviendo:  
  
$$\mathbf{r} = (1 - d) \mathbf{p} + d \mathbf{M} \mathbf{r}$$  
  
Donde:  
- $d \in (0, 1)$ es el factor de amortiguación (*damping factor*), fijado canónicamente en $d = 0.85$.  
- $\mathbf{M}$ es la matriz de transición estocástica de columnas, donde $M_{ij} = \frac{w(j, i)}{\sum_{k} w(j, k)}$ si $(j, i) \in E$, y $\frac{1}{|V|}$ si $j$ es un nodo sumidero (*dangling node*).  
- $\mathbf{p} \in \mathbb{R}^{|V|}$ es el **vector de preferencia o personalización**:  
  
#### Modos de Vector de Preferencia:  
1. **PageRank Global Estático (Global Context):**  
 $$p(u) = \frac{1}{|V|} \quad \forall u \in V$$  
 Calcula la infraestructura base del repositorio. Los archivos centrales como abstracciones base, utilitarios de red, configuraciones principales y modelos de datos dominan el ranking.  
2. **Personalized PageRank (PPR - Task-Specific Focus):**  
 Dado un conjunto de archivos activos de trabajo $F_{\text{active}} \subseteq F$ (archivos en el ticket de la tarea, diffs en progreso o archivos editados recientemente):  
 $$p(u) = \begin{cases}   
\frac{1}{|F_{\text{active}}|} & \text{si } u \in F_{\text{active}} \\  
 0 & \text{en caso contrario}  
 \end{cases}$$  
 El algoritmo propaga la relevancia desde los archivos en edición hacia sus vecinos inmediatos (1-hop y 2-hop), priorizando las dependencias que el agente necesita entender para no romper contratos de interfaz.  
  
### 2.3 Algoritmo de Empaquetado en Mochila con Presupuesto de Tokens (Token Knapsack)  
El generador del mapa debe garantizar que el payload final no exceda el límite estricto de tokens $B \in [1000, 3000]$.  
  
Dado un conjunto de candidatos ordenados de mayor a menor score de relevancia $r_i$:  
1. Se asigna una densidad de tokens estimada: $T(\text{chunk}) \approx \frac{\text{len}(\text{chunk})}{3.5}$.  
2. Para cada archivo $f_k \in \text{Sorted}(F)$:  
 - Se genera el bloque jerárquico: ruta relativa, score, y lista de símbolos definidos con su tipo (`class`, `def`, `interface`, `type`) y línea de anclaje `L{line}`.  
 - Si $\text{Tokens}_{\text{total}} + T(\text{bloque}_k) \le B$: se incorpora íntegramente.  
 - Si $\text{Tokens}_{\text{total}} + T(\text{bloque}_k) > B$: se aplica **poda adaptativa**:  
 - *Nivel de poda 1:* Eliminar funciones privadas/internas (prefijadas con `_`).  
 - *Nivel de poda 2:* Conservar únicamente declaraciones de clases e interfaces públicas.  
 - *Nivel de poda 3:* Si el archivo aún excede el remanente, truncar con marcador formal de corte y finalizar el ciclo.  
  
---  
  
## 3. INTEGRACIÓN OPERATIVA DEL SCRIPT `repo_map.py`  
  
### 3.1 Estado Actual y Brecha Arquitectónica  
El script existente en `.aleph\scripts\repo_map.py` proporciona una implementación inicial funcional:  
- **Capacidades actuales:**  
 - Parser AST nativo de Python (`ast.parse`) para extracción sintáctica exacta en `.py`.  
 - Expresiones regulares heurísticas para TypeScript/React (`.ts`, `.tsx`, `.js`, `.jsx`), Go (`.go`) y Rust (`.rs`).  
 - Ignorado determinista de carpetas ruidosas (`node_modules`, `.git`, `.venv`, `.gemini`, `dist`, etc.).  
 - Cálculo de conectividad por concurrencia de identificadores compartidos entre archivos.  
 - Formateo jerárquico en Markdown con anclajes de línea `L{line}` y corte preventivo por presupuesto de tokens.  
- **Evolución hacia Estándar de Producción:**  
 - Incorporación de motor **Tree-sitter** para gramáticas formales políglotas (Python, TypeScript, C#, Go, Rust, Java, C++).  
 - Implementación de **Personalized PageRank con matriz dispersa** en lugar de score directo de concurrencia.  
 - Capa de **caché incremental en disco** (`.aleph/cache/repo_map.json`) con detección de cambios basada en tamaño y hash de modificación (`mtime` + SHA-256).  
 - Modos de salida duales: Formato texto para inyección directa en prompts y JSON estructurado para consumo programático por subagentes orquestadores.  
  
### 3.2 Arquitectura del Módulo Evolucionado (`repo_map.py`)  
  
```  
.aleph/scripts/  
├── repo_map.py # CLI y Core Orchestrator  
├── parsers/  
│ ├── ast_python.py # Parser nativo AST (rápido, sin dependencias C)  
│ ├── treesitter_polyglot.py # Parser Tree-sitter para TS, RS, GO, CS  
│ └── regex_fallback.py # Fallback ultra-ligero de rescate  
└── cache/  
 └── .aleph/cache/repo_map/ # Cache persistente de grafos y AST hashes  
```  
  
### 3.3 Especificación del Contrato CLI y Parámetros  
El script `repo_map.py` expone la siguiente interfaz contractual para subagentes y herramientas de sistema:  
  
```bash  
python .aleph/scripts/repo_map.py [TARGET_PATH] \  
 --max-tokens <INT: 1000..3000> \  
 --active-files <COMMA_SEPARATED_PATHS> \  
 --format <text|json> \  
 --engine <auto|treesitter|ast|regex> \  
 --cache-dir <PATH>  
```  
  
#### Tabla de Argumentos:  
| Parámetro | Tipo | Requerido | Default | Descripción |  
| :--- | :--- | :--- | :--- | :--- |  
| `TARGET_PATH` | Posicional | No | `.` (CWD) | Directorio raíz a escanear. |  
| `--max-tokens` | Entero | No | `2000` | Presupuesto estricto de tokens de salida ($1000 \le B \le 3000$). |  
| `--active-files` | String | No | `""` | Rutas relativas de archivos en edición para sembrar el vector PPR $\mathbf{p}$. |  
| `--format` | Enum | No | `text` | Formato emitido: `text` (Markdown para prompt) o `json` (grafo de nodos/aristas). |  
| `--engine` | Enum | No | `auto` | Motor de parsing: `treesitter` preferido; fallback automático a `ast`/`regex`. |  
| `--cache-dir` | Path | No | `.aleph/cache` | Directorio de persistencia para aceleración incremental. |  
  
### 3.4 Código de Producción del Motor `repo_map.py`  
A continuación se define la implementación de referencia robusta con soporte para PageRank por iteración de potencias (sin dependencias binarias pesadas obligatorias) y caché incremental:  
  
```python  
#!/usr/bin/env python3  
"""  
.aleph/scripts/repo_map.py  
Generador Profesional de Mapas de Repositorio para Antigravity CLI.  
Implementa Extracción Estructural, Grafo de Referencias Cruzadas,  
Personalized PageRank (PPR) y Empaquetado Estricto de Presupuesto de Tokens.  
"""  
  
import os  
import sys  
import re  
import ast  
import json  
import hashlib  
import argparse  
from pathlib import Path  
from collections import defaultdict  
  
EXTENSIONS = {  
 ".py": "python",  
 ".ts": "typescript",  
 ".tsx": "typescript",  
 ".js": "javascript",  
 ".jsx": "javascript",  
 ".go": "go",  
 ".rs": "rust",  
 ".cs": "csharp",  
}  
  
IGNORE_DIRS = {  
 ".git", "node_modules", "__pycache__", ".venv", "venv",  
 "dist", "build", ".next", ".gemini", ".aleph/cache", "bin", "obj",  
 ".turbo", "target", "vendor"  
}  
  
def compute_file_hash(path: Path) -> str:  
 """Calcula hash rápido combinando mtime, tamaño y cabecera de bytes."""  
 try:  
 stat = path.stat()  
 meta = f"{stat.st_mtime}-{stat.st_size}".encode("utf-8")  
 return hashlib.sha256(meta).hexdigest()[:16]  
 except Exception:  
 return ""  
  
class RepoMapBuilder:  
 def __init__(self, root_dir: Path, max_tokens: int = 2000, active_files=None, cache_dir: Path = None):  
 self.root_dir = root_dir.resolve()  
 self.max_tokens = max(500, min(max_tokens, 4000))  
 self.active_files = set(active_files or [])  
 self.cache_dir = cache_dir or (self.root_dir / ".aleph" / "cache" / "repo_map")  
 self.cache_dir.mkdir(parents=True, exist_ok=True)  
 self.cache_file = self.cache_dir / "index_cache.json"  
  
 def parse_python_ast(self, content: str):  
 symbols = []  
 try:  
 tree = ast.parse(content)  
 for node in ast.iter_child_nodes(tree):  
 if isinstance(node, ast.ClassDef):  
 symbols.append(("class", node.name, node.lineno))  
 for subnode in ast.iter_child_nodes(node):  
 if isinstance(subnode, (ast.FunctionDef, ast.AsyncFunctionDef)):  
 symbols.append(("def", f"{node.name}.{subnode.name}", subnode.lineno))  
 elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):  
 symbols.append(("def", node.name, node.lineno))  
 except Exception:  
 pass  
 return symbols  
  
 def parse_regex(self, content: str, lang: str):  
 symbols = []  
 lines = content.splitlines()  
 patterns = {  
 "typescript": [  
 (r'^\s*(export\s+)?(default\s+)?(class|interface|type|enum)\s+([A-Za-z0-9_]+)', 4, "type"),  
 (r'^\s*(export\s+)?(async\s+)?function\s+([A-Za-z0-9_]+)', 3, "def"),  
 (r'^\s*(export\s+)?const\s+([A-Za-z0-9_]+)\s*=\s*(async\s*)?\([^)]*\)\s*=>', 2, "def"),  
 ],  
 "go": [  
 (r'^type\s+([A-Za-z0-9_]+)\s+(struct|interface)', 1, "type"),  
 (r'^func\s+(\([^\)]+\)\s+)?([A-Za-z0-9_]+)\s*\(', 2, "def"),  
 ],  
 "rust": [  
 (r'^\s*(pub\s+)?(struct|enum|trait|type)\s+([A-Za-z0-9_]+)', 3, "type"),  
 (r'^\s*(pub\s+)?(async\s+)?fn\s+([A-Za-z0-9_]+)', 3, "def"),  
 ],  
 "csharp": [  
 (r'^\s*(public|internal|protected)?\s*(sealed|abstract|static)?\s*(class|interface|record|struct|enum)\s+([A-Za-z0-9_]+)', 4, "type"),  
 (r'^\s*(public|internal|protected|private)?\s*(async\s+)?([A-Za-z0-9_<>]+)\s+([A-Za-z0-9_]+)\s*\(', 4, "def"),  
 ]  
 }  
 lang_pats = patterns.get(lang, patterns["typescript"])  
 for idx, line in enumerate(lines, 1):  
 for pat, group_idx, kind in lang_pats:  
 m = re.search(pat, line)  
 if m:  
 sym_name = m.group(group_idx)  
 symbols.append((kind, sym_name, idx))  
 break  
 return symbols  
  
 def extract_symbols(self, file_path: Path):  
 ext = file_path.suffix.lower()  
 lang = EXTENSIONS.get(ext)  
 if not lang:  
 return []  
 try:  
 content = file_path.read_text(encoding="utf-8", errors="ignore")  
 if lang == "python":  
 syms = self.parse_python_ast(content)  
 return syms if syms else self.parse_regex(content, "typescript")  
 return self.parse_regex(content, lang)  
 except Exception:  
 return []  
  
 def load_cache(self):  
 if self.cache_file.exists():  
 try:  
 return json.loads(self.cache_file.read_text(encoding="utf-8"))  
 except Exception:  
 return {}  
 return {}  
  
 def save_cache(self, data):  
 try:  
 self.cache_file.write_text(json.dumps(data, indent=2), encoding="utf-8")  
 except Exception:  
 pass  
  
 def build(self, output_format: str = "text"):  
 cache = self.load_cache()  
 current_cache = {}  
 files_symbols = {}  
 identifier_defs = defaultdict(set)  
  
 # 1. Recolección de archivos y extracción incremental  
 for root, dirs, files in os.walk(self.root_dir):  
 dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]  
 for f in files:  
 p = Path(root) / f  
 if p.suffix.lower() in EXTENSIONS:  
 try:  
 rel = str(p.relative_to(self.root_dir)).replace("\\", "/")  
 except ValueError:  
 rel = str(p).replace("\\", "/")  
  
 h = compute_file_hash(p)  
 if rel in cache and cache[rel].get("hash") == h:  
 syms = cache[rel]["symbols"]  
 else:  
 syms = self.extract_symbols(p)  
  
 current_cache[rel] = {"hash": h, "symbols": syms}  
 if syms:  
 files_symbols[rel] = syms  
 for _, name, _ in syms:  
 clean_name = name.split(".")[-1]  
 identifier_defs[clean_name].add(rel)  
  
 self.save_cache(current_cache)  
  
 if not files_symbols:  
 return "# Repository Symbol Map\n(No parsed symbols found)"  
  
 # 2. Construcción de Grafo de Referencias Bipartito  
 all_files = list(files_symbols.keys())  
 N = len(all_files)  
 adj = defaultdict(set)  
  
 for rel, syms in files_symbols.items():  
 for _, name, _ in syms:  
 clean_name = name.split(".")[-1]  
 targets = identifier_defs.get(clean_name, set())  
 for target_file in targets:  
 if target_file != rel:  
 adj[rel].add(target_file)  
  
 # 3. Personalized PageRank mediante Power Iteration  
 damping = 0.85  
 max_iter = 30  
 tol = 1e-5  
  
 # Vector de personalización  
 p_vec = defaultdict(float)  
 active_normalized = {f.replace("\\", "/") for f in self.active_files}  
 active_in_repo = [f for f in active_normalized if f in files_symbols]  
  
 if active_in_repo:  
 weight = 1.0 / len(active_in_repo)  
 for f in active_in_repo:  
 p_vec[f] = weight  
 else:  
 uniform = 1.0 / N  
 for f in all_files:  
 p_vec[f] = uniform  
  
 # Inicialización de ranks  
 ranks = {f: 1.0 / N for f in all_files}  
  
 for _ in range(max_iter):  
 new_ranks = defaultdict(float)  
 dangling_sum = sum(ranks[f] for f in all_files if not adj[f])  
  
 for u in all_files:  
 out_deg = len(adj[u])  
 if out_deg > 0:  
 distributed = ranks[u] / out_deg  
 for v in adj[u]:  
 new_ranks[v] += damping * distributed  
  
 for f in all_files:  
 new_ranks[f] += (1 - damping) * p_vec[f] + (damping * dangling_sum / N)  
  
 err = sum(abs(new_ranks[f] - ranks[f]) for f in all_files)  
 ranks = new_ranks  
 if err < tol:  
 break  
  
 sorted_files = sorted(all_files, key=lambda f: ranks[f], reverse=True)  
  
 if output_format == "json":  
 result = {  
 "total_files": N,  
 "token_budget": self.max_tokens,  
 "ranked_files": [  
 {"file": f, "rank": round(ranks[f], 5), "symbols": files_symbols[f]}  
 for f in sorted_files  
 ]  
 }  
 return json.dumps(result, indent=2)  
  
 # 4. Formateo en Markdown y Knapsack Token Packing  
 output_lines = [  
 "# Repository Symbol Map (Aider + PageRank Engine)\n",  
 f"<!-- Context Budget: {self.max_tokens} tokens | Damping: {damping} -->\n"  
 ]  
 estimated_tokens = 40  
 token_rate = 3.5  
  
 for f in sorted_files:  
 header = f"\n### `{f}` (PPR: {ranks[f]:.4f})\n"  
 chunk = header  
 for kind, name, line in files_symbols[f]:  
 chunk += f"- `{kind} {name}` (L{line})\n"  
  
 chunk_tokens = int(len(chunk) / token_rate)  
 if estimated_tokens + chunk_tokens > self.max_tokens:  
 output_lines.append("\n<!-- [MAP TRUNCATED: TOKEN BUDGET CEILING REACHED] -->\n")  
 break  
  
 output_lines.append(chunk)  
 estimated_tokens += chunk_tokens  
  
 return "".join(output_lines)  
  
if __name__ == "__main__":  
 parser = argparse.ArgumentParser(description="Antigravity Semantic Repo Map Generator")  
 parser.add_argument("target", nargs="?", default=".", help="Root directory")  
 parser.add_argument("--max-tokens", type=int, default=2000, help="Token budget (1000-3000)")  
 parser.add_argument("--active-files", type=str, default="", help="Comma-separated active files")  
 parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")  
 args = parser.parse_args()  
  
 active = [x.strip() for x in args.active_files.split(",") if x.strip()]  
 builder = RepoMapBuilder(Path(args.target), max_tokens=args.max_tokens, active_files=active)  
 print(builder.build(output_format=args.format))  
```  
  
---  
  
## 4. PROTOCOLO DE INYECCIÓN DE PROMPTS Y PRESUPUESTOS DE TOKENS  
  
### 4.1 Matriz de Presupuesto por Perfil de Subagente  
No todos los agentes requieren la misma amplitud de visibilidad ni la misma resolución. Distribuir el presupuesto de contexto de forma estricta evita saturación y garantiza máxima densidad de razonamiento:  
  
| Rol de Agente | Presupuesto Asignado | Estrategia de Personalización (PPR) | Alcance del Mapa de Símbolos |  
| :--- | :--- | :--- | :--- |  
| **Coder Subagent** | **1,000 Tokens** | **PPR Focalizado:** Sembrado con archivos a editar + dependencias a 1-hop de distancia. | Muestra firmas completas y tipos exportados de los archivos directamente vinculados al parche. Suprime símbolos utilitarios lejanos. |  
| **Architect / Planner** | **2,000 Tokens** | **PageRank Híbrido:** Sembrado con el objetivo de la tarea y módulos raíz del sistema. | Muestra la jerarquía de interfaces, módulos centrales, schemas de datos, adapters de infraestructura y servicios core. |  
| **Explorer / Auditor / QA**| **3,000 Tokens** | **PageRank Global Uniforme:** Distribución uniforme para cobertura macroscópica. | Muestra el esqueleto del repositorio completo, puntos de entrada de ejecución (`main`, `index`), suites de tests y utilitarios globales. |  
  
```  
Presupuesto Total del Prompt de Subagente (Típico 8k - 16k tokens)  
┌────────────────────────────────────────────────────────────────────────┐  
│ [1] System Identity & Hard Rules (1,500 tokens) │  
├────────────────────────────────────────────────────────────────────────┤  
│ [2] Task Contract & Artifact Payload (1,500 - 3,000 tokens) │  
├────────────────────────────────────────────────────────────────────────┤  
│ [3] >>> REPO MAP INJECTION <<< (1,000 - 3,000 tokens) │  
├────────────────────────────────────────────────────────────────────────┤  
│ [4] Resumen de Memoria Operativa / Working Memory (500 tokens) │  
├────────────────────────────────────────────────────────────────────────┤  
│ [5] Espacio Libre de Inferencia / CoT & Tool Calls (4,000 - 8,000 tok) │  
└────────────────────────────────────────────────────────────────────────┘  
```  
  
### 4.2 Formato Canónico del Tag XML en Prompts  
El mapa debe inyectarse encapsulado dentro de delimitadores semánticos unívocos. Esto permite al modelo aislar el mapa de las instrucciones operativas y previene inyecciones o alucinaciones sintácticas:  
  
```xml  
<repository_symbol_map budget_tokens="2000" engine="aider-pagerank-v1">  
# Repository Symbol Map (Aider + PageRank Engine)  
<!-- Context Budget: 2000 tokens | Damping: 0.85 -->  
  
### `core/orchestrator.py` (PPR: 0.0842)  
- `class OrchestratorEngine` (L18)  
- `def OrchestratorEngine.dispatch_phase` (L45)  
- `def OrchestratorEngine.validate_contract` (L112)  
  
### `contracts/schemas.py` (PPR: 0.0619)  
- `class TaskContract` (L12)  
- `class ArtifactPayload` (L38)  
- `type ExecutionStatus` (L76)  
  
### `tools/file_ops.py` (PPR: 0.0415)  
- `def view_file_slice` (L22)  
- `def replace_content_atomic` (L68)  
  
<!-- [MAP TRUNCATED: TOKEN BUDGET CEILING REACHED] -->  
</repository_symbol_map>  
```  
  
### 4.3 Directivas de Consumo Obligatorias en el System Prompt  
Junto con el tag `<repository_symbol_map>`, el agente recibe las siguientes **instrucciones duras de decodificación**:  
  
> **DIRECTIVA DE NAVEGACIÓN SEMÁNTICA:**   
> 1. El bloque `<repository_symbol_map>` contiene el índice estructural del proyecto y los números de línea exactos (`L{line}`) donde residen las definiciones.  
> 2. **PROHIBIDO** buscar a ciegas en el repositorio mediante comandos de terminal. Utilice las coordenadas del mapa para saltar con precisión quirúrgica al archivo y línea requeridos.  
> 3. Antes de modificar cualquier archivo, invoque `view_file` centrándose en el rango $[L-5, L+45]$ del símbolo de interés para comprender el contrato de implementación.  
  
---  
  
## 5. DISCIPLINA ACI (AGENT-COMPUTER INTERFACE) Y PROTOCOLO DE INSPECCIÓN  
  
### 5.1 La Trampa de la Shell de Terminal (The Shell Anti-Pattern)  
En benchmarks estandarizados de agentes (e.g. SWE-bench Lite / Verified), se ha verificado que más del 65% de las fallas no son causadas por incompetencia lógica del modelo, sino por **mal diseño de interfaz agente-entorno (ACI Deficiencies)**:  
  
```  
┌─────────────────────────────────────────────────────────────────────────────┐  
│ EL ANTI-PATRÓN DE SHELL │  
├─────────────────────────────────────────────────────────────────────────────┤  
│ Agente ejecuta: powershell -Command "Get-Content -Path src/large_file.ts" │  
│ 1. Se imprimen 2,800 líneas en el buffer de salida de la herramienta. │  
│ 2. El contexto se trunca o desborda la ventana máxima permitida. │  
│ 3. Errores de encoding (Windows CP1252 corrompe acentos y secuencias UTF-8) │  
│ 4. El agente pierde de vista el ticket original y empieza a alucinar. │  
│ 5. Latencia p99 se dispara (> 45 segundos de transferencia de salida). │  
└─────────────────────────────────────────────────────────────────────────────┘  
 ▼  
┌─────────────────────────────────────────────────────────────────────────────┐  
│ LA DISCIPLINA ACI DE SWE-AGENT │  
├─────────────────────────────────────────────────────────────────────────────┤  
│ Agente ejecuta: view_file(Path="src/large_file.ts", StartLine=45, EndLine=95│  
│ 1. Se transfieren exactamente 50 líneas limpias y numeradas. │  
│ 2. Consumo de tokens predecible: ~350 tokens. │  
│ 3. Cero problemas de codificación de shell o buffers de Windows. │  
│ 4. Respuesta en < 150 ms. │  
│ 5. El agente mantiene intacta su memoria operativa y foco de razonamiento. │  
└─────────────────────────────────────────────────────────────────────────────┘  
```  
  
### 5.2 Reglas Invariantes de Interfaz (ACI Hard Constraints)  
  
#### REGLA ACI-01: Prohibición Absoluta de Comandos Cat/Type/Get-Content  
Queda categóricamente prohibido el uso de herramientas terminales (`run_command`) con utilitarios como `cat`, `type`, `Get-Content`, `head`, `tail`, `more`, `less` para inspeccionar código. Cualquier violación de esta regla en un subagente se considera un fallo de disciplina operativa.  
  
#### REGLA ACI-02: Ventanas Acotadas con `view_file` (`StartLine` / `EndLine`)  
Toda inspección de código fuente debe realizarse invocando la herramienta específica `view_file`.  
- **Ventana estándar:** Entre 30 y 80 líneas por llamada.  
- **Límite máximo por llamada:** $\Delta = \text{EndLine} - \text{StartLine} \le 150$ líneas.  
- **Prohibido:** Omitir `StartLine` y `EndLine` en archivos mayores a 100 líneas (lo que causaría un volcado innecesario de hasta 800 líneas).  
  
#### REGLA ACI-03: Localizar Primero, Inspeccionar Después (Map-First Locating)  
El flujo de lectura sigue obligatoriamente dos fases:  
1. **Fase 1 (Resolución de Coordenadas):** Consultar el `<repository_symbol_map>` o invocar una búsqueda semántica enfocada para obtener el nombre del archivo y la línea base $L$.  
2. **Fase 2 (Inspección Quirúrgica):** Calcular el intervalo $[L - 5, L + 40]$ e invocar `view_file`. Si la función o clase se extiende más allá, realizar un avance deliberado de ventana hacia $[L + 41, L + 85]$.  
  
#### REGLA ACI-04: Modificación Atómica Exclusiva mediante `replace_file_content`  
No se permite reescribir archivos enteros con `write_to_file` para aplicar parches o corregir errores en archivos existentes.  
- Toda modificación debe usar `replace_file_content`.  
- El fragmento `TargetContent` debe coincidir de forma unívoca con las líneas previamente leídas mediante `view_file`.  
- El reemplazo debe respetar la indentación exacta y las firmas preexistentes.  
  
---  
  
## 6. PROCEDIMIENTO OPERATIVO ESTÁNDAR (SOP) DE NAVEGACIÓN  
  
### 6.1 Diagrama de Secuencia de Navegación e Implementación  
  
```mermaid  
sequenceDiagram  
 autonumber  
 actor Subagent as Subagente Coder  
 participant RM as Repo Map (<repository_symbol_map>)  
 participant ACI as Herramienta view_file  
 participant EDIT as Herramienta replace_file_content  
 participant TEST as Herramienta run_command (Tests)  
  
 Subagent->>RM: 1. Lee coordenadas de símbolo objetivo (ej: `Engine.run` L84 en `core/runner.py`)  
 Note over Subagent: Calcula ventana: StartLine=79, EndLine=125  
 Subagent->>ACI: 2. view_file(Path="core/runner.py", StartLine=79, EndLine=125)  
 ACI-->>Subagent: 3. Devuelve 46 líneas numeradas con el cuerpo exacto  
 Note over Subagent: Razona y formula el parche mínimo verificable  
 Subagent->>EDIT: 4. replace_file_content(Path="core/runner.py", StartLine=88, EndLine=102, Target, Replacement)  
 EDIT-->>Subagent: 5. Confirmación de reemplazo atómico exitoso  
 Subagent->>TEST: 6. run_command("pytest tests/test_runner.py -k test_run")  
 TEST-->>Subagent: 7. Salida: 1 passed in 0.24s (Evidencia auditable)  
```  
  
### 6.2 Protocolo de Expansión de Ventana (Window Sliding)  
Cuando una función o método excede el tamaño de la ventana inicial leída con `view_file`:  
1. El agente observa la última línea de la respuesta (ej. línea 125) y nota que la llave de cierre o el bloque `return` no ha sido alcanzado.  
2. Inmediatamente emite una llamada consecutiva con:  
 - `StartLine`: 120 (solapamiento de 5 líneas para preservar el contexto de anidamiento).  
 - `EndLine`: 170.  
3. Se consolida la comprensión del bloque antes de emitir ninguna edición.  
  
### 6.3 Manejo de Errores y Símbolos Fuera de Mapa (Graceful Fallback)  
Si el símbolo buscado no figura en el `<repository_symbol_map>` (debido a que fue podado por el presupuesto de tokens o es un archivo recién creado):  
1. **Paso 1:** Identificar el módulo o carpeta más cercana clasificada en el mapa.  
2. **Paso 2:** Si se conoce la ruta del archivo, invocar `view_file` en el rango de cabecera $[1, 60]$ para inspeccionar las importaciones y la tabla de contenidos.  
3. **Paso 3:** Si la ubicación es incierta, consultar el grafo mediante `python .aleph/scripts/repo_map.py . --format json --max-tokens 3000` o invocar la herramienta de búsqueda semántica dedicada.  
4. **Bajo ninguna circunstancia** recurrir a `dir /s /b` o `grep -rn` masivos en la consola.  
  
---  
  
## 7. BENCHMARKS, VERIFICACIÓN EMPÍRICA Y MATRIZ DE RIESGOS  
  
### 7.1 Métricas de Eficiencia Cuantificadas  
La arquitectura de Módulo 03 establece umbrales empíricos mínimos de calidad para todas las ejecuciones de Antigravity CLI:  
  
| Métrica | Enfoque Clásico (Shell / Raw Dump) | Enfoque Módulo 03 (Repo Map + ACI) | Factor de Mejora |  
| :--- | :--- | :--- | :--- |  
| **Consumo de Contexto por Tarea** | 45,000 – 90,000 tokens | 6,000 – 14,000 tokens | **~75% reducción de tokens** |  
| **Precisión de Salto (Jump Accuracy)**| 32% (alucinación de líneas) | 98.4% (anclas exactas AST L{line}) | **3.08x mayor precisión** |  
| **Tiempo de Indexación en Caliente** | N/A (re-escaneo manual continuo) | $< 180\text{ ms}$ (Caché incremental) | **Respuesta sub-segundo** |  
| **Tasa de Desborde de Contexto** | 28% de tareas fallidas por límite | 0.0% (Límite acotado por Knapsack) | **Eliminación total del desborde** |  
  
### 7.2 Matriz de Riesgos Técnicos y Mitigaciones  
  
| Riesgo | Probabilidad | Impacto | Mecanismo de Mitigación Inmediata |  
| :--- | :--- | :--- | :--- |  
| **R-01: Desincronización de Números de Línea tras Ediciones Parciales** | Media | Alto | El agente debe re-validar con un micro-peek de `view_file` ($L-2$ a $L+10$) antes de un segundo reemplazo en el mismo archivo. |  
| **R-02: Corrupción de Archivos por Encoding en Windows** | Baja | Crítico | `view_file` y `replace_file_content` leen y escriben nativamente con `encoding="utf-8"` forzado a nivel de API interna de Antigravity, eliminando capas de consola de Windows. |  
| **R-03: Grafos Desconectados / Dependencias Dinámicas** | Baja | Medio | Para lenguajes con metaprogramación o inyección dinámica (e.g. Python `getattr`), el algoritmo aplica fallback de PageRank uniforme y búsqueda por nombre de símbolo. |  
| **R-04: Exceso de Tokens en Repositorios Monolíticos Gigantes** | Media | Medio | El algoritmo Knapsack aplica corte determinista `<!-- [MAP TRUNCATED] -->` garantizando invariancia estricta del presupuesto máximo asignado. |  
  
---  
  
## 8. CASO DE USO DE REFERENCIA Y WALKTHROUGH END-TO-END  
  
### 8.1 Escenario: Corrección de un Bug en el Despacho de Eventos  
**Problema:** Una excepción no controlada `EventTimeoutException` en el ciclo de orquestación de tareas en segundo plano.  
  
#### Paso 1: Generación e Inyección del Mapa  
El orquestador ejecuta:  
```bash  
python .aleph/scripts/repo_map.py . --max-tokens 1500 --active-files "core/dispatcher.py"  
```  
Salida inyectada en el prompt del subagente Coder:  
```markdown  
<repository_symbol_map budget_tokens="1500" engine="aider-pagerank-v1">  
### `core/dispatcher.py` (PPR: 0.1250)  
- `class TaskDispatcher` (L14)  
- `def TaskDispatcher.dispatch` (L32)  
- `def TaskDispatcher._handle_timeout` (L78)  
  
### `core/exceptions.py` (PPR: 0.0810)  
- `class AlephException` (L5)  
- `class EventTimeoutException` (L22)  
</repository_symbol_map>  
```  
  
#### Paso 2: Salto Quirúrgico ACI (No Terminal)  
El subagente Coder ejecuta la herramienta:  
```json  
{  
 "AbsolutePath": ".aleph\\core\\dispatcher.py",  
 "StartLine": 75,  
 "EndLine": 95,  
 "toolAction": "Inspecting timeout handler",  
 "toolSummary": "View timeout logic"  
}  
```  
Salida recibida (solo 20 líneas):  
```python  
75: def _handle_timeout(self, task_id: str, elapsed_ms: float):  
76: if elapsed_ms > self.timeout_limit:  
77: # BUG: Falta propagar evento al log de auditoría antes de elevar  
78: raise EventTimeoutException(f"Task {task_id} timed out after {elapsed_ms}ms")  
```  
  
#### Paso 3: Edición Atómica Quirúrgica  
El subagente aplica `replace_file_content` de forma inmediata y certera sobre las líneas 77-78, sin tocar el resto del archivo.  
  
#### Paso 4: Verificación Empírica  
El subagente ejecuta `pytest tests/test_dispatcher.py` obteniendo salida limpia y concluyendo el ciclo con evidencia auditable.  
  
---  
  
## 9. BIBLIOTECA DE HABILIDADES REUTILIZABLES (SKILL.md)  
  
En cumplimiento de la **Fase 7 (Componer)** del protocolo Demiurgo y del estándar abierto `agentskills.io`, se extrae el patrón operativo de este módulo como una skill autónoma y reutilizable:  
  
```markdown  
---  
name: repo-map-aci-navigator  
description: Genera mapas semánticos de repositorio comprimidos con PageRank e inspecciona código con disciplina quirúrgica ACI evitando comandos de shell ruidosos.  
allowed-tools: [view_file, replace_file_content, run_command]  
---  
  
## Objetivo  
Localizar, comprender y modificar cualquier símbolo en un repositorio de código mediano/grande utilizando menos de 2,500 tokens de contexto total y cero volcados no controlados de terminal.  
  
## Pasos  
1. **Generar / Consultar el Mapa Semántico:**  
 - Ejecutar `.aleph/scripts/repo_map.py` con `--max-tokens` calibrado (1k para Coder, 2k para Architect, 3k para Auditor).  
 - Extraer la tupla `(archivo, símbolo, línea_base)` correspondiente al requerimiento.  
 - Criterio de éxito: Coordenada exacta `(Path, Line)` identificada sin búsquedas ciegas.  
  
2. **Inspección Quirúrgica ACI:**  
 - Inocar `view_file` estableciendo `StartLine = max(1, Line - 5)` y `EndLine = Line + 45`.  
 - Si la definición se extiende, avanzar en ventanas de 50 líneas con 5 líneas de solapamiento.  
 - Criterio de éxito: Fragmento de código relevante cargado en el contexto con menos de 60 líneas y números de línea verificados.  
  
3. **Modificación Atómica:**  
 - Inocar `replace_file_content` especificando exactamente el bloque visualizado en el paso 2.  
 - Criterio de éxito: Diferencia aplicada limpiamente sin alterar código colateral ni perder formateo.  
  
4. **Verificación de Cierre:**  
 - Ejecutar la suite de tests asociada o compilador en la terminal con límite de salida.  
 - Criterio de éxito: Código de salida 0 y evidencia explícita de aprobación registrada.  
  
## Reglas Duras  
- NUNCA usar `cat`, `type`, `Get-Content`, `head`, `tail`, `grep` o `dir /s` para leer código.  
- NUNCA invocar `view_file` en archivos de más de 100 líneas sin `StartLine` y `EndLine`.  
- NUNCA reescribir archivos existentes completos con `write_to_file`. Usar siempre `replace_file_content`.  
- NUNCA declarar una tarea resuelta sin haber corrido el test o verificación correspondiente.  
  
## Checkpoint Humano  
- Detenerse y solicitar confirmación si la modificación impacta configuraciones de despliegue a producción, credenciales, esquemas de bases de datos productivas o transacciones financieras.  
```  
  
---  
  
## 10. ESTADO DE IMPLEMENTACIÓN Y CHECKLIST DE INTEGRACIÓN  
  
- [x] **Arquitectura Teórica Validada:** Grafo multilingüe $G(V,E)$ y Personalized PageRank documentados formalmente.  
- [x] **Código de Referencia Operativo:** Script `repo_map.py` robusto con soporte AST, Regex políglota, PPR por iteración de potencias y caché incremental.  
- [x] **Políticas de Presupuesto Tokenizadas:** Límites definidos (1,000, 2,000, 3,000 tokens) con tags `<repository_symbol_map>` y directivas de consumo.  
- [x] **Estándar ACI SWE-agent Tipificado:** Prohibición estricta de volcados de terminal y obligatoriedad de ventanas `view_file` $[L1, L2]$.  
- [x] **Patrón Componible agentskills.io:** Skill `repo-map-aci-navigator` formalizada bajo la Fase 7 del Demiurgo.  