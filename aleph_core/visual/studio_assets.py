"""Descargador y caché determinista de HDRIs CC0 de estudio desde Poly Haven."""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

_DEFAULT_CACHE_DIR = os.path.join(os.path.expanduser("~"), ".aleph", "cache", "hdri")
_USER_AGENT = "ElAleph-Sovereign/33.0 (PolyHaven-CC0-StudioAssets)"
_MIN_VALID_HDR_BYTES = 16384


def _resolve_hdr_url(files_payload: Dict[str, Any], resolution: str) -> str:
    hdr_block = files_payload.get("hdri")
    if not isinstance(hdr_block, dict):
        hdr_block = files_payload.get("hdr")
    if not isinstance(hdr_block, dict):
        raise ValueError("Poly Haven payload missing 'hdri' section")
    for res_candidate in (resolution, "1k", "2k", "4k"):
        res_entry = hdr_block.get(res_candidate)
        if isinstance(res_entry, dict):
            hdr_info = res_entry.get("hdr")
            if isinstance(hdr_info, dict) and hdr_info.get("url"):
                return str(hdr_info.get("url"))
    raise ValueError(f"No .hdr download URL found for resolution {resolution}")


def fetch_polyhaven_studio_hdri(
    preset: str = "studio_small_09",
    resolution: str = "1k",
    dest_dir: str = "",
    cache_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Descarga o reutiliza un HDRI CC0 de Poly Haven hacia caché local y dest_dir."""
    safe_preset = (preset or "studio_small_09").strip()
    safe_res = (resolution or "1k").strip().lower()
    filename = f"{safe_preset}_{safe_res}.hdr"
    resolved_cache = os.path.abspath(cache_dir or _DEFAULT_CACHE_DIR)
    os.makedirs(resolved_cache, exist_ok=True)
    cache_path = os.path.join(resolved_cache, filename)

    status = "CACHE_HIT"
    source_url = f"https://api.polyhaven.com/files/{safe_preset}"
    if not os.path.isfile(cache_path) or os.path.getsize(cache_path) < _MIN_VALID_HDR_BYTES:
        req = urllib.request.Request(source_url, headers={"User-Agent": _USER_AGENT})
        with urllib.request.urlopen(req, timeout=25) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Invalid Poly Haven API JSON response")
        hdr_url = _resolve_hdr_url(payload, safe_res)
        dl_req = urllib.request.Request(hdr_url, headers={"User-Agent": _USER_AGENT})
        fd, tmp_file = tempfile.mkstemp(prefix="aleph_hdr_", suffix=".hdr", dir=resolved_cache)
        os.close(fd)
        try:
            with urllib.request.urlopen(dl_req, timeout=60) as dl_resp, open(tmp_file, "wb") as out_f:
                shutil.copyfileobj(dl_resp, out_f)
            if os.path.getsize(tmp_file) < _MIN_VALID_HDR_BYTES:
                raise IOError(f"Downloaded HDRI unexpectedly small: {tmp_file}")
            os.replace(tmp_file, cache_path)
            status = "DOWNLOADED"
        except Exception as exc:
            if os.path.isfile(tmp_file):
                os.remove(tmp_file)
            raise RuntimeError(f"Failed downloading HDRI {safe_preset}: {exc}") from exc

    dest_path = cache_path
    if dest_dir and str(dest_dir).strip():
        resolved_dest_dir = os.path.abspath(dest_dir)
        os.makedirs(resolved_dest_dir, exist_ok=True)
        dest_path = os.path.join(resolved_dest_dir, filename)
        if os.path.normcase(os.path.abspath(cache_path)) != os.path.normcase(dest_path):
            shutil.copy2(cache_path, dest_path)

    return {
        "status": status,
        "preset": safe_preset,
        "resolution": safe_res,
        "filename": filename,
        "cache_path": cache_path,
        "dest_path": dest_path,
        "bytes": int(Path(dest_path).stat().st_size),
        "license": "CC0",
    }


def cli_fetch_hdri(argv: List[str]) -> int:
    """Subcomando CLI para `aleph_cli.py fetch-hdri [preset] [dest_dir] [--res 1k]`."""
    preset = "studio_small_09"
    dest_dir = ""
    resolution = "1k"
    positional: List[str] = []
    idx = 0
    while idx < len(argv):
        tok = str(argv[idx])
        if tok == "--res" and idx + 1 < len(argv):
            resolution = str(argv[idx + 1])
            idx += 2
            continue
        if not tok.startswith("--"):
            positional.append(tok)
        idx += 1
    if len(positional) >= 1:
        preset = positional[0]
    if len(positional) >= 2:
        dest_dir = positional[1]
    report = fetch_polyhaven_studio_hdri(preset=preset, resolution=resolution, dest_dir=dest_dir)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0
