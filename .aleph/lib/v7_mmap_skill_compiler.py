#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
C:\Users\Lucas cardozo\.aleph\lib\v7_mmap_skill_compiler.py

Compilador e Indexador Binario Mmap de 1,957 Skills para El Aleph v7.0 Omega-Prime.
Diseñado para la Doctrina EL DEMIURGO.

Responsabilidades Nucleares:
  1. SkillFrontmatterParser: Extracción determinista de metadatos YAML y secciones Markdown.
  2. VSA10240Projector: Proyección hiperdimensional determinista en {0, 1}^10240 (160 x u64).
  3. BM25OkapiIndexer: Precomputación de estadísticas léxicas DF, IDF y matriz de términos.
  4. SkillsCatalogDB: Gestor de catálogo SQLite WAL de alto throughput con tabla virtual FTS5.
  5. MmapSkillCompiler: Pipeline atómico de compilación, serialización binaria y verificación SHA-256.
  6. Interfaz CLI completa con comandos --compile, --verify, --stats y --benchmark.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
import math
import mmap
import os
from pathlib import Path
import re
import sqlite3
import struct
import sys
import time
from typing import Any, Dict, Generator, Iterable, List, Optional, Sequence, Set, Tuple, Union

import numpy as np

# Constantes de Arquitectura Binaria VSA
MAGIC_BYTES: bytes = b"ALEPHVSA"
FORMAT_VERSION: int = 1
VSA_DIMENSION_BITS: int = 10240
VSA_WORDS_64: int = 160
BYTES_PER_SKILL: int = VSA_WORDS_64 * 8  # Exactamente 1,280 bytes
HEADER_FORMAT: str = "<8sIIIIQ32s"
HEADER_SIZE_BYTES: int = 64

# Rutas Canónicas del Sistema
DEFAULT_SKILLS_DIR: Path = Path(r"C:\Users\Lucas cardozo\.agents\skills")
DEFAULT_ALEPH_ROOT: Path = Path(r"C:\Users\Lucas cardozo\.aleph")
DEFAULT_DATA_DIR: Path = DEFAULT_ALEPH_ROOT / "data"
DEFAULT_MMAP_PATH: Path = DEFAULT_DATA_DIR / "skills_vsa_10240.mmap"
DEFAULT_DB_PATH: Path = DEFAULT_DATA_DIR / "skills_catalog.db"
DEFAULT_JSON_PATH: Path = DEFAULT_DATA_DIR / "skills_metadata.json"


@dataclass(frozen=True)
class SkillMetadata:
    """Estructura inmutable que contiene los metadatos completos y el contenido de una habilidad."""
    id: int
    name: str
    path: str
    description: str
    allowed_tools: List[str]
    tags: List[str]
    risk: str
    step_count: int
    raw_markdown_bytes: int
    sha256: str
    mtime: float
    sections: Dict[str, str]
    clean_text: str


class SkillFrontmatterParser:
    """
    Parser determinista y tolerante a fallos para YAML frontmatter y secciones Markdown.
    No requiere dependencias externas como PyYAML, operando a alta velocidad con regex y state machine.
    """

    FRONTMATTER_PATTERN = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n(.*)$", re.DOTALL)
    HEADING_PATTERN = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
    LIST_ITEM_PATTERN = re.compile(r"^\s*(?:\d+[\.\)]|[-*])\s+(.+)$", re.MULTILINE)

    @classmethod
    def parse_file(cls, file_path: Union[str, Path], skill_id: int = 0) -> SkillMetadata:
        """Lee y parsea un archivo SKILL.md desde el sistema de archivos."""
        path = Path(file_path).resolve()
        stat = path.stat()
        raw_bytes = path.read_bytes()
        sha256_hash = hashlib.sha256(raw_bytes).hexdigest()
        text_content = raw_bytes.decode("utf-8", errors="replace")
        return cls.parse_content(
            content=text_content,
            path_str=str(path),
            skill_id=skill_id,
            mtime=stat.st_mtime,
            raw_bytes_len=len(raw_bytes),
            sha256_val=sha256_hash,
        )

    @classmethod
    def parse_content(
        cls,
        content: str,
        path_str: str,
        skill_id: int = 0,
        mtime: float = 0.0,
        raw_bytes_len: int = 0,
        sha256_val: str = "",
    ) -> SkillMetadata:
        """Parsea el contenido textual de una habilidad extrayendo frontmatter y secciones."""
        frontmatter_dict: Dict[str, Any] = {}
        body = content

        fm_match = cls.FRONTMATTER_PATTERN.match(content)
        if fm_match:
            fm_text, body = fm_match.group(1), fm_match.group(2)
            frontmatter_dict = cls._parse_yaml_lines(fm_text)

        dir_fallback_name = Path(path_str).parent.name if path_str else f"skill-{skill_id}"
        name = str(frontmatter_dict.get("name") or dir_fallback_name).strip()

        # Extracción y limpieza de descripción
        description = str(frontmatter_dict.get("description") or "").strip()
        if not description:
            # Extraer primer párrafo no vacío del cuerpo
            paragraphs = [p.strip() for p in body.split("\n\n") if p.strip() and not p.strip().startswith("#")]
            description = paragraphs[0].replace("\n", " ")[:280] if paragraphs else name.replace("-", " ")

        # Herramientas permitidas (allowed-tools / allowed_tools)
        raw_tools = frontmatter_dict.get("allowed_tools") or frontmatter_dict.get("allowed-tools") or []
        allowed_tools: List[str] = []
        if isinstance(raw_tools, list):
            allowed_tools = [str(t).strip() for t in raw_tools if str(t).strip()]
        elif isinstance(raw_tools, str):
            allowed_tools = [t.strip() for t in raw_tools.replace("[", "").replace("]", "").split(",") if t.strip()]

        # Etiquetas (tags)
        raw_tags = frontmatter_dict.get("tags") or []
        tags: List[str] = []
        if isinstance(raw_tags, list):
            tags = [str(t).strip().lower() for t in raw_tags if str(t).strip()]
        elif isinstance(raw_tags, str):
            tags = [t.strip().lower() for t in raw_tags.replace("[", "").replace("]", "").split(",") if t.strip()]

        risk = str(frontmatter_dict.get("risk") or "unknown").strip().lower()

        # Extracción de secciones Markdown
        sections = cls._extract_markdown_sections(body)

        # Conteo de pasos en la sección de ejecución
        pasos_text = sections.get("pasos", "") or sections.get("steps", "") or body
        step_items = cls.LIST_ITEM_PATTERN.findall(pasos_text)
        step_count = len(step_items)

        # Texto limpio para indexación y proyección
        clean_text = cls._clean_text_for_indexing(f"{name} {description} {' '.join(tags)} {body}")

        if not sha256_val:
            sha256_val = hashlib.sha256(content.encode("utf-8")).hexdigest()
        if raw_bytes_len == 0:
            raw_bytes_len = len(content.encode("utf-8"))

        return SkillMetadata(
            id=skill_id,
            name=name,
            path=path_str,
            description=description,
            allowed_tools=allowed_tools,
            tags=tags,
            risk=risk,
            step_count=step_count,
            raw_markdown_bytes=raw_bytes_len,
            sha256=sha256_val,
            mtime=mtime,
            sections=sections,
            clean_text=clean_text,
        )

    @classmethod
    def _parse_yaml_lines(cls, yaml_text: str) -> Dict[str, Any]:
        """Parser básico de YAML lineal para parejas clave-valor y listas simples."""
        result: Dict[str, Any] = {}
        current_list_key: Optional[str] = None

        for line in yaml_text.splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue

            # Elemento de lista "- valor"
            if line_str.startswith("- ") and current_list_key is not None:
                item_val = line_str[2:].strip().strip('"\'')
                if isinstance(result.get(current_list_key), list):
                    result[current_list_key].append(item_val)
                continue

            # Par clave: valor
            if ":" in line_str:
                parts = line_str.split(":", 1)
                k = parts[0].strip().replace("-", "_")
                v = parts[1].strip()

                if not v:
                    # Posible lista en líneas siguientes
                    result[k] = []
                    current_list_key = k
                elif v.startswith("[") and v.endswith("]"):
                    # Lista inline [a, b, c]
                    inner = v[1:-1].strip()
                    items = [x.strip().strip('"\'') for x in inner.split(",") if x.strip()]
                    result[k] = items
                    current_list_key = None
                else:
                    result[k] = v.strip('"\'')
                    current_list_key = None

        return result

    @classmethod
    def _extract_markdown_sections(cls, markdown_text: str) -> Dict[str, str]:
        """Extrae el contenido organizado por encabezados normalizados en minúsculas."""
        sections: Dict[str, str] = {}
        lines = markdown_text.splitlines()
        current_section = "intro"
        current_buffer: List[str] = []

        for line in lines:
            m = cls.HEADING_PATTERN.match(line)
            if m:
                if current_buffer:
                    sections[current_section] = "\n".join(current_buffer).strip()
                    current_buffer.clear()
                heading_title = m.group(2).strip().lower()
                # Normalización semántica de encabezados clave
                if "objetivo" in heading_title or "purpose" in heading_title or "scope" in heading_title:
                    current_section = "objetivo"
                elif "paso" in heading_title or "step" in heading_title or "workflow" in heading_title:
                    current_section = "pasos"
                elif "criterio" in heading_title or "success" in heading_title or "acceptance" in heading_title:
                    current_section = "criterios_de_exito"
                elif "regla" in heading_title or "hard rule" in heading_title or "constraint" in heading_title:
                    current_section = "reglas_duras"
                elif "checkpoint" in heading_title or "humano" in heading_title:
                    current_section = "checkpoint_humano"
                else:
                    clean_name = re.sub(r"[^a-z0-9_]", "_", heading_title).strip("_")
                    current_section = clean_name or "section"
            else:
                current_buffer.append(line)

        if current_buffer:
            sections[current_section] = "\n".join(current_buffer).strip()

        return sections

    @staticmethod
    def _clean_text_for_indexing(raw_text: str) -> str:
        """Elimina bloques de código, URLs y markdown tags para dejar texto puro indexable."""
        # Remover bloques de código ```...```
        no_code = re.sub(r"```.*?```", " ", raw_text, flags=re.DOTALL)
        # Remover código inline `...`
        no_inline = re.sub(r"`[^`]*`", " ", no_code)
        # Remover links markdown [texto](url) -> texto
        no_links = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", no_inline)
        # Remover símbolos especiales markdown
        no_md = re.sub(r"[#*_~>`=\-\[\]\(\)]", " ", no_links)
        # Normalizar espacios en blanco
        return re.sub(r"\s+", " ", no_md).strip()


class VSA10240Projector:
    """
    Proyector Hiperdimensional Determinista en {0, 1}^10240 (160 palabras uint64).
    Implementa:
      1. Generación determinista de vectores base de tokens mediante hashing SHA-256 de 40 bloques.
      2. Permutación circular por rotación de bits (orden posicional de n-gramas).
      3. Binding XOR de shingles adyacentes.
      4. Bundling mayoritario vectorizado con NumPy y desempate determinista PRNG.
    """

    DIMENSION_BITS: int = VSA_DIMENSION_BITS
    WORDS_64: int = VSA_WORDS_64

    def __init__(self, use_memoization: bool = True) -> None:
        self.use_memoization: bool = use_memoization
        self._token_cache: Dict[str, np.ndarray] = {}

    def get_token_vector(self, token: str) -> np.ndarray:
        """Genera o recupera de caché el hipervector cuasi-ortogonal de 10,240 bits para un token."""
        if self.use_memoization and token in self._token_cache:
            return self._token_cache[token]

        words = np.empty(self.WORDS_64, dtype=np.uint64)
        token_bytes = token.lower().encode("utf-8")

        # 40 iteraciones de SHA-256 producen 40 x 32 bytes = 1,280 bytes = 160 x u64
        for chunk_idx in range(40):
            seed_data = b"%s:%d" % (token_bytes, chunk_idx)
            digest = hashlib.sha256(seed_data).digest()
            w0, w1, w2, w3 = struct.unpack("<4Q", digest)
            base = chunk_idx * 4
            words[base] = w0
            words[base + 1] = w1
            words[base + 2] = w2
            words[base + 3] = w3

        if self.use_memoization:
            self._token_cache[token] = words
        return words

    def permute(self, vector: np.ndarray, shift_bits: int = 1) -> np.ndarray:
        """
        Permutación circular de 10,240 bits.
        Rotación en palabras y rotación a nivel de bits dentro de cada palabra.
        """
        word_shift = (shift_bits // 64) % self.WORDS_64
        bit_shift = shift_bits % 64

        # Rotación de palabras
        if word_shift > 0:
            rotated_words = np.concatenate([vector[word_shift:], vector[:word_shift]])
        else:
            rotated_words = vector.copy()

        # Rotación de bits
        if bit_shift > 0:
            inv_shift = 64 - bit_shift
            part1 = rotated_words >> np.uint64(bit_shift)
            part2 = rotated_words << np.uint64(inv_shift)
            return part1 | part2
        return rotated_words

    def bind(self, vec_a: np.ndarray, vec_b: np.ndarray) -> np.ndarray:
        """Operador de Binding (XOR bit a bit): invierte paridad preservando cuasi-ortogonalidad."""
        return np.bitwise_xor(vec_a, vec_b)

    def bundle(self, vectors: Sequence[np.ndarray], tie_breaker_seed: str = "") -> np.ndarray:
        """
        Operador de Bundling (Superposición por regla de mayoría).
        Vectorizado mediante desempaquetado de bits en NumPy.
        Si la cantidad de vectores M es par, desempata de forma determinista usando el seed textual.
        """
        num_vecs = len(vectors)
        if num_vecs == 0:
            return np.zeros(self.WORDS_64, dtype=np.uint64)
        if num_vecs == 1:
            return vectors[0].copy()

        matrix = np.vstack(vectors)  # Formato: (M, 160) uint64
        # Desempaquetar a bits individuales: (M, 160, 8 bytes, 8 bits) -> (M, 160, 64) uint8
        unpacked = np.unpackbits(matrix.view(np.uint8).reshape(num_vecs, self.WORDS_64, 8), axis=2, bitorder="little")
        # Sumar votos a través de la dimensión de vectores: (160, 64)
        bit_sums = np.sum(unpacked, axis=0)
        threshold = num_vecs // 2

        majority_bits = (bit_sums > threshold).astype(np.uint8)

        # Manejo estricto de empates para M par
        if num_vecs % 2 == 0:
            ties = (bit_sums == threshold)
            if np.any(ties):
                tie_vec = self.get_token_vector(f"__tie_breaker__:{tie_breaker_seed}")
                tie_unpacked = np.unpackbits(tie_vec.view(np.uint8).reshape(self.WORDS_64, 8), axis=1, bitorder="little")
                majority_bits = np.where(ties, tie_unpacked, majority_bits)

        packed = np.packbits(majority_bits, axis=1, bitorder="little")
        return packed.view(np.uint64).ravel()

    def project_text(self, text: str, name: str = "", tags: Sequence[str] = ()) -> np.ndarray:
        """
        Proyecta una descripción textual completa a un hipervector de 10,240 bits.
        Combina:
          - Tokens individuales ponderados (el nombre de la habilidad tiene triple peso).
          - Shingles de 2 tokens adyacentes vinculados con permutación (orden gramatical).
          - Trigramas de caracteres de palabras clave.
        """
        clean = text.lower()
        tokens = re.findall(r"[a-z0-9_\-]{3,}", clean)
        if not tokens:
            return self.get_token_vector(name or "empty_skill")

        vec_list: List[np.ndarray] = []

        # 1. Vectores del nombre con alto apalancamiento
        name_tokens = re.findall(r"[a-z0-9]+", name.lower())
        for nt in name_tokens:
            vec_nt = self.get_token_vector(nt)
            vec_list.extend([vec_nt, vec_nt, vec_nt])  # Ponderación x3

        # 2. Vectores de etiquetas (tags) con ponderación x2
        for tag in tags:
            tag_toks = re.findall(r"[a-z0-9]+", tag.lower())
            for tt in tag_toks:
                v_t = self.get_token_vector(tt)
                vec_list.extend([v_t, v_t])

        # 3. Tokens del cuerpo y shingles posicionales (bigramas de palabras)
        max_tokens = min(len(tokens), 96)
        prev_vec: Optional[np.ndarray] = None
        for i in range(max_tokens):
            t = tokens[i]
            cur_vec = self.get_token_vector(t)
            vec_list.append(cur_vec)

            # Binding posicional: w_{i-1} XOR Permute(w_i, 1)
            if prev_vec is not None:
                bound_pair = self.bind(prev_vec, self.permute(cur_vec, shift_bits=1))
                vec_list.append(bound_pair)
            prev_vec = cur_vec

        return self.bundle(vec_list, tie_breaker_seed=name)


class BM25OkapiIndexer:
    """
    Precomputador de estadísticas documentales y pesos BM25-Okapi.
    Calcula longitudes de documento, frecuencias documentales (DF),
    frecuencia documental inversa (IDF) y matriz de puntuaciones precalculadas.
    """

    K1: float = 1.25
    B: float = 0.75

    @classmethod
    def index_corpus(cls, skills: Sequence[SkillMetadata]) -> Dict[str, Any]:
        """Indexa un conjunto completo de habilidades y precalcula los pesos de términos."""
        num_docs = len(skills)
        if num_docs == 0:
            return {"num_docs": 0, "avgdl": 0.0, "idf": {}, "precomputed": {}}

        inverted_index: Dict[str, Dict[str, float]] = {}
        doc_lengths: Dict[str, int] = {}
        total_tokens = 0

        # Paso 1: Frecuencias de Términos (TF) y Longitudes
        for s in skills:
            tokens = re.findall(r"[a-z0-9_]{3,}", f"{s.name} {s.description} {' '.join(s.tags)}".lower())
            d_len = max(len(tokens), 1)
            doc_lengths[s.name] = d_len
            total_tokens += d_len

            term_counts: Dict[str, int] = {}
            for tok in tokens:
                term_counts[tok] = term_counts.get(tok, 0) + 1

            for tok, cnt in term_counts.items():
                if tok not in inverted_index:
                    inverted_index[tok] = {}
                inverted_index[tok][s.name] = float(cnt)

        avgdl = total_tokens / float(num_docs)

        # Paso 2: Cálculo de IDF y Pesos Precalculados BM25
        idf_table: Dict[str, float] = {}
        precomputed_scores: Dict[str, Dict[str, float]] = {}

        for tok, postings in inverted_index.items():
            n_t = len(postings)
            # Fórmula estándar BM25-Okapi para IDF
            idf = math.log(1.0 + (num_docs - n_t + 0.5) / (n_t + 0.5))
            idf = max(idf, 0.05)  # Floor protector contra términos omnipresentes
            idf_table[tok] = round(idf, 4)

            term_doc_scores: Dict[str, float] = {}
            for doc_name, tf in postings.items():
                d_len = doc_lengths[doc_name]
                denom = tf + cls.K1 * (1.0 - cls.B + cls.B * (d_len / avgdl))
                numerator = idf * (tf * (cls.K1 + 1.0))
                term_doc_scores[doc_name] = round(numerator / denom, 4)

            precomputed_scores[tok] = term_doc_scores

        return {
            "num_docs": num_docs,
            "avgdl": round(avgdl, 2),
            "vocab_size": len(idf_table),
            "idf": idf_table,
            "precomputed": precomputed_scores,
        }


class SkillsCatalogDB:
    """
    Gestor del Catálogo de Habilidades en SQLite en modo WAL (Write-Ahead Logging).
    Proporciona persistencia estructurada, índices B-Tree y búsqueda full-text con FTS5.
    """

    def __init__(self, db_path: Union[str, Path]) -> None:
        self.db_path: Path = Path(db_path).resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None

    def get_connection(self) -> sqlite3.Connection:
        """Retorna una conexión activa configurada con PRAGMAs de alto rendimiento para Windows."""
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path), timeout=10.0, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            cursor = self._conn.cursor()
            cursor.execute("PRAGMA temp_store = MEMORY;")
            cursor.execute("PRAGMA mmap_size = 67108864;")  # 64 MB
            cursor.execute("PRAGMA busy_timeout = 5000;")
            cursor.close()
        return self._conn

    def init_schema(self) -> None:
        """Crea las tablas B-Tree y la tabla virtual FTS5 si no existen."""
        conn = self.get_connection()
        with conn:
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA synchronous = NORMAL;")
            conn.execute("""
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                path TEXT NOT NULL,
                description TEXT,
                allowed_tools TEXT,
                tags TEXT,
                step_count INTEGER DEFAULT 0,
                raw_markdown_bytes INTEGER DEFAULT 0,
                sha256 TEXT NOT NULL,
                mtime REAL NOT NULL
            );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_skills_name ON skills(name);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_skills_sha256 ON skills(sha256);")

            conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS skills_fts USING fts5(
                name,
                description,
                tags,
                content_text,
                tokenize = "unicode61 remove_diacritics 2"
            );
            """)

    def insert_skills_batch(self, skills: Sequence[SkillMetadata]) -> int:
        """Inserta o actualiza un lote de habilidades en una sola transacción atómica."""
        conn = self.get_connection()
        with conn:
            cursor = conn.cursor()
            # Limpiar datos previos para garantizar sincronía total con la matriz mmap
            cursor.execute("DELETE FROM skills;")
            cursor.execute("DELETE FROM skills_fts;")

            skills_rows = [
                (
                    s.id,
                    s.name,
                    s.path,
                    s.description,
                    json.dumps(s.allowed_tools, ensure_ascii=False),
                    json.dumps(s.tags, ensure_ascii=False),
                    s.step_count,
                    s.raw_markdown_bytes,
                    s.sha256,
                    s.mtime,
                )
                for s in skills
            ]
            cursor.executemany(
                """
                INSERT INTO skills (
                    id, name, path, description, allowed_tools, tags,
                    step_count, raw_markdown_bytes, sha256, mtime
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                skills_rows,
            )

            fts_rows = [
                (
                    s.name,
                    s.description,
                    " ".join(s.tags),
                    s.clean_text,
                )
                for s in skills
            ]
            cursor.executemany(
                """
                INSERT INTO skills_fts (rowid, name, description, tags, content_text)
                VALUES ((SELECT id FROM skills WHERE name = ?), ?, ?, ?, ?);
                """,
                [(s.name, s.name, s.description, " ".join(s.tags), s.clean_text) for s in skills],
            )
            cursor.close()
        return len(skills)

    def search_fts(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Realiza una búsqueda de texto completo con ponderación BM25 nativa de FTS5."""
        conn = self.get_connection()
        clean_q = re.sub(r"[^\w\s]", " ", query).strip()
        if not clean_q:
            return []

        fts_query = " OR ".join([f'"{tok}"*' for tok in clean_q.split() if len(tok) >= 2])
        if not fts_query:
            return []

        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT s.id, s.name, s.path, s.description, s.allowed_tools, s.tags, s.step_count, rank
                FROM skills_fts f
                JOIN skills s ON s.id = f.rowid
                WHERE skills_fts MATCH ?
                ORDER BY rank
                LIMIT ?;
                """,
                (fts_query, limit),
            )
            rows = cursor.fetchall()
            results = []
            for r in rows:
                results.append({
                    "id": r["id"],
                    "name": r["name"],
                    "path": r["path"],
                    "description": r["description"],
                    "allowed_tools": json.loads(r["allowed_tools"] or "[]"),
                    "tags": json.loads(r["tags"] or "[]"),
                    "step_count": r["step_count"],
                    "fts_rank": float(r["rank"]),
                })
            return results
        finally:
            cursor.close()

    def get_skill_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Recupera los metadatos de una habilidad por su clave primaria de nombre."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM skills WHERE name = ? LIMIT 1;", (name,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "id": row["id"],
                "name": row["name"],
                "path": row["path"],
                "description": row["description"],
                "allowed_tools": json.loads(row["allowed_tools"] or "[]"),
                "tags": json.loads(row["tags"] or "[]"),
                "step_count": row["step_count"],
                "raw_markdown_bytes": row["raw_markdown_bytes"],
                "sha256": row["sha256"],
                "mtime": row["mtime"],
            }
        finally:
            cursor.close()

    def count(self) -> int:
        """Retorna la cantidad total de habilidades indexadas."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM skills;")
            val = cursor.fetchone()[0]
            return int(val)
        finally:
            cursor.close()

    def verify_fts_integrity(self) -> bool:
        """Verifica la integridad física del árbol FTS5."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO skills_fts(skills_fts) VALUES('integrity-check');")
            return True
        except Exception:
            return False
        finally:
            cursor.close()

    def close(self) -> None:
        """Cierra la conexión activa."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None


class MmapSkillCompiler:
    """
    Compilador Soberano V7 de Habilidades.
    Escanea el corpus de 1,957 habilidades, proyecta hipervectores VSA,
    calcula estadísticas BM25 y emite de forma atómica:
      1. skills_vsa_10240.mmap (Cabecera de 64B + Payload de 2.39 MB).
      2. skills_catalog.db (SQLite WAL con FTS5).
      3. skills_metadata.json (Índice BM25 precomputado).
    """

    def __init__(
        self,
        skills_root: Optional[Union[str, Path]] = None,
        data_dir: Optional[Union[str, Path]] = None,
    ) -> None:
        self.skills_root: Path = Path(skills_root or DEFAULT_SKILLS_DIR).resolve()
        self.data_dir: Path = Path(data_dir or DEFAULT_DATA_DIR).resolve()
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.mmap_path: Path = self.data_dir / "skills_vsa_10240.mmap"
        self.db_path: Path = self.data_dir / "skills_catalog.db"
        self.json_path: Path = self.data_dir / "skills_metadata.json"

        self.projector: VSA10240Projector = VSA10240Projector(use_memoization=True)

    def scan_skill_paths(self) -> List[Path]:
        """
        Escaneo de alto rendimiento de directorios en disco.
        Usa os.scandir() para minimizar los cambios de contexto en Windows NTFS.
        """
        if not self.skills_root.exists():
            return []

        skill_files: List[Path] = []
        with os.scandir(str(self.skills_root)) as it:
            for entry in it:
                if entry.is_dir():
                    candidate = Path(entry.path) / "SKILL.md"
                    if candidate.is_file():
                        skill_files.append(candidate)

        # Ordenamiento determinista lexicográfico por nombre de habilidad
        skill_files.sort(key=lambda p: p.parent.name)
        return skill_files

    def compile(self, force: bool = False) -> Dict[str, Any]:
        """
        Ejecuta el pipeline completo de compilación de forma atómica.
        Usa archivos temporales .tmp y os.replace() para evitar corrupción de datos.
        """
        t_start = time.perf_counter()
        skill_paths = self.scan_skill_paths()
        total_skills = len(skill_paths)

        if total_skills == 0:
            return {
                "status": "ERROR",
                "message": f"No se encontraron habilidades en: {self.skills_root}",
                "count": 0,
            }

        # Comprobar si ya está compilado
        if not force and self.mmap_path.exists() and self.db_path.exists() and self.json_path.exists():
            v_res = self.verify()
            if v_res.get("valid", False):
                return {
                    "status": "ALREADY_COMPILED",
                    "count": total_skills,
                    "mmap_bytes": self.mmap_path.stat().st_size,
                    "db_bytes": self.db_path.stat().st_size,
                    "elapsed_ms": round((time.perf_counter() - t_start) * 1000.0, 2),
                }

        # 1. Parsear todas las habilidades
        t_parse_0 = time.perf_counter()
        parsed_skills: List[SkillMetadata] = []
        for idx, p in enumerate(skill_paths):
            meta = SkillFrontmatterParser.parse_file(p, skill_id=idx)
            parsed_skills.append(meta)
        dt_parse = time.perf_counter() - t_parse_0

        # 2. Proyección Hiperdimensional VSA de 10,240 bits
        t_proj_0 = time.perf_counter()
        vector_list: List[np.ndarray] = []
        for s in parsed_skills:
            v = self.projector.project_text(
                text=s.clean_text,
                name=s.name,
                tags=s.tags,
            )
            vector_list.append(v)
        dt_proj = time.perf_counter() - t_proj_0

        matrix_u64 = np.vstack(vector_list)  # (N, 160) uint64
        payload_bytes = matrix_u64.tobytes()
        payload_sha256 = hashlib.sha256(payload_bytes).digest()

        # 3. Construir Cabecera Binaria Soberana (64 bytes exactos)
        timestamp_now = int(time.time())
        header_bytes = struct.pack(
            HEADER_FORMAT,
            MAGIC_BYTES,
            FORMAT_VERSION,
            total_skills,
            VSA_DIMENSION_BITS,
            VSA_WORDS_64,
            timestamp_now,
            payload_sha256,
        )
        assert len(header_bytes) == HEADER_SIZE_BYTES, f"Header size mismatch: {len(header_bytes)} != 64"

        # 4. Escritura Atómica del Archivo MMAP
        tmp_mmap_path = self.mmap_path.with_suffix(".mmap.tmp")
        with open(tmp_mmap_path, "wb") as f_mmap:
            f_mmap.write(header_bytes)
            f_mmap.write(payload_bytes)
            f_mmap.flush()
            os.fsync(f_mmap.fileno())
        os.replace(tmp_mmap_path, self.mmap_path)

        # 5. Precomputación de Estadísticas BM25-Okapi y Dump JSON
        t_bm25_0 = time.perf_counter()
        bm25_data = BM25OkapiIndexer.index_corpus(parsed_skills)
        dt_bm25 = time.perf_counter() - t_bm25_0

        metadata_payload = {
            "version": "7.0.0",
            "count": total_skills,
            "vsa_dimension": VSA_DIMENSION_BITS,
            "vsa_words": VSA_WORDS_64,
            "compiled_at_epoch": timestamp_now,
            "payload_sha256_hex": payload_sha256.hex(),
            "avg_doc_len": bm25_data["avgdl"],
            "vocab_size": bm25_data["vocab_size"],
            "idf": bm25_data["idf"],
            "precomputed_bm25": bm25_data["precomputed"],
            "records": [
                {
                    "id": s.id,
                    "name": s.name,
                    "path": s.path,
                    "description": s.description,
                    "allowed_tools": s.allowed_tools,
                    "tags": s.tags,
                    "risk": s.risk,
                    "step_count": s.step_count,
                    "raw_markdown_bytes": s.raw_markdown_bytes,
                    "sha256": s.sha256,
                }
                for s in parsed_skills
            ],
        }

        tmp_json_path = self.json_path.with_suffix(".json.tmp")
        with open(tmp_json_path, "w", encoding="utf-8") as f_json:
            json.dump(metadata_payload, f_json, ensure_ascii=False)
            f_json.flush()
            os.fsync(f_json.fileno())
        os.replace(tmp_json_path, self.json_path)

        # 6. Población de Catálogo SQLite WAL con FTS5
        t_db_0 = time.perf_counter()
        catalog_db = SkillsCatalogDB(self.db_path)
        catalog_db.init_schema()
        catalog_db.insert_skills_batch(parsed_skills)
        catalog_db.close()
        dt_db = time.perf_counter() - t_db_0

        total_elapsed_ms = (time.perf_counter() - t_start) * 1000.0

        return {
            "status": "OK",
            "skills_compiled": total_skills,
            "mmap_file": str(self.mmap_path),
            "mmap_bytes": self.mmap_path.stat().st_size,
            "db_file": str(self.db_path),
            "db_bytes": self.db_path.stat().st_size,
            "json_bytes": self.json_path.stat().st_size,
            "timings_ms": {
                "parse": round(dt_parse * 1000.0, 2),
                "vsa_projection": round(dt_proj * 1000.0, 2),
                "bm25_index": round(dt_bm25 * 1000.0, 2),
                "sqlite_wal": round(dt_db * 1000.0, 2),
                "total": round(total_elapsed_ms, 2),
            },
            "throughput_skills_per_sec": round(total_skills / (total_elapsed_ms / 1000.0), 2),
        }

    def verify(self) -> Dict[str, Any]:
        """
        Verificación forense bit-a-bit de consistencia e integridad.
        Comprueba cabecera binaria, checksum SHA-256, dimensiones del tensor y base SQLite.
        """
        if not self.mmap_path.exists():
            return {"valid": False, "error": f"Falta archivo mmap: {self.mmap_path}"}
        if not self.db_path.exists():
            return {"valid": False, "error": f"Falta base de datos: {self.db_path}"}

        file_size = self.mmap_path.stat().st_size
        if file_size < HEADER_SIZE_BYTES:
            return {"valid": False, "error": f"Archivo corrupto, tamaño insuficiente: {file_size}"}

        with open(self.mmap_path, "rb") as f:
            header_raw = f.read(HEADER_SIZE_BYTES)
            magic, ver, num_skills, vsa_dim, w_size, epoch, payload_sha = struct.unpack(
                HEADER_FORMAT, header_raw
            )

            if magic != MAGIC_BYTES:
                return {"valid": False, "error": f"Magic bytes inválidos: {magic}"}
            if ver != FORMAT_VERSION:
                return {"valid": False, "error": f"Versión de formato no soportada: {ver}"}
            if vsa_dim != VSA_DIMENSION_BITS or w_size != VSA_WORDS_64:
                return {"valid": False, "error": f"Dimensiones incompatibles: dim={vsa_dim}, word={w_size}"}

            expected_payload_size = num_skills * BYTES_PER_SKILL
            expected_total_size = HEADER_SIZE_BYTES + expected_payload_size
            if file_size != expected_total_size:
                return {
                    "valid": False,
                    "error": f"Tamaño incorrecto: actual={file_size}, esperado={expected_total_size}",
                }

            # Recálculo de integridad SHA-256 sobre el payload
            payload_data = f.read(expected_payload_size)
            actual_sha = hashlib.sha256(payload_data).digest()
            if actual_sha != payload_sha:
                return {
                    "valid": False,
                    "error": "Checksum SHA-256 del payload no coincide (corrupción binaria)",
                }

        # Verificación del catálogo SQLite WAL
        catalog_db = SkillsCatalogDB(self.db_path)
        db_count = catalog_db.count()
        fts_valid = catalog_db.verify_fts_integrity()
        catalog_db.close()

        if db_count != num_skills:
            return {
                "valid": False,
                "error": f"Discrepancia en recuento DB vs MMAP: DB={db_count}, MMAP={num_skills}",
            }
        if not fts_valid:
            return {"valid": False, "error": "El índice virtual FTS5 reportó corrupción estructural"}

        return {
            "valid": True,
            "status": "VERIFIED_OK",
            "num_skills": num_skills,
            "vsa_dimension": vsa_dim,
            "total_bytes": file_size,
            "compiled_epoch": epoch,
            "sha256_hex": actual_sha.hex(),
            "sqlite_rows": db_count,
            "fts5_healthy": True,
        }

    def stats(self) -> Dict[str, Any]:
        """Retorna estadísticas completas del corpus compilado."""
        v = self.verify()
        if not v.get("valid", False):
            return {"status": "NOT_COMPILED_OR_INVALID", "details": v}

        catalog_db = SkillsCatalogDB(self.db_path)
        conn = catalog_db.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT AVG(step_count), MAX(step_count), AVG(raw_markdown_bytes) FROM skills;")
        avg_steps, max_steps, avg_bytes = cursor.fetchone()

        cursor.execute("SELECT allowed_tools FROM skills WHERE allowed_tools != '[]';")
        tool_counts: Dict[str, int] = {}
        for row in cursor.fetchall():
            tools = json.loads(row[0] or "[]")
            for t in tools:
                tool_counts[t] = tool_counts.get(t, 0) + 1

        cursor.close()
        catalog_db.close()

        # Top 10 herramientas más demandadas
        top_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "status": "OK",
            "skills_count": v["num_skills"],
            "mmap_file_size_bytes": v["total_bytes"],
            "avg_steps_per_skill": round(float(avg_steps or 0.0), 2),
            "max_steps": int(max_steps or 0),
            "avg_markdown_size_bytes": round(float(avg_bytes or 0.0), 2),
            "top_allowed_tools": top_tools,
            "sha256": v["sha256_hex"],
        }

    def benchmark(self, iterations: int = 50) -> Dict[str, Any]:
        """
        Ejecuta benchmarks de latencia de inicialización en frío,
        proyección semántica VSA y consultas FTS5 en la base de datos.
        """
        v = self.verify()
        if not v.get("valid", False):
            return {"status": "ERROR", "message": "Corpus no verificado", "details": v}

        # 1. Benchmark de Arranque en Frío (Apertura de MMAP + Conexión SQLite)
        boot_latencies: List[float] = []
        for _ in range(iterations):
            t0 = time.perf_counter()
            with open(self.mmap_path, "rb") as f_bin:
                mm = mmap.mmap(f_bin.fileno(), 0, access=mmap.ACCESS_READ)
                # Leer cabecera y primera fila
                _hdr = mm[:64]
                _row = mm[64: 64 + BYTES_PER_SKILL]
                mm.close()

            c_db = SkillsCatalogDB(self.db_path)
            _cnt = c_db.count()
            c_db.close()
            dt_ms = (time.perf_counter() - t0) * 1000.0
            boot_latencies.append(dt_ms)

        # 2. Benchmark de Búsqueda FTS5
        queries = ["docker container", "python simd avx2", "sqlite wal performance", "machine learning onnx", "rust ffi c-abi"]
        fts_latencies: List[float] = []
        c_db = SkillsCatalogDB(self.db_path)
        for _ in range(iterations):
            for q in queries:
                t0 = time.perf_counter()
                res = c_db.search_fts(q, limit=5)
                dt_ms = (time.perf_counter() - t0) * 1000.0
                fts_latencies.append(dt_ms)
        c_db.close()

        # 3. Benchmark de Proyección VSA
        vsa_latencies: List[float] = []
        for _ in range(iterations):
            t0 = time.perf_counter()
            _vec = self.projector.project_text(
                "optimizar cold-start mediante memoria mapeada y rust con kernel simétrico",
                name="test-query",
            )
            dt_ms = (time.perf_counter() - t0) * 1000.0
            vsa_latencies.append(dt_ms)

        boot_arr = np.array(boot_latencies)
        fts_arr = np.array(fts_latencies)
        vsa_arr = np.array(vsa_latencies)

        return {
            "status": "BENCHMARK_COMPLETE",
            "iterations": iterations,
            "cold_boot_latency_ms": {
                "min": round(float(np.min(boot_arr)), 3),
                "mean": round(float(np.mean(boot_arr)), 3),
                "p50": round(float(np.percentile(boot_arr, 50)), 3),
                "p95": round(float(np.percentile(boot_arr, 95)), 3),
                "p99": round(float(np.percentile(boot_arr, 99)), 3),
                "target_met": bool(np.mean(boot_arr) < 4.5),
            },
            "fts5_query_latency_ms": {
                "min": round(float(np.min(fts_arr)), 3),
                "mean": round(float(np.mean(fts_arr)), 3),
                "p50": round(float(np.percentile(fts_arr, 50)), 3),
                "p95": round(float(np.percentile(fts_arr, 95)), 3),
            },
            "vsa_projection_latency_ms": {
                "min": round(float(np.min(vsa_arr)), 3),
                "mean": round(float(np.mean(vsa_arr)), 3),
                "p50": round(float(np.percentile(vsa_arr, 50)), 3),
                "p95": round(float(np.percentile(vsa_arr, 95)), 3),
            },
        }


def main() -> int:
    """Punto de entrada de línea de comandos para el compilador V7."""
    parser = argparse.ArgumentParser(
        description="Compilador e Indexador Binario Mmap de 1,957 Skills para El Aleph v7.0 Omega-Prime"
    )
    parser.add_argument("--compile", action="store_true", help="Compilar el directorio de skills a .mmap y .db")
    parser.add_argument("--force", action="store_true", help="Forzar recompilación incluso si los archivos existen")
    parser.add_argument("--verify", action="store_true", help="Verificar consistencia bit-a-bit del header y SQLite")
    parser.add_argument("--stats", action="store_true", help="Mostrar estadísticas detalladas del corpus compilado")
    parser.add_argument("--benchmark", action="store_true", help="Ejecutar benchmarks de latencia de cold-boot y queries")
    parser.add_argument("--skills-dir", type=str, default="", help="Directorio raíz de habilidades")
    parser.add_argument("--data-dir", type=str, default="", help="Directorio destino de datos binarios")

    args = parser.parse_args()

    skills_root = Path(args.skills_dir) if args.skills_dir else None
    data_dir = Path(args.data_dir) if args.data_dir else None

    compiler = MmapSkillCompiler(skills_root=skills_root, data_dir=data_dir)

    # Si no se pasa ninguna bandera, ejecutar compilación por defecto
    if not any([args.compile, args.verify, args.stats, args.benchmark]):
        args.compile = True

    if args.compile:
        print("[ALEPH-COMPILER] Iniciando compilación de habilidades...")
        result = compiler.compile(force=args.force)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        if result.get("status") not in ("OK", "ALREADY_COMPILED"):
            return 1

    if args.verify:
        print("[ALEPH-COMPILER] Verificando integridad del tensor mmap y catálogo DB...")
        v_res = compiler.verify()
        print(json.dumps(v_res, indent=2, ensure_ascii=False))
        if not v_res.get("valid", False):
            return 2

    if args.stats:
        print("[ALEPH-COMPILER] Estadísticas del corpus de habilidades:")
        s_res = compiler.stats()
        print(json.dumps(s_res, indent=2, ensure_ascii=False))

    if args.benchmark:
        print("[ALEPH-COMPILER] Ejecutando benchmarks de rendimiento...")
        b_res = compiler.benchmark(iterations=50)
        print(json.dumps(b_res, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
