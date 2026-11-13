"""
Memoria Bicameral Híbrida y Grafo de Conocimiento (Nivel 3 Superación de ECC Instincts).
Mientras ECC almacena "instincts" difusos con scoring simple, El Aleph v2.0 implementa:
1. Bitácora Algorítmica Determinista: Reglas SI [Contexto] -> ENTONCES [Acción] -> EVITAR [Anti-Patrón]
   con Lazy Filtering por dominio (Código, Doc, Correo, Análisis, General) y detección automática de contradicciones.
2. Grafo de Conocimiento Ligero en SQLite (Nodos + Aristas Ponderadas + Búsqueda Léxica/Semántica BM25-like).
"""
import json
import math
import re
import time
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from aleph_core.state.store import StateStore

@dataclass
class AlgorithmicRule:
    rule_id: str
    category: str          # 'Código', 'Doc', 'Correo', 'Análisis', 'General'
    priority: str          # 'Crítica', 'Alta', 'Media'
    friction_pattern: str
    if_condition: str
    then_action: str
    avoid_anti_pattern: str
    status: str = "Activa" # 'Activa' | 'Obsoleta'
    confidence: float = 0.95
    hit_count: int = 0

    def format_directive(self) -> str:
        return (
            f"[{self.rule_id} | {self.category} | {self.priority}] "
            f"SI {self.if_condition} -> ENTONCES {self.then_action} -> EVITAR {self.avoid_anti_pattern}"
        )

@dataclass
class KnowledgeNode:
    node_id: str
    node_type: str
    title: str
    content: str
    tags: List[str] = field(default_factory=list)
    updated_at: float = field(default_factory=time.time)

class BicameralMemory:
    def __init__(self, store: StateStore):
        self.store = store
        self._seed_sparkos_canonical_rules()

    def _seed_sparkos_canonical_rules(self):
        """Pre-carga las 5 reglas fundacionales de SparkOS_Bitacora_Reglas si la tabla está vacía."""
        existing = self.get_active_rules()
        if existing:
            return
        defaults = [
            AlgorithmicRule(
                rule_id="REG-001",
                category="Código",
                priority="Crítica",
                friction_pattern="Fallos en Excel 2010 (32/64 bits) y binarios Python en máquinas de cliente.",
                if_condition="se desarrolla código VBA para Excel o ejecutables Python (.exe) para clientes como GOAR Diseño",
                then_action="incluir #If VBA7 PtrSafe, constantes numéricas nativas en lugar de mso*, FindFormat.Clear como Sub puro, forzar DMCOLOR_COLOR=2 en winspool.drv con PageSetup.Draft=False y compilar con PyInstaller autónomo",
                avoid_anti_pattern="usar PageSetup.Draft=True, asumir Office 64-bit moderno o requerir dependencias manuales"
            ),
            AlgorithmicRule(
                rule_id="REG-002",
                category="Análisis",
                priority="Crítica",
                friction_pattern="Ruido publicitario en lanzamientos de IA y gasto innecesario en APIs externas.",
                if_condition="se audita un lanzamiento de IA, paper o motor de inferencia",
                then_action="evaluar con Matriz Anti-Hype (0-100 pts, corte <65/100), etiquetar [VERIFICADO-EXTERNO], [AUTO-REPORTADO] o [NO PUBLICADO] e incluir siempre a Gemini 4 Argon ($0.00 USD marginal en Gemini Pro) como Rival #1 de línea base",
                avoid_anti_pattern="interpolar datos no publicados, usar adjetivos vacíos o recomendar APIs pagas cuando Gemini 4 Argon resuelve el flujo a costo marginal cero"
            ),
            AlgorithmicRule(
                rule_id="REG-003",
                category="Doc",
                priority="Alta",
                friction_pattern="Fricción con referentes operativos de Sala y Caja en Codere al recibir solo documentación técnica.",
                if_condition="se genera documentación del sistema codere_venta_de_cartones para stakeholders de Codere",
                then_action="acompañar la especificación técnica (Rust/Postgres/Next.js) con dos desgloses operativos: (1) Validación Funcional de Sala y (2) Relevamiento de Operaciones",
                avoid_anti_pattern="entregar un único documento monolítico de código a interlocutores operativos sin separar validaciones de sala y reglas de caja"
            ),
            AlgorithmicRule(
                rule_id="REG-004",
                category="Doc",
                priority="Alta",
                friction_pattern="Desincronización entre manual de entrenamiento y planilla de seguimiento con fatiga del SNC.",
                if_condition="se diseña o actualiza un protocolo de entrenamiento físico en Google Workspace",
                then_action="mantener paridad sincronizada entre Manual Operativo (Docs) y Logbook (Sheets) con Tempo 3-1-X-1 y semáforo SNC (-40% volumen si sueño <6h o fatiga >=8/10)",
                avoid_anti_pattern="prescribir rutinas fijas sin autorregulación por fatiga alostática"
            ),
            AlgorithmicRule(
                rule_id="REG-005",
                category="Correo",
                priority="Alta",
                friction_pattern="Demora en acceso a entregables en correos a clientes y entregas académicas de EESTN1.",
                if_condition="se redacta un correo de entrega de software, enlaces de Drive o trabajos prácticos de EESTN1",
                then_action="ubicar el enlace verificable en las primeras 2 líneas con guía de máximo 3 pasos en voseo rioplatense y asunto '7mo 4ta Matias Cardozo [y coautor] - [Trabajo/Materia]'",
                avoid_anti_pattern="introducciones protocolares vacías o asuntos genéricos"
            ),
AlgorithmicRule(
    rule_id="REG-006",
    category="Código",
    priority="Crítica",
    friction_pattern="Bucles infinitos deterministas sin mutación de variables de control y bloques except: pass silenciosos.",
    if_condition="se implementa un bucle de control (while/for) o manejo de excepciones en código agéntico",
    then_action="declarar contrato formal de terminación (@loop_variant o mutación verificada en cuerpo), registrar/re-lanzar excepciones y pasar por compuerta AegisShield (AEGIS-005/006)",
    avoid_anti_pattern="bucles while True: pass sin break, evaluar variables que no mutan en el cuerpo o usar bloques except: pass silenciosos"
),
AlgorithmicRule(
    rule_id="REG-007",
    category="General",
    priority="Crítica",
    friction_pattern="Riesgo de conformarse con soluciones heurísticas o locales cuando existe una solución estrictamente superior en el estado del arte.",
    if_condition="se diseña, construye o mejora cualquier componente, algoritmo o arquitectura en El Aleph y proyectos core",
    then_action="ejecutar un Torneo de Optimalidad Global (GlobalOptimalityGate) evaluando las alternativas bajo las 5 perspectivas del Consejo de Guerra e implementar exclusivamente la solución Pareto-Dominante #1 del mundo",
    avoid_anti_pattern="implementar parches subóptimos, heurísticas frágiles o la primera idea que funcione si existe un algoritmo o arquitectura superior"
),
        ]
        for rule in defaults:
            self.upsert_rule(rule)

    def upsert_rule(self, rule: AlgorithmicRule) -> Tuple[str, List[str]]:
        """
        Inserta o actualiza una regla algorítmica.
        Detecta si existe una regla activa en la misma categoría con la misma condición base (`if_condition`),
        marcando la anterior como 'Obsoleta' para evitar contradicciones en la ventana de contexto.
        """
        superseded_ids: List[str] = []
        now = time.time()
        with self.store._connection() as conn:
            rows = conn.execute(
                "SELECT rule_id, if_condition FROM algorithmic_rules WHERE category = ? AND status = 'Activa' AND rule_id != ?",
                (rule.category, rule.rule_id)
            ).fetchall()
            for r in rows:
                # Si comparten >75% de tokens clave en if_condition, marcamos la previa como Obsoleta
                tokens_new = set(re.findall(r"\w{4,}", rule.if_condition.lower()))
                tokens_old = set(re.findall(r"\w{4,}", r["if_condition"].lower()))
                if tokens_new and tokens_old:
                    overlap = len(tokens_new & tokens_old) / max(len(tokens_new | tokens_old), 1)
                    if overlap >= 0.65:
                        conn.execute(
                            "UPDATE algorithmic_rules SET status = 'Obsoleta', updated_at = ? WHERE rule_id = ?",
                            (now, r["rule_id"])
                        )
                        superseded_ids.append(r["rule_id"])

            conn.execute("""
                INSERT OR REPLACE INTO algorithmic_rules
                (rule_id, category, priority, friction_pattern, if_condition, then_action, avoid_anti_pattern, status, confidence, hit_count, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rule.rule_id, rule.category, rule.priority, rule.friction_pattern,
                rule.if_condition, rule.then_action, rule.avoid_anti_pattern,
                rule.status, rule.confidence, rule.hit_count, now, now
            ))
            conn.commit()
        return rule.rule_id, superseded_ids

    def get_active_rules(self, domain_category: Optional[str] = None) -> List[AlgorithmicRule]:
        """
        Lazy Context Filtering (estilo SparkOS cargar-contexto-activo):
        Devuelve únicamente reglas con Estado='Activa' que coincidan con `domain_category`
        o que sean `General` con prioridad `Crítica`.
        """
        with self.store._connection() as conn:
            if domain_category:
                rows = conn.execute("""
                    SELECT * FROM algorithmic_rules
                    WHERE status = 'Activa'
                      AND (category = ? OR (category = 'General' AND priority = 'Crítica'))
                    ORDER BY CASE priority WHEN 'Crítica' THEN 1 WHEN 'Alta' THEN 2 ELSE 3 END, rule_id ASC
                """, (domain_category,)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM algorithmic_rules
                    WHERE status = 'Activa'
                    ORDER BY CASE priority WHEN 'Crítica' THEN 1 WHEN 'Alta' THEN 2 ELSE 3 END, rule_id ASC
                """).fetchall()
            return [
                AlgorithmicRule(
                    rule_id=r["rule_id"],
                    category=r["category"],
                    priority=r["priority"],
                    friction_pattern=r["friction_pattern"],
                    if_condition=r["if_condition"],
                    then_action=r["then_action"],
                    avoid_anti_pattern=r["avoid_anti_pattern"],
                    status=r["status"],
                    confidence=r["confidence"],
                    hit_count=r["hit_count"]
                )
                for r in rows
            ]

    def add_knowledge_node(self, node: KnowledgeNode, related_to: Optional[List[Tuple[str, str, float]]] = None):
        """Agrega un nodo atómico al grafo de conocimiento (estilo Zettelkasten) y sus enlaces."""
        with self.store._connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO kg_nodes (node_id, node_type, title, content, tags_json, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (node.node_id, node.node_type, node.title, node.content, json.dumps(node.tags, ensure_ascii=False), node.updated_at))
            if related_to:
                for target_id, relation, weight in related_to:
                    conn.execute("""
                        INSERT OR REPLACE INTO kg_edges (source_id, target_id, relation, weight)
                        VALUES (?, ?, ?, ?)
                    """, (node.node_id, target_id, relation, weight))
            conn.commit()

    def search_knowledge_graph(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Recuperación híbrida BM25 + expansión de 1 salto en el grafo de conocimiento en consulta única IN (...)."""
        q_tokens = set(re.findall(r"\w{3,}", query.lower()))
        with self.store._connection() as conn:
            rows = conn.execute("SELECT * FROM kg_nodes").fetchall()
            scored = []
            for r in rows:
                text = f"{r['title']} {r['content']} {r['tags_json']}".lower()
                doc_tokens = set(re.findall(r"\w{3,}", text))
                overlap = len(q_tokens & doc_tokens)
                if overlap > 0 or not q_tokens:
                    score = overlap / math.sqrt(max(len(doc_tokens), 1))
                    scored.append({
                        "node_id": r["node_id"],
                        "node_type": r["node_type"],
                        "title": r["title"],
                        "content": r["content"],
                        "tags": json.loads(r["tags_json"]),
                        "score": round(score, 4),
                        "links": []
                    })
            scored.sort(key=lambda x: x["score"], reverse=True)
            top_scored = scored[:top_k]
            if top_scored:
                node_ids = [item["node_id"] for item in top_scored]
                edges_by_source: Dict[str, List[Dict[str, Any]]] = {nid: [] for nid in node_ids}
                for offset in range(0, len(node_ids), 500):
                    chunk = node_ids[offset:offset + 500]
                    placeholders = ",".join("?" for _ in chunk)
                    edge_rows = conn.execute(
                        f"SELECT source_id, target_id, relation, weight FROM kg_edges WHERE source_id IN ({placeholders})",
                        tuple(chunk),
                    ).fetchall()
                    for e in edge_rows:
                        edges_by_source[e["source_id"]].append({
                            "target": e["target_id"],
                            "relation": e["relation"],
                            "weight": e["weight"],
                        })
                for item in top_scored:
                    item["links"] = edges_by_source.get(item["node_id"], [])
            return top_scored
