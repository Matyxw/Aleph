"""Assets CC0 de Poly Haven y extractor de ADN visual W3C DTCG 2025.10."""
from __future__ import annotations

import functools
import hashlib
import http.server
import json
import os
import shutil
import tempfile
import threading
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

_DEFAULT_CACHE_DIR = os.path.join(os.path.expanduser("~"), ".aleph", "cache", "hdri")
_USER_AGENT = "ElAleph-Sovereign/33.0 (PolyHaven-CC0-StudioAssets)"
_MIN_VALID_HDR_BYTES = 16384

_DNA_EVAL_JS = """async () => {
  try { if (document.fonts && document.fonts.ready) await document.fonts.ready; } catch (_e) {}
  const loadedFonts = document.fonts ? Array.from(document.fonts).filter(f => f.status === 'loaded' && f.family).map(f => f.family).filter((v, i, a) => a.indexOf(v) === i) : [];
  const gs = (s) => { const el = document.querySelector(s); return el ? window.getComputedStyle(el) : null; };
  const bSt = gs('body'), h1St = gs('h1') || bSt, h2St = gs('h2') || h1St, cardSt = gs('[class*="card"], [class*="panel"], section') || bSt, btnSt = gs('button, a[class*="btn"]') || h1St;
  const radii = [], durs = [];
  let hasBackdropBlur = false;
  for (const el of Array.from(document.querySelectorAll('button, div, section, a')).slice(0, 60)) {
    const st = window.getComputedStyle(el);
    if (st.borderRadius && st.borderRadius !== '0px' && radii.length < 4) radii.push(st.borderRadius.split(' ')[0]);
    if (st.transitionDuration && st.transitionDuration !== '0s' && durs.length < 4) durs.push(st.transitionDuration.split(',')[0].trim());
    const bf = st.backdropFilter || st.webkitBackdropFilter || '';
    if (bf && bf !== 'none') hasBackdropBlur = true;
  }
  return {
    loadedFonts, hasCanvas: document.querySelectorAll('canvas').length > 0, hasBackdropFilter: hasBackdropBlur,
    h1Px: h1St ? (parseFloat(h1St.fontSize) || 36) : 36, h2Px: h2St ? (parseFloat(h2St.fontSize) || 28) : 28, bodyPx: bSt ? (parseFloat(bSt.fontSize) || 16) : 16,
    h1Font: h1St ? h1St.fontFamily : 'Space Grotesk', bodyFont: bSt ? bSt.fontFamily : 'Plus Jakarta Sans',
    bgColor: bSt ? bSt.backgroundColor : 'rgb(8,9,11)', surfaceColor: cardSt ? cardSt.backgroundColor : 'rgb(17,19,24)',
    inkPrimary: h1St ? h1St.color : 'rgb(244,245,247)', inkSecondary: bSt ? bSt.color : 'rgb(156,164,178)',
    accentColor: btnSt && btnSt.backgroundColor !== 'rgba(0, 0, 0, 0)' ? btnSt.backgroundColor : (btnSt ? btnSt.color : 'rgb(255,77,0)'),
    dominantRadii: radii, transitionDurations: durs, easingSample: btnSt ? btnSt.transitionTimingFunction : 'ease',
  };
}"""


def _resolve_hdr_url(files_payload: Dict[str, Any], resolution: str) -> str:
    hdr_block = files_payload.get("hdri") if isinstance(files_payload.get("hdri"), dict) else files_payload.get("hdr")
    if not isinstance(hdr_block, dict):
        raise ValueError("Poly Haven payload missing 'hdri' section")
    for res_candidate in (resolution, "1k", "2k", "4k"):
        res_entry = hdr_block.get(res_candidate)
        if isinstance(res_entry, dict) and isinstance(res_entry.get("hdr"), dict) and res_entry.get("hdr", {}).get("url"):
            return str(res_entry.get("hdr", {}).get("url"))
    raise ValueError(f"No .hdr download URL found for resolution {resolution}")


def fetch_polyhaven_studio_hdri(preset: str = "studio_small_09", resolution: str = "1k", dest_dir: str = "", cache_dir: Optional[str] = None) -> Dict[str, Any]:
    """Descarga o reutiliza un HDRI CC0 de Poly Haven hacia caché local y dest_dir."""
    safe_preset = (preset or "studio_small_09").strip()
    safe_res = (resolution or "1k").strip().lower()
    filename = f"{safe_preset}_{safe_res}.hdr"
    resolved_cache = os.path.abspath(cache_dir or _DEFAULT_CACHE_DIR)
    os.makedirs(resolved_cache, exist_ok=True)
    cache_path = os.path.join(resolved_cache, filename)
    status = "CACHE_HIT"

    if not os.path.isfile(cache_path) or os.path.getsize(cache_path) < _MIN_VALID_HDR_BYTES:
        req = urllib.request.Request(f"https://api.polyhaven.com/files/{safe_preset}", headers={"User-Agent": _USER_AGENT})
        with urllib.request.urlopen(req, timeout=25) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        hdr_url = _resolve_hdr_url(payload if isinstance(payload, dict) else {}, safe_res)
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

    file_bytes = Path(dest_path).read_bytes()
    return {"status": status, "preset": safe_preset, "resolution": safe_res, "filename": filename, "cache_path": cache_path, "dest_path": dest_path, "bytes": len(file_bytes), "sha256": hashlib.sha256(file_bytes).hexdigest(), "license": "CC0"}


def extract_live_design_dna(target_url_or_path: str, timeout_ms: int = 15000) -> Dict[str, Any]:
    """Abre URL o HTML local en Chromium 1440x900 y destila tokens W3C DTCG 2025.10."""
    from playwright.sync_api import sync_playwright

    raw = str(target_url_or_path or "").strip()
    httpd: Optional[http.server.ThreadingHTTPServer] = None
    if raw.startswith(("http://", "https://", "file://", "data:")):
        url = raw
    else:
        abs_p = os.path.abspath(raw)
        if not os.path.exists(abs_p):
            raise FileNotFoundError(f"DNA target not found: {target_url_or_path}")
        serve_dir = abs_p if os.path.isdir(abs_p) else os.path.dirname(abs_p)
        entry = "index.html" if os.path.isdir(abs_p) else os.path.basename(abs_p)
        httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=serve_dir))
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        url = f"http://127.0.0.1:{int(httpd.server_address[1])}/{entry}"

    raw_dna: Dict[str, Any] = {}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--no-sandbox", "--enable-webgl", "--ignore-gpu-blocklist"])
            try:
                page = browser.new_page(viewport={"width": 1440, "height": 900})
                page.set_default_timeout(timeout_ms)
                page.goto(url, wait_until="load", timeout=timeout_ms)
                ev = page.evaluate(_DNA_EVAL_JS)
                if isinstance(ev, dict):
                    raw_dna = ev
            finally:
                browser.close()
    finally:
        if httpd is not None:
            httpd.shutdown()
            httpd.server_close()

    h1_px = float(raw_dna.get("h1Px") or 36.0)
    body_px = max(1.0, float(raw_dna.get("bodyPx") or 16.0))
    radii = list(raw_dna.get("dominantRadii") or ["8px"])
    durs = list(raw_dna.get("transitionDurations") or ["180ms"])
    return {
        "$schema": "https://tr.designtokens.org/format/2025.10/",
        "source": raw,
        "color": {
            "background": {"$type": "color", "$value": str(raw_dna.get("bgColor") or "rgb(8,9,11)")},
            "surface": {"$type": "color", "$value": str(raw_dna.get("surfaceColor") or "rgb(17,19,24)")},
            "ink-primary": {"$type": "color", "$value": str(raw_dna.get("inkPrimary") or "rgb(244,245,247)")},
            "ink-secondary": {"$type": "color", "$value": str(raw_dna.get("inkSecondary") or "rgb(156,164,178)")},
            "accent": {"$type": "color", "$value": str(raw_dna.get("accentColor") or "rgb(255,77,0)")},
        },
        "typography": {
            "display": {"$type": "fontFamily", "$value": str(raw_dna.get("h1Font") or "Space Grotesk")},
            "body": {"$type": "fontFamily", "$value": str(raw_dna.get("bodyFont") or "Plus Jakarta Sans")},
            "h1-size": {"$type": "dimension", "$value": f"{round(h1_px, 2)}px"},
            "h2-size": {"$type": "dimension", "$value": f"{round(float(raw_dna.get('h2Px') or 28.0), 2)}px"},
            "body-size": {"$type": "dimension", "$value": f"{round(body_px, 2)}px"},
        },
        "dimension": {"radius-primary": {"$type": "dimension", "$value": str(radii[0])}},
        "transition": {"duration-ui": {"$type": "duration", "$value": str(durs[0])}, "easing-ui": {"$type": "cubicBezier", "$value": str(raw_dna.get("easingSample") or "cubic-bezier(0.23, 1, 0.32, 1)")}},
        "summary_metrics": {"typography_scale_ratio": round(h1_px / body_px, 3), "loaded_fonts": list(raw_dna.get("loadedFonts") or []), "has_canvas": bool(raw_dna.get("hasCanvas")), "has_backdrop_filter": bool(raw_dna.get("hasBackdropFilter"))},
    }


def cli_fetch_hdri(argv: List[str]) -> int:
    preset = str(argv[0]) if len(argv) >= 1 and not str(argv[0]).startswith("--") else "studio_small_09"
    dest_dir = str(argv[1]) if len(argv) >= 2 and not str(argv[1]).startswith("--") else ""
    res = str(argv[argv.index("--res") + 1]) if "--res" in argv and argv.index("--res") + 1 < len(argv) else "1k"
    print(json.dumps(fetch_polyhaven_studio_hdri(preset=preset, resolution=res, dest_dir=dest_dir), indent=2, ensure_ascii=False))
    return 0


def cli_extract_dna(argv: List[str]) -> int:
    if not argv:
        raise SystemExit("Usage: aleph_cli.py extract-dna <url_or_html_path>")
    print(json.dumps(extract_live_design_dna(str(argv[0])), indent=2, ensure_ascii=False))
    return 0
