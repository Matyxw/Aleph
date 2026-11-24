"""Fundición Omni-Studio: HDRI CC0, FFmpeg Cinema Scroll, Blender bpy/GLB y ADN W3C DTCG 2025.10."""
from __future__ import annotations

import functools
import glob
import hashlib
import http.server
import json
import os
import shutil
import subprocess
import tempfile
import threading
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

_DEFAULT_CACHE_DIR = os.path.join(os.path.expanduser("~"), ".aleph", "cache", "hdri")
_TOOLS_DIR = os.path.join(os.path.expanduser("~"), ".aleph", "tools")
_USER_AGENT = "ElAleph-Sovereign/33.0 (OmniStudio-Foundry)"
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


def find_ffmpeg_binary() -> Optional[str]:
    """Localiza ffmpeg.exe portable o en PATH."""
    for p in (os.path.join(_TOOLS_DIR, "ffmpeg", "bin", "ffmpeg.exe"), os.path.join(_TOOLS_DIR, "ffmpeg", "ffmpeg.exe")):
        if os.path.isfile(p):
            return p
    found = shutil.which("ffmpeg")
    return found if found and os.path.isfile(found) else None


def find_blender_binary() -> Optional[str]:
    """Localiza blender.exe portable, Program Files o PATH."""
    portable = os.path.join(_TOOLS_DIR, "blender", "blender.exe")
    if os.path.isfile(portable):
        return portable
    for pat in (os.path.join(_TOOLS_DIR, "blender", "*", "blender.exe"), os.path.join("C:\\", "Program Files", "Blender Foundation", "*", "blender.exe")):
        matches = sorted(glob.glob(pat), reverse=True)
        if matches and os.path.isfile(matches[0]):
            return matches[0]
    found = shutil.which("blender")
    return found if found and os.path.isfile(found) else None


def detect_media_backends() -> Dict[str, Any]:
    """Reporta backends locales y claves opcionales (solo booleano) sin exponer secretos."""
    ff_bin, bl_bin = find_ffmpeg_binary(), find_blender_binary()
    mcp_cfg = os.path.join(os.path.expanduser("~"), ".gemini", "config", "mcp_config.json")
    has_shadcn = False
    if os.path.isfile(mcp_cfg):
        try:
            has_shadcn = "shadcn" in (json.loads(Path(mcp_cfg).read_text(encoding="utf-8")).get("mcpServers") or {})
        except Exception as exc:
            _ = exc
    return {
        "blender_local": bl_bin is not None, "blender_path": bl_bin,
        "ffmpeg_local": ff_bin is not None, "ffmpeg_path": ff_bin,
        "node_portable": os.path.isfile(os.path.join(_TOOLS_DIR, "node", "node.exe")),
        "rtx_optix_ready": bl_bin is not None and shutil.which("nvidia-smi") is not None,
        "polyhaven_hdri": True, "shadcn_react_bits_mcp": has_shadcn,
        "gemini_imagen_veo": bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")),
        "fal_ai_3d_video": bool(os.environ.get("FAL_KEY")),
        "tripo_3d": bool(os.environ.get("TRIPO_API_KEY")), "meshy_3d": bool(os.environ.get("MESHY_API_KEY")),
    }


def enable_rtx_cycles(scene_var: str = "scene") -> str:
    """Devuelve snippet bpy para activar Cycles RTX OptiX/CUDA en GPU NVIDIA con fallback CPU."""
    s = (scene_var or "scene").strip() or "scene"
    return (
        f"import bpy\n{s}.render.engine = 'CYCLES'\nprefs = bpy.context.preferences.addons['cycles'].preferences\n"
        "for backend in ('OPTIX', 'CUDA'):\n    try:\n        prefs.compute_device_type = backend\n        prefs.get_devices()\n"
        "        gpus = [d for d in prefs.devices if d.type != 'CPU']\n        if gpus:\n            for d in prefs.devices: d.use = True\n"
        f"            {s}.cycles.device = 'GPU'\n            break\n    except Exception as exc:\n        _ = exc\n"
    )


def stitch_contact_sheet(image_paths: List[str], output_path: str, cols: int = 3, tile_width: int = 640) -> Dict[str, Any]:
    """Ensambla hoja de contacto (turntable o motion filmstrip) vía ffmpeg tile."""
    ff_bin = find_ffmpeg_binary()
    if ff_bin is None:
        raise FileNotFoundError("ffmpeg binary not found in portable tools or PATH")
    if image_paths is None:
        raise ValueError("image_paths must not be None")
    valid = [os.path.abspath(str(p)) for p in image_paths if os.path.isfile(str(p))]
    if not valid:
        raise FileNotFoundError("No valid input images for stitch_contact_sheet")
    c, r, w = max(1, int(cols)), max(1, (len(valid) + max(1, int(cols)) - 1) // max(1, int(cols))), max(64, int(tile_width))
    out_abs = os.path.abspath(str(output_path))
    os.makedirs(os.path.dirname(out_abs), exist_ok=True)
    tmp_dir = tempfile.mkdtemp(prefix="aleph_sheet_")
    try:
        for idx, src_p in enumerate(valid, 1):
            shutil.copy2(src_p, os.path.join(tmp_dir, f"t_{idx:04d}.png"))
        cmd = [ff_bin, "-y", "-i", os.path.join(tmp_dir, "t_%04d.png"), "-vf", f"scale={w}:-2:flags=lanczos,tile={c}x{r}", "-frames:v", "1", out_abs]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        if proc.returncode != 0 or not os.path.isfile(out_abs):
            raise RuntimeError(f"ffmpeg tile failed ({proc.returncode}): {proc.stderr[-300:]}")
        raw = Path(out_abs).read_bytes()
        return {"status": "CONTACT_SHEET_OK", "output_path": out_abs, "tiles": len(valid), "cols": c, "rows": r, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


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
    """Descarga o reutiliza desde caché un HDRI CC0 de Poly Haven y devuelve metadata + SHA-256."""
    safe_preset, safe_res = (preset or "studio_small_09").strip(), (resolution or "1k").strip().lower()
    filename = f"{safe_preset}_{safe_res}.hdr"
    resolved_cache = os.path.abspath(cache_dir or _DEFAULT_CACHE_DIR)
    os.makedirs(resolved_cache, exist_ok=True)
    cache_path, status = os.path.join(resolved_cache, filename), "CACHE_HIT"
    if not os.path.isfile(cache_path) or os.path.getsize(cache_path) < _MIN_VALID_HDR_BYTES:
        with urllib.request.urlopen(urllib.request.Request(f"https://api.polyhaven.com/files/{safe_preset}", headers={"User-Agent": _USER_AGENT}), timeout=25) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        hdr_url = _resolve_hdr_url(payload if isinstance(payload, dict) else {}, safe_res)
        fd, tmp_file = tempfile.mkstemp(prefix="aleph_hdr_", suffix=".hdr", dir=resolved_cache)
        os.close(fd)
        try:
            with urllib.request.urlopen(urllib.request.Request(hdr_url, headers={"User-Agent": _USER_AGENT}), timeout=60) as dl_resp, open(tmp_file, "wb") as out_f:
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
        resolved_dest = os.path.abspath(dest_dir)
        os.makedirs(resolved_dest, exist_ok=True)
        dest_path = os.path.join(resolved_dest, filename)
        if os.path.normcase(os.path.abspath(cache_path)) != os.path.normcase(dest_path):
            shutil.copy2(cache_path, dest_path)
    raw = Path(dest_path).read_bytes()
    return {"status": status, "preset": safe_preset, "resolution": safe_res, "filename": filename, "cache_path": cache_path, "dest_path": dest_path, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), "license": "CC0"}


def encode_cinema_scroll_sequence(input_source: str, output_dir: str, fps: int = 24, width: int = 1440, quality: int = 82) -> Dict[str, Any]:
    """Convierte video o secuencia de PNGs en fotogramas frame_XXXX.webp + manifest.json con ffmpeg real."""
    ff_bin = find_ffmpeg_binary()
    if ff_bin is None:
        raise FileNotFoundError("ffmpeg binary not found in portable tools or PATH")
    src = os.path.abspath(str(input_source)) if ("%" not in str(input_source) and os.path.exists(str(input_source))) else str(input_source)
    out_abs = os.path.abspath(output_dir)
    os.makedirs(out_abs, exist_ok=True)
    concat_file: Optional[str] = None
    try:
        if os.path.isdir(src):
            if os.path.isfile(os.path.join(src, "frame_0001.png")):
                cmd = [ff_bin, "-y", "-framerate", str(int(fps)), "-i", os.path.join(src, "frame_%04d.png")]
            else:
                pngs = sorted(glob.glob(os.path.join(src, "*.png")))
                if not pngs:
                    raise FileNotFoundError(f"No PNG frames found in {src}")
                fd, concat_file = tempfile.mkstemp(prefix="aleph_concat_", suffix=".txt", dir=out_abs)
                os.close(fd)
                dur = round(1.0 / max(1, int(fps)), 6)
                Path(concat_file).write_text("".join(f"file '{p.replace(chr(39), chr(39)+chr(92)+chr(39)+chr(39))}'\nduration {dur}\n" for p in pngs), encoding="utf-8")
                cmd = [ff_bin, "-y", "-f", "concat", "-safe", "0", "-i", concat_file]
            vf = f"scale={int(width)}:-2:flags=lanczos"
        elif "%" in src:
            cmd, vf = [ff_bin, "-y", "-framerate", str(int(fps)), "-i", src], f"scale={int(width)}:-2:flags=lanczos"
        else:
            if not os.path.isfile(src):
                raise FileNotFoundError(f"Input media not found: {input_source}")
            cmd, vf = [ff_bin, "-y", "-i", src], f"fps={int(fps)},scale={int(width)}:-2:flags=lanczos"
        cmd.extend(["-vf", vf, "-c:v", "libwebp", "-lossless", "0", "-compression_level", "4", "-q:v", str(int(quality)), "-an", os.path.join(out_abs, "frame_%04d.webp")])
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if proc.returncode != 0:
            raise RuntimeError(f"ffmpeg failed ({proc.returncode}): {proc.stderr[-400:]}")
    finally:
        if concat_file and os.path.isfile(concat_file):
            os.remove(concat_file)

    webp_files = sorted(glob.glob(os.path.join(out_abs, "frame_*.webp")))
    if not webp_files:
        raise RuntimeError(f"ffmpeg generated 0 .webp frames in {out_abs}")
    manifest = {"frame_count": len(webp_files), "width": int(width), "fps": int(fps), "quality": int(quality), "total_bytes": sum(os.path.getsize(f) for f in webp_files), "frames": [os.path.basename(f) for f in webp_files]}
    manifest_path = os.path.join(out_abs, "manifest.json")
    Path(manifest_path).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {**manifest, "manifest_path": manifest_path, "output_dir": out_abs}


def run_blender_studio_job(script_path: str, output_path: str, timeout_sec: int = 180, extra_args: Optional[List[str]] = None) -> Dict[str, Any]:
    """Ejecuta script bpy headless en Blender real y verifica el artefacto (.glb o secuencia)."""
    bl_bin = find_blender_binary()
    if bl_bin is None:
        raise FileNotFoundError("blender.exe binary not found in portable tools or PATH")
    scr_abs = os.path.abspath(str(script_path))
    if not os.path.isfile(scr_abs):
        raise FileNotFoundError(f"Blender script not found: {script_path}")
    out_abs = os.path.abspath(str(output_path))
    cmd = [bl_bin, "--background", "--factory-startup", "--python-exit-code", "1", "--python", scr_abs] + (["--", *(str(a) for a in extra_args)] if extra_args else [])
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=int(timeout_sec))
    if proc.returncode != 0:
        raise RuntimeError(f"Blender exited {proc.returncode}: {proc.stderr[-500:] or proc.stdout[-500:]}")
    if os.path.isfile(out_abs):
        raw = Path(out_abs).read_bytes()
        if not raw:
            raise RuntimeError(f"Blender output file is empty: {out_abs}")
        return {"status": "BLENDER_JOB_OK", "blender": bl_bin, "output_path": out_abs, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    if os.path.isdir(out_abs):
        files = [os.path.join(out_abs, f) for f in sorted(os.listdir(out_abs)) if os.path.isfile(os.path.join(out_abs, f))]
        if not files:
            raise RuntimeError(f"Blender output directory is empty: {out_abs}")
        return {"status": "BLENDER_JOB_OK", "blender": bl_bin, "output_path": out_abs, "file_count": len(files), "total_bytes": sum(os.path.getsize(f) for f in files)}
    raise FileNotFoundError(f"Expected Blender output missing: {out_abs}")


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
        httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=serve_dir))
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        url = f"http://127.0.0.1:{int(httpd.server_address[1])}/{'index.html' if os.path.isdir(abs_p) else os.path.basename(abs_p)}"
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
    h1_px, body_px = float(raw_dna.get("h1Px") or 36.0), max(1.0, float(raw_dna.get("bodyPx") or 16.0))
    return {
        "$schema": "https://tr.designtokens.org/format/2025.10/", "source": raw,
        "color": {"background": {"$type": "color", "$value": str(raw_dna.get("bgColor") or "rgb(8,9,11)")}, "surface": {"$type": "color", "$value": str(raw_dna.get("surfaceColor") or "rgb(17,19,24)")}, "ink-primary": {"$type": "color", "$value": str(raw_dna.get("inkPrimary") or "rgb(244,245,247)")}, "ink-secondary": {"$type": "color", "$value": str(raw_dna.get("inkSecondary") or "rgb(156,164,178)")}, "accent": {"$type": "color", "$value": str(raw_dna.get("accentColor") or "rgb(255,77,0)")}},
        "typography": {"display": {"$type": "fontFamily", "$value": str(raw_dna.get("h1Font") or "Space Grotesk")}, "body": {"$type": "fontFamily", "$value": str(raw_dna.get("bodyFont") or "Plus Jakarta Sans")}, "h1-size": {"$type": "dimension", "$value": f"{round(h1_px, 2)}px"}, "h2-size": {"$type": "dimension", "$value": f"{round(float(raw_dna.get('h2Px') or 28.0), 2)}px"}, "body-size": {"$type": "dimension", "$value": f"{round(body_px, 2)}px"}},
        "dimension": {"radius-primary": {"$type": "dimension", "$value": str((raw_dna.get("dominantRadii") or ["8px"])[0])}},
        "transition": {"duration-ui": {"$type": "duration", "$value": str((raw_dna.get("transitionDurations") or ["180ms"])[0])}, "easing-ui": {"$type": "cubicBezier", "$value": str(raw_dna.get("easingSample") or "cubic-bezier(0.23, 1, 0.32, 1)")}},
        "summary_metrics": {"typography_scale_ratio": round(h1_px / body_px, 3), "loaded_fonts": list(raw_dna.get("loadedFonts") or []), "has_canvas": bool(raw_dna.get("hasCanvas")), "has_backdrop_filter": bool(raw_dna.get("hasBackdropFilter"))},
    }


def cli_fetch_hdri(argv: List[str]) -> int:
    preset = str(argv[0]) if len(argv) >= 1 and not str(argv[0]).startswith("--") else "studio_small_09"
    dest_dir = str(argv[1]) if len(argv) >= 2 and not str(argv[1]).startswith("--") else ""
    res = str(argv[argv.index("--res") + 1]) if "--res" in argv and argv.index("--res") + 1 < len(argv) else "1k"
    print(json.dumps(fetch_polyhaven_studio_hdri(preset=preset, resolution=res, dest_dir=dest_dir), indent=2, ensure_ascii=False))
    return 0
def cli_encode_scroll(argv: List[str]) -> int:
    if len(argv) < 2:
        raise SystemExit("Usage: aleph_cli.py encode-scroll <input_video_or_dir> <output_dir> [--fps 24] [--width 1440] [--quality 82]")
    fps = int(argv[argv.index("--fps") + 1]) if "--fps" in argv and argv.index("--fps") + 1 < len(argv) else 24
    width = int(argv[argv.index("--width") + 1]) if "--width" in argv and argv.index("--width") + 1 < len(argv) else 1440
    quality = int(argv[argv.index("--quality") + 1]) if "--quality" in argv and argv.index("--quality") + 1 < len(argv) else 82
    print(json.dumps(encode_cinema_scroll_sequence(str(argv[0]), str(argv[1]), fps=fps, width=width, quality=quality), indent=2, ensure_ascii=False))
    return 0
def cli_extract_dna(argv: List[str]) -> int:
    if not argv:
        raise SystemExit("Usage: aleph_cli.py extract-dna <url_or_html_path>")
    print(json.dumps(extract_live_design_dna(str(argv[0])), indent=2, ensure_ascii=False))
    return 0
def cli_studio_status() -> int:
    data = detect_media_backends()
    if data is None:
        return 1
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return 0
