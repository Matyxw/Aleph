"""
Arnés A/B: ¿tu agente rinde mejor CON las reglas de El Aleph que SIN ellas?

Para cada tarea (JSONL) y cada repetición, corre el agente dos veces en copias limpias del
directorio de trabajo (orden aleatorio): brazo `with` y brazo `without`. El éxito lo decide un
comando de verificación externo (p. ej. `pytest -q`), nunca el propio agente.

Tu agente recibe:
  * el prompt por stdin y en la variable AGENT_PROMPT
  * ALEPH_ARM=with|without  -> TU script decide si activa o no la config/reglas de Aleph
  * (opcional) puede imprimir como última línea de stdout un JSON {"tokens": N}

Uso:
  python3 -m ab_eval.ab_harness --tasks ab_eval/tasks.example.jsonl \
      --agent-cmd "./mi_agente.sh" --reps 3 --out resultados.csv

Formato de tarea:  {"id": "t1", "prompt": "...", "workdir": "ruta/al/repo", "verify": "pytest -q"}
Sin shell: `--agent-cmd` y `verify` se parten con shlex (si necesitas pipes, ponlos en un script).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import shlex
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ARMS = ("with", "without")
MIN_PAIRS_CONCLUSIVE = 20


def mcnemar_exact_p(b: int, c: int) -> float:
    """p bilateral exacto (binomial, p=0.5) sobre los pares discordantes b y c."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def _tokens_from(stdout: str) -> Optional[int]:
    for line in reversed(stdout.strip().splitlines()[-3:]):
        try:
            val = json.loads(line)
            if isinstance(val, dict) and isinstance(val.get("tokens"), int):
                return val["tokens"]
        except ValueError:
            continue
    return None


def run_arm(task: Dict[str, Any], arm: str, agent_cmd: str, timeout: int) -> Dict[str, Any]:
    src = Path(task["workdir"]).resolve()
    with tempfile.TemporaryDirectory(prefix=f"ab_{arm}_") as tmp:
        work = Path(tmp) / "work"
        shutil.copytree(src, work, ignore=shutil.ignore_patterns(".git", "__pycache__", "node_modules"))
        env = dict(os.environ, ALEPH_ARM=arm, AGENT_PROMPT=task["prompt"])
        t0 = time.perf_counter()
        agent_rc, tokens, timed_out = None, None, False
        try:
            _posix = os.name != "nt"
            r = subprocess.run(shlex.split(agent_cmd, posix=_posix), cwd=work, env=env, input=task["prompt"],
                               capture_output=True, text=True, timeout=timeout)
            agent_rc, tokens = r.returncode, _tokens_from(r.stdout)
        except subprocess.TimeoutExpired:
            timed_out = True
        elapsed = time.perf_counter() - t0
        try:
            v = subprocess.run(shlex.split(task["verify"], posix=(os.name != "nt")), cwd=work, capture_output=True, text=True, timeout=timeout)
            success = v.returncode == 0 and not timed_out
        except subprocess.TimeoutExpired:
            success = False
    return {"task": task["id"], "arm": arm, "success": int(success), "agent_rc": agent_rc,
            "timed_out": int(timed_out), "seconds": round(elapsed, 3), "tokens": tokens}


def summarize(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_pair: Dict[tuple, Dict[str, Dict[str, Any]]] = {}
    for r in rows:
        by_pair.setdefault((r["task"], r["rep"]), {})[r["arm"]] = r
    b = c = both = neither = 0
    for pair in by_pair.values():
        if len(pair) != 2:
            continue
        w, wo = pair["with"]["success"], pair["without"]["success"]
        b += int(w and not wo)
        c += int(wo and not w)
        both += int(w and wo)
        neither += int(not w and not wo)
    out: Dict[str, Any] = {"pairs": b + c + both + neither, "with_only": b, "without_only": c,
                           "both": both, "neither": neither, "mcnemar_p": mcnemar_exact_p(b, c)}
    for arm in ARMS:
        sel = [r for r in rows if r["arm"] == arm]
        toks = [r["tokens"] for r in sel if r["tokens"] is not None]
        out[arm] = {"n": len(sel),
                    "success_rate": round(sum(r["success"] for r in sel) / len(sel), 4) if sel else None,
                    "median_seconds": round(statistics.median(r["seconds"] for r in sel), 3) if sel else None,
                    "median_tokens": statistics.median(toks) if toks else None}
    if out["pairs"] < MIN_PAIRS_CONCLUSIVE:
        out["verdict"] = f"NO CONCLUYENTE: {out['pairs']} pares (< {MIN_PAIRS_CONCLUSIVE})."
    elif out["mcnemar_p"] < 0.05:
        better = "CON reglas" if b > c else "SIN reglas"
        out["verdict"] = f"Diferencia significativa (p={out['mcnemar_p']:.3f}): mejor {better}."
    else:
        out["verdict"] = f"Sin diferencia detectable (p={out['mcnemar_p']:.3f})."
    return out


def run(tasks_path: Path, agent_cmd: str, reps: int, timeout: int, seed: int, out_csv: Optional[Path]) -> Dict[str, Any]:
    tasks = [json.loads(l) for l in tasks_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    rng = random.Random(seed)
    rows: List[Dict[str, Any]] = []
    for task in tasks:
        for rep in range(reps):
            order = list(ARMS)
            rng.shuffle(order)
            for arm in order:
                row = run_arm(task, arm, agent_cmd, timeout)
                row["rep"] = rep
                rows.append(row)
    if out_csv:
        with out_csv.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["task", "rep", "arm", "success", "agent_rc", "timed_out", "seconds", "tokens"])
            w.writeheader()
            w.writerows(rows)
    return summarize(rows)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tasks", required=True, type=Path)
    ap.add_argument("--agent-cmd", required=True)
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args(argv)
    print(json.dumps(run(a.tasks, a.agent_cmd, a.reps, a.timeout, a.seed, a.out), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
