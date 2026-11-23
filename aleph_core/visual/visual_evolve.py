"""Visión perceptual CV + Primitiva inédita texto-vs-saliencia + MAP-Elites Bradley-Terry/Elo."""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import math
import os
import sqlite3
import struct
import uuid
import zlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    return a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)


def _decode_png_grid(png_path: str, gw: int = 96, gh: int = 60) -> Tuple[int, int, List[Tuple[int, int, int]]]:
    """Decodifica PNG RGB/RGBA en stdlib puro y muestrea a grid gw x gh."""
    raw = Path(png_path).read_bytes()
    if len(raw) < 24 or raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Invalid PNG signature: {png_path}")
    pos, width, height, ctype = 8, 0, 0, 6
    idat_chunks: List[bytes] = []
    while pos + 8 <= len(raw):
        clen, ctag = struct.unpack(">I4s", raw[pos : pos + 8])
        cdata = raw[pos + 8 : pos + 8 + clen]
        pos += 12 + clen
        if ctag == b"IHDR":
            width, height, _bd, ctype = struct.unpack(">IIBB", cdata[:10])
        elif ctag == b"IDAT":
            idat_chunks.append(cdata)
        elif ctag == b"IEND":
            break
    if width <= 0 or height <= 0 or not idat_chunks:
        raise ValueError("Missing IHDR or IDAT in PNG")
    bpp = 4 if ctype == 6 else 3 if ctype == 2 else 1
    stride = width * bpp
    decomp = zlib.decompress(b"".join(idat_chunks))
    out_w, out_h = min(gw, width), min(gh, height)
    sample_ys = [int(y * height / out_h) for y in range(out_h)]
    sample_xs = [int(x * width / out_w) for x in range(out_w)]
    needed_rows = set(sample_ys)
    prev, rows, offset = bytearray(stride), {}, 0
    for y in range(height):
        if offset >= len(decomp):
            break
        ft = decomp[offset]
        row = bytearray(decomp[offset + 1 : offset + 1 + stride])
        offset += 1 + stride
        if ft == 1:
            for i in range(bpp, stride):
                row[i] = (row[i] + row[i - bpp]) & 0xFF
        elif ft == 2:
            for i in range(stride):
                row[i] = (row[i] + prev[i]) & 0xFF
        elif ft == 3:
            for i in range(stride):
                row[i] = (row[i] + (((row[i - bpp] if i >= bpp else 0) + prev[i]) >> 1)) & 0xFF
        elif ft == 4:
            for i in range(stride):
                a = row[i - bpp] if i >= bpp else 0
                c = prev[i - bpp] if i >= bpp else 0
                row[i] = (row[i] + _paeth(a, prev[i], c)) & 0xFF
        prev = row
        if y in needed_rows:
            rows[y] = bytes(row)
    pixels: List[Tuple[int, int, int]] = []
    for sy in sample_ys:
        rb = rows.get(sy, b"")
        for sx in sample_xs:
            idx = sx * bpp
            if bpp >= 3 and idx + 2 < len(rb):
                pixels.append((rb[idx], rb[idx + 1], rb[idx + 2]))
            else:
                v = rb[idx] if idx < len(rb) else 0
                pixels.append((v, v, v))
    return out_w, out_h, pixels


def analyze_png_perceptual_and_clearance(
    png_path: str, viewport_w: int, viewport_h: int, unshielded_rects: List[Dict[str, Any]], type_scale_ratio: float = 2.0
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Computa métricas CV reales (Sobel, saliencia, aire, acento) y primitiva saliency_text_clearance."""
    w, h, px = _decode_png_grid(png_path)
    n = max(1, w * h)
    lums = [0.299 * r + 0.587 * g + 0.114 * b for r, g, b in px]
    sats = [((max(r, g, b) - min(r, g, b)) / max(r, g, b)) if max(r, g, b) > 4 else 0.0 for r, g, b in px]
    sobel, sal = [0.0] * n, [0.0] * n
    mean_lum = sum(lums) / n
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            i = y * w + x
            gx = -lums[i - w - 1] + lums[i - w + 1] - 2 * lums[i - 1] + 2 * lums[i + 1] - lums[i + w - 1] + lums[i + w + 1]
            gy = -lums[i - w - 1] - 2 * lums[i - w] - lums[i - w + 1] + lums[i + w - 1] + 2 * lums[i + w] + lums[i + w + 1]
            mag = min(1.0, math.hypot(gx, gy) / 360.0)
            sobel[i] = mag
            sal[i] = min(1.0, 0.58 * mag + 0.25 * (abs(lums[i] - mean_lum) / 255.0) + 0.17 * sats[i])

    edge_clutter = round(sum(sobel) / n, 4)
    neg_space = round(sum(1 for i in range(n) if sobel[i] < 0.09 and abs(lums[i] - mean_lum) < 38.0) / n, 4)
    sat_ratio = round(sum(1 for i in range(n) if sats[i] > 0.38 and lums[i] > 28.0) / n, 4)
    total_sal = sum(sal)
    if total_sal > 1e-6:
        cx = round(sum((i % w) / max(1, w - 1) * sal[i] for i in range(n)) / total_sal, 4)
        cy = round(sum((i // w) / max(1, h - 1) * sal[i] for i in range(n)) / total_sal, 4)
        mean_sal = total_sal / n
        peak_sal = sum(sorted(sal, reverse=True)[: max(1, n // 10)]) / max(1, n // 10)
        focal_conc = round(min(1.0, max(0.0, (peak_sal - mean_sal) / max(0.08, peak_sal))), 4)
    else:
        cx, cy, focal_conc = 0.5, 0.5, 0.0

    colliding: List[str] = []
    max_under_sal = 0.0
    vw, vh = max(1, int(viewport_w)), max(1, int(viewport_h))
    for rect in unshielded_rects:
        x0 = max(0, min(w - 1, int(float(rect.get("left", 0)) / vw * w)))
        x1 = max(x0 + 1, min(w, int(float(rect.get("right", 0)) / vw * w)))
        y0 = max(0, min(h - 1, int(float(rect.get("top", 0)) / vh * h)))
        y1 = max(y0 + 1, min(h, int(float(rect.get("bottom", 0)) / vh * h)))
        cells = [sal[yy * w + xx] for yy in range(y0, y1) for xx in range(x0, x1)]
        if cells:
            noisy = sum(1 for v in cells if v > 0.28) / len(cells)
            max_under_sal = max(max_under_sal, round(sum(cells) / len(cells), 4))
            if noisy > 0.34 and bool(rect.get("overlapsCanvas")):
                sel = str(rect.get("selector") or "text")
                if sel not in colliding:
                    colliding.append(sel)

    clearance_score = round(max(0.0, 100.0 - len(colliding) * 28.0 - max_under_sal * 25.0), 2)
    air_score = max(0.0, 1.0 - abs(neg_space - 0.52) / 0.52)
    clutter_score = max(0.0, 1.0 - max(0.0, edge_clutter - 0.18) / 0.35)
    accent_score = 1.0 if sat_ratio <= 0.16 else max(0.0, 1.0 - (sat_ratio - 0.16) / 0.3)
    scale_score = min(1.0, max(0.0, (type_scale_ratio - 1.2) / 1.8))
    pqi = round(min(100.0, max(0.0, 26.0 * focal_conc + 22.0 * air_score + 20.0 * clutter_score + 14.0 * accent_score + 10.0 * scale_score + 8.0 * (clearance_score / 100.0))), 2)

    cv_metrics = {"edge_clutter_density": edge_clutter, "focal_saliency_concentration": focal_conc, "focal_centroid_xy": [cx, cy], "negative_space_ratio": neg_space, "saturated_accent_ratio": sat_ratio, "typography_scale_ratio": round(float(type_scale_ratio), 3), "perceptual_quality_index": pqi}
    clearance = {"clearance_score": clearance_score, "unshielded_blocks": len(unshielded_rects), "colliding_selectors": colliding, "max_underlying_saliency": max_under_sal}
    return cv_metrics, clearance


class VisualEvolutionEngine:
    """Motor auto-evolutivo MAP-Elites + Bradley-Terry/Elo con rollback SHA-256."""

    def __init__(self, db_path: Optional[str] = None, repo_root: Optional[str] = None):
        if db_path:
            self.db_path = os.path.abspath(db_path)
        else:
            root = os.path.abspath(repo_root) if repo_root else os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.db_path = os.path.join(root, ".aleph", "runtime", "visual_evolution.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        conn = self._connect()
        try:
            conn.executescript(
                "CREATE TABLE IF NOT EXISTS visual_genome_niches (niche_key TEXT PRIMARY KEY, genome_id TEXT NOT NULL, design_mode TEXT NOT NULL, visual_paradigm TEXT NOT NULL, elo_rating REAL NOT NULL, bradley_terry_strength REAL NOT NULL, perceptual_score REAL NOT NULL, tokens_w3c_json TEXT NOT NULL, winning_patterns_json TEXT NOT NULL, rejected_antipatterns_json TEXT NOT NULL, screenshot_sha256 TEXT NOT NULL, updated_at TEXT NOT NULL);"
                "CREATE TABLE IF NOT EXISTS pairwise_matches (match_id TEXT PRIMARY KEY, design_mode TEXT NOT NULL, visual_paradigm TEXT NOT NULL, cand_a TEXT NOT NULL, cand_b TEXT NOT NULL, verdict_ab TEXT NOT NULL, verdict_ba TEXT NOT NULL, resolved_winner TEXT NOT NULL, position_bias_detected INTEGER NOT NULL, created_at TEXT NOT NULL);"
                "CREATE TABLE IF NOT EXISTS visual_genome_snapshots (snapshot_id TEXT PRIMARY KEY, niche_key TEXT NOT NULL, genome_id TEXT NOT NULL, pre_snapshot_sha256 TEXT NOT NULL, post_snapshot_sha256 TEXT NOT NULL, state_json TEXT NOT NULL, created_at TEXT NOT NULL);"
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def _gate_ok(cand: Dict[str, Any]) -> bool:
        return float(cand.get("overflow", cand.get("horizontal_overflow_px", 0.0))) == 0.0 and int(cand.get("console_errors", 0)) == 0 and float(cand.get("cls", 0.0)) <= 0.25

    @staticmethod
    def _state_hash(row: Optional[Dict[str, Any]]) -> str:
        return hashlib.sha256(json.dumps(row or {}, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()

    def record_pairwise_match(self, design_mode: str, visual_paradigm: str, candidate_a: Dict[str, Any], candidate_b: Dict[str, Any], verdict_ab: str, verdict_ba: str) -> Dict[str, Any]:
        """Registra duelo ciego AB + BA, neutraliza sesgo posicional y actualiza Elo/BT."""
        v_ab, v_ba = str(verdict_ab or "tie").strip(), str(verdict_ba or "tie").strip()
        bias_detected = v_ab != v_ba
        resolved = "tie" if bias_detected else v_ab
        niche_key = f"{design_mode}::{visual_paradigm}"
        id_a, id_b = str(candidate_a.get("genome_id") or "cand_a"), str(candidate_b.get("genome_id") or "cand_b")
        elo_a, elo_b = float(candidate_a.get("elo_rating", 1200.0)), float(candidate_b.get("elo_rating", 1200.0))
        exp_a = 1.0 / (1.0 + 10.0 ** ((elo_b - elo_a) / 400.0))
        score_a = 1.0 if resolved == "A" else 0.0 if resolved == "B" else 0.5
        new_elo_a = round(elo_a + 32.0 * (score_a - exp_a), 2)
        new_elo_b = round(elo_b + 32.0 * ((1.0 - score_a) - (1.0 - exp_a)), 2)
        bt_a = round(10.0 ** ((new_elo_a - 1200.0) / 400.0), 4)
        bt_b = round(10.0 ** ((new_elo_b - 1200.0) / 400.0), 4)
        now = _dt.datetime.now(_dt.timezone.utc).isoformat()
        match_id = f"pm_{uuid.uuid4().hex[:10]}"

        conn = self._connect()
        try:
            conn.execute("INSERT INTO pairwise_matches VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (match_id, design_mode, visual_paradigm, id_a, id_b, v_ab, v_ba, resolved, 1 if bias_detected else 0, now))
            conn.commit()
        finally:
            conn.close()

        snapshot_id, promoted_id = None, None
        if resolved in ("A", "B"):
            winner = dict(candidate_a if resolved == "A" else candidate_b)
            winner["elo_rating"] = new_elo_a if resolved == "A" else new_elo_b
            winner["bradley_terry_strength"] = bt_a if resolved == "A" else bt_b
            if self._gate_ok(winner):
                promo = self.promote_champion(design_mode, visual_paradigm, winner)
                snapshot_id, promoted_id = promo.get("snapshot_id"), winner.get("genome_id")

        return {"match_id": match_id, "niche_key": niche_key, "position_bias_detected": bias_detected, "resolved_winner": resolved, "elo_a": new_elo_a, "elo_b": new_elo_b, "bradley_terry_a": bt_a, "bradley_terry_b": bt_b, "promoted_genome_id": promoted_id, "snapshot_id": snapshot_id}

    def promote_champion(self, design_mode: str, visual_paradigm: str, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Promueve campeón a su celda MAP-Elites guardando snapshot pre/post SHA-256."""
        if not self._gate_ok(candidate):
            raise ValueError("Candidate failed hard quality gate (overflow/console_errors/cls)")
        niche_key = f"{design_mode}::{visual_paradigm}"
        gid = str(candidate.get("genome_id") or f"gen_{uuid.uuid4().hex[:8]}")
        elo = float(candidate.get("elo_rating", 1200.0))
        bt = float(candidate.get("bradley_terry_strength", round(10.0 ** ((elo - 1200.0) / 400.0), 4)))
        pscore = float(candidate.get("perceptual_score", 0.0))
        tokens_json = json.dumps(candidate.get("tokens_w3c") or {}, ensure_ascii=False)
        wins_json = json.dumps(list(candidate.get("winning_patterns") or []), ensure_ascii=False)
        anti_json = json.dumps(list(candidate.get("rejected_antipatterns") or []), ensure_ascii=False)
        shot_sha = str(candidate.get("screenshot_sha256") or "")
        now = _dt.datetime.now(_dt.timezone.utc).isoformat()
        snap_id = f"snap_{uuid.uuid4().hex[:10]}"

        conn = self._connect()
        try:
            prev_row = conn.execute("SELECT * FROM visual_genome_niches WHERE niche_key = ?", (niche_key,)).fetchone()
            prev_dict = dict(prev_row) if prev_row is not None else {}
            pre_sha = self._state_hash(prev_dict)
            conn.execute("INSERT OR REPLACE INTO visual_genome_niches VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (niche_key, gid, design_mode, visual_paradigm, elo, bt, pscore, tokens_json, wins_json, anti_json, shot_sha, now))
            post_row = conn.execute("SELECT * FROM visual_genome_niches WHERE niche_key = ?", (niche_key,)).fetchone()
            post_sha = self._state_hash(dict(post_row) if post_row is not None else {})
            conn.execute("INSERT INTO visual_genome_snapshots VALUES (?, ?, ?, ?, ?, ?, ?)", (snap_id, niche_key, gid, pre_sha, post_sha, json.dumps(prev_dict, ensure_ascii=False), now))
            conn.commit()
        finally:
            conn.close()
        return {"snapshot_id": snap_id, "niche_key": niche_key, "genome_id": gid, "pre_snapshot_sha256": pre_sha, "post_snapshot_sha256": post_sha}

    def rollback_genome_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        """Revierte una celda MAP-Elites al estado exacto pre_snapshot_sha256."""
        conn = self._connect()
        try:
            snap = conn.execute("SELECT * FROM visual_genome_snapshots WHERE snapshot_id = ?", (snapshot_id,)).fetchone()
            if snap is None:
                raise KeyError(f"Snapshot not found: {snapshot_id}")
            niche_key = str(snap["niche_key"])
            prev_state = json.loads(str(snap["state_json"]) or "{}")
            expected_sha = str(snap["pre_snapshot_sha256"])
            if prev_state:
                conn.execute("INSERT OR REPLACE INTO visual_genome_niches VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (prev_state["niche_key"], prev_state["genome_id"], prev_state["design_mode"], prev_state["visual_paradigm"], float(prev_state["elo_rating"]), float(prev_state["bradley_terry_strength"]), float(prev_state["perceptual_score"]), prev_state["tokens_w3c_json"], prev_state["winning_patterns_json"], prev_state["rejected_antipatterns_json"], prev_state["screenshot_sha256"], prev_state["updated_at"]))
            else:
                conn.execute("DELETE FROM visual_genome_niches WHERE niche_key = ?", (niche_key,))
            conn.commit()
            cur = conn.execute("SELECT * FROM visual_genome_niches WHERE niche_key = ?", (niche_key,)).fetchone()
            restored_sha = self._state_hash(dict(cur) if cur is not None else {})
            return {"status": "ROLLED_BACK", "snapshot_id": snapshot_id, "niche_key": niche_key, "restored_sha256": restored_sha, "verified_exact": restored_sha == expected_sha}
        finally:
            conn.close()

    def get_status(self) -> Dict[str, Any]:
        conn = self._connect()
        try:
            niches = [dict(r) for r in conn.execute("SELECT niche_key, genome_id, elo_rating, bradley_terry_strength, perceptual_score FROM visual_genome_niches ORDER BY elo_rating DESC").fetchall()]
            matches_n = conn.execute("SELECT COUNT(*) FROM pairwise_matches").fetchone()[0]
            snaps_n = conn.execute("SELECT COUNT(*) FROM visual_genome_snapshots").fetchone()[0]
            return {"db_path": self.db_path, "niches_count": len(niches), "matches_count": int(matches_n), "snapshots_count": int(snaps_n), "niches": niches}
        finally:
            conn.close()


def recall_elite_genes(design_mode: str, limit: int = 2, repo_root: Optional[str] = None, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Recall ultra-rápido (< 5 ms) sin overhead si no existe DB."""
    if db_path:
        target = db_path
    else:
        root = os.path.abspath(repo_root) if repo_root else os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        target = os.path.join(root, ".aleph", "runtime", "visual_evolution.db")
    if not os.path.isfile(target):
        return []
    conn = sqlite3.connect(target, timeout=1.0)
    try:
        rows = conn.execute("SELECT genome_id, visual_paradigm, elo_rating, perceptual_score, winning_patterns_json FROM visual_genome_niches WHERE design_mode = ? ORDER BY elo_rating DESC LIMIT ?", (str(design_mode), max(1, int(limit)))).fetchall()
        return [{"genome_id": str(r[0]), "visual_paradigm": str(r[1]), "elo_rating": float(r[2]), "perceptual_score": float(r[3]), "winning_patterns": json.loads(str(r[4] or "[]"))} for r in rows]
    except Exception as exc:
        _ = exc
        return []
    finally:
        conn.close()


def cli_visual_evolve(argv: List[str]) -> int:
    sub = str(argv[0]) if argv else "status"
    eng = VisualEvolutionEngine()
    if sub == "status":
        print(json.dumps(eng.get_status(), indent=2, ensure_ascii=False))
        return 0
    if sub == "recall":
        print(json.dumps(recall_elite_genes(str(argv[1]) if len(argv) > 1 else "AVANT_GARDE_SOTY"), indent=2, ensure_ascii=False))
        return 0
    if sub == "rollback" and len(argv) > 1:
        print(json.dumps(eng.rollback_genome_snapshot(str(argv[1])), indent=2, ensure_ascii=False))
        return 0
    raise SystemExit("Usage: aleph_cli.py visual-evolve <status|recall|rollback> [arg]")
