"""Auditor visual multiviewport real en Chromium headless (import lazy de Playwright)."""
from __future__ import annotations

import datetime as _dt
import functools
import http.server
import os
import shutil
import tempfile
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

VIEWPORTS: Tuple[Tuple[str, int, int], ...] = (
    ("mobile_390", 390, 844),
    ("desktop_1440", 1440, 900),
    ("ultrawide_2560", 2560, 1440),
)

_DOM_EVAL_JS = """(vpName) => {
  const vw = window.innerWidth || document.documentElement.clientWidth || 0;
  const docSw = document.documentElement ? document.documentElement.scrollWidth : 0;
  const bodySw = document.body ? document.body.scrollWidth : 0;
  const overflowPx = Math.max(0, docSw - vw, bodySw - vw);
  const overflowSelectors = [];
  if (overflowPx > 0) {
    const allEls = document.querySelectorAll('body *');
    for (let i = 0; i < allEls.length && overflowSelectors.length < 12; i++) {
      const el = allEls[i];
      const st = window.getComputedStyle(el);
      if (st.display === 'none' || st.visibility === 'hidden') continue;
      const r = el.getBoundingClientRect();
      if (r.right > vw + 1 || el.scrollWidth > vw + 1) {
        const idPart = el.id ? '#' + el.id : '';
        const cls = typeof el.className === 'string' && el.className.trim()
          ? '.' + el.className.trim().split(/\\s+/)[0] : '';
        overflowSelectors.push(el.tagName.toLowerCase() + idPart + cls);
      }
    }
  }
  const brokenImages = [];
  for (const img of document.querySelectorAll('img')) {
    if (img.complete && img.naturalWidth === 0) {
      brokenImages.push(img.getAttribute('src') || img.id || img.alt || 'img');
    }
  }
  const parseColor = (s) => {
    if (!s || s === 'transparent') return null;
    const m = s.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([\\d.]+))?\\)/);
    if (!m) return null;
    return {r: +m[1], g: +m[2], b: +m[3], a: m[4] !== undefined ? +m[4] : 1};
  };
  const lin = (c) => { const x = c / 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); };
  const lum = (rgb) => 0.2126 * lin(rgb.r) + 0.7152 * lin(rgb.g) + 0.0722 * lin(rgb.b);
  const contrast = (c1, c2) => {
    const l1 = lum(c1), l2 = lum(c2);
    return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
  };
  const resolveBg = (el) => {
    let cur = el;
    while (cur) {
      const c = parseColor(window.getComputedStyle(cur).backgroundColor);
      if (c && c.a >= 0.85) return c;
      cur = cur.parentElement;
    }
    return {r: 255, g: 255, b: 255, a: 1};
  };
  const contrastViolations = [];
  const textEls = document.querySelectorAll('h1,h2,h3,h4,h5,h6,p,span,a,button,label,li,td,th,code');
  for (const el of textEls) {
    if (contrastViolations.length >= 12) break;
    const txt = (el.innerText || '').trim();
    if (!txt) continue;
    const hasOwnText = Array.from(el.childNodes).some(n => n.nodeType === 3 && n.textContent.trim().length > 0);
    if (!hasOwnText && el.children.length > 0) continue;
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) continue;
    const st = window.getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden' || parseFloat(st.opacity) < 0.1) continue;
    const fg = parseColor(st.color);
    const bg = resolveBg(el);
    if (!fg || !bg) continue;
    const fz = parseFloat(st.fontSize) || 16;
    const fw = parseInt(st.fontWeight, 10) || 400;
    const threshold = (fz >= 24 || (fz >= 18.67 && fw >= 700)) ? 3.0 : 4.5;
    const ratio = contrast(fg, bg);
    if (ratio < threshold) {
      contrastViolations.push({
        viewport: vpName,
        selector: el.tagName.toLowerCase() + (el.id ? '#' + el.id : ''),
        ratio: Math.round(ratio * 100) / 100,
        threshold,
      });
    }
  }
  let animationsDetected = (typeof document.getAnimations === 'function') ? document.getAnimations().length : 0;
  for (const el of document.querySelectorAll('*')) {
    const st = window.getComputedStyle(el);
    if (st.animationName && st.animationName !== 'none' && parseFloat(st.animationDuration || '0') > 0) {
      animationsDetected += 1;
      break;
    }
  }
  let hasReducedMediaRule = false;
  for (const sheet of Array.from(document.styleSheets || [])) {
    try {
      for (const rule of Array.from(sheet.cssRules || [])) {
        if (rule.conditionText && rule.conditionText.includes('prefers-reduced-motion')) { hasReducedMediaRule = true; break; }
      }
    } catch (_err) { /* cross-origin stylesheet */ }
    if (hasReducedMediaRule) break;
  }
  const nav = performance.getEntriesByType('navigation')[0];
  return {
    viewport: vpName, width: vw, scrollWidth: docSw, horizontalOverflowPx: overflowPx,
    overflowSelectors, brokenImages, contrastViolations, animationsDetected, hasReducedMediaRule,
    domContentLoadedMs: nav ? Math.max(0, Math.round(nav.domContentLoadedEventEnd - nav.startTime)) : 0,
    loadEventMs: nav ? Math.max(0, Math.round(nav.loadEventEnd - nav.startTime)) : 0,
  };
}"""

_REDUCED_CHECK_JS = """() => {
  let active = 0;
  if (typeof document.getAnimations === 'function') {
    for (const a of document.getAnimations()) { if (a.playState === 'running') active += 1; }
  }
  for (const el of document.querySelectorAll('*')) {
    const st = window.getComputedStyle(el);
    if (st.animationName && st.animationName !== 'none' && parseFloat(st.animationDuration || '0') > 0 && st.animationPlayState !== 'paused') { active += 1; break; }
  }
  return active;
}"""

_WEBGL_FONTS_JS = """async () => {
  try { if (document.fonts && document.fonts.ready) await document.fonts.ready; } catch (_e) { /* fonts */ }
  const loadedFonts = [];
  if (document.fonts) {
    for (const f of Array.from(document.fonts)) {
      if (f.status === 'loaded' && f.family && !loadedFonts.includes(f.family)) loadedFonts.push(f.family);
    }
  }
  const tick = () => new Promise((r) => requestAnimationFrame(r));
  for (let i = 0; i < 6; i++) await tick();
  const canvases = [];
  for (const c of Array.from(document.querySelectorAll('canvas'))) {
    const rect = c.getBoundingClientRect();
    let variance = 0;
    try {
      const probe = document.createElement('canvas');
      probe.width = 16; probe.height = 16;
      const pctx = probe.getContext('2d');
      if (pctx && c.width > 0 && c.height > 0) {
        pctx.drawImage(c, 0, 0, 16, 16);
        const px = pctx.getImageData(0, 0, 16, 16).data;
        let minL = 255, maxL = 0;
        for (let i = 0; i < px.length; i += 4) {
          const lum = px[i] * 0.299 + px[i + 1] * 0.587 + px[i + 2] * 0.114;
          if (lum < minL) minL = lum;
          if (lum > maxL) maxL = lum;
        }
        variance = Math.round((maxL - minL) * 100) / 100;
      }
    } catch (_e) { variance = -1; }
    canvases.push({ width: c.width || Math.round(rect.width), height: c.height || Math.round(rect.height), pixelVariance: variance, monochrome: variance >= 0 && variance < 1.5, contextLost: Boolean(window.__alephWebglLost) });
  }
  return { loadedFonts, canvases };
}"""

_MOTION_LAYOUT_JS = """async (sampleScrollFps) => {
  const vw = window.innerWidth || document.documentElement.clientWidth || 0;
  const vh = window.innerHeight || document.documentElement.clientHeight || 0;
  const fixedHeaders = [];
  for (const el of Array.from(document.querySelectorAll('header, nav'))) {
    const st = window.getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden') continue;
    if (st.position === 'fixed' || st.position === 'sticky') {
      fixedHeaders.push({ el, rect: el.getBoundingClientRect() });
    }
  }
  const canvasRects = Array.from(document.querySelectorAll('canvas')).map((c) => c.getBoundingClientRect()).filter((r) => r.width > 20 && r.height > 20);
  const clippedSelectors = [];
  const overlapSelectors = [];
  const unshieldedRects = [];
  const hasShield = (el) => {
    let cur = el;
    while (cur && cur !== document.body && cur !== document.documentElement) {
      const st = window.getComputedStyle(cur);
      const m = (st.backgroundColor || '').match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([\\d.]+))?\\)/);
      const alpha = m ? (m[4] !== undefined ? parseFloat(m[4]) : 1) : 0;
      if (alpha >= 0.72) return true;
      cur = cur.parentElement;
    }
    return false;
  };
  for (const el of Array.from(document.querySelectorAll('h1, h2, h3, p'))) {
    const st = window.getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden' || parseFloat(st.opacity) < 0.1) continue;
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0 || r.bottom <= 0 || r.top >= vh) continue;
    const tag = el.tagName.toLowerCase() + (el.id ? '#' + el.id : '');
    if (r.right > vw + 2 || r.left < -2) {
      if (clippedSelectors.length < 10) clippedSelectors.push(tag);
    }
    let inHeader = false;
    for (const fh of fixedHeaders) {
      if (fh.el.contains(el)) inHeader = true;
      else if (r.top >= 0 && r.top < fh.rect.bottom - 2 && r.bottom > fh.rect.top + 2) {
        if (overlapSelectors.length < 10) overlapSelectors.push(tag);
      }
    }
    if (!inHeader && !hasShield(el) && unshieldedRects.length < 10) {
      const overlapsCanvas = canvasRects.some((cr) => !(r.right < cr.left || r.left > cr.right || r.bottom < cr.top || r.top > cr.bottom));
      unshieldedRects.push({ selector: tag, left: r.left, right: r.right, top: r.top, bottom: r.bottom, overlapsCanvas });
    }
  }
  const h1El = document.querySelector('h1');
  const h1Px = h1El ? (parseFloat(window.getComputedStyle(h1El).fontSize) || 36) : 36;
  const bodyPx = parseFloat(window.getComputedStyle(document.body).fontSize) || 16;
  const typeScaleRatio = Math.round((h1Px / Math.max(1, bodyPx)) * 1000) / 1000;
  let motion = null;
  if (sampleScrollFps) {
    const stamps = [];
    const maxScroll = Math.max(0, document.documentElement.scrollHeight - vh);
    const startY = window.scrollY;
    await new Promise((resolve) => {
      let i = 0;
      const step = (ts) => {
        stamps.push(ts);
        if (maxScroll > 20 && i < 12) window.scrollTo(0, Math.round((maxScroll * 0.25 * i) / 12));
        i += 1;
        if (i <= 12) requestAnimationFrame(step);
        else resolve();
      };
      requestAnimationFrame(step);
    });
    window.scrollTo(0, startY);
    const deltas = [];
    for (let i = 1; i < stamps.length; i++) deltas.push(Math.max(1.0, stamps[i] - stamps[i - 1]));
    const avgDelta = deltas.length ? deltas.reduce((a, b) => a + b, 0) / deltas.length : 16.67;
    const maxDelta = deltas.length ? Math.max(...deltas) : 16.67;
    motion = {
      cls: Math.round(Number(window.__alephCls || 0) * 10000) / 10000,
      avg_fps: Math.round((1000.0 / avgDelta) * 10) / 10,
      min_frame_fps: Math.round((1000.0 / maxDelta) * 10) / 10,
      frames_sampled: deltas.length,
      long_frames_over_50ms: deltas.filter((d) => d > 50).length,
    };
  }
  return {
    motion,
    typeScaleRatio,
    unshieldedRects,
    layout: {
      clipped_text_count: clippedSelectors.length,
      clipped_selectors: clippedSelectors,
      fixed_header_overlap_count: overlapSelectors.length,
      overlap_selectors: overlapSelectors,
    },
  };
}"""


@dataclass
class VisualAuditReport:
    """Resultado completo de auditoría visual real en Chromium headless."""
    audit_id: str
    target: str
    passed: bool
    engine: str
    viewports: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    console_errors: List[str] = field(default_factory=list)
    page_errors: List[str] = field(default_factory=list)
    horizontal_overflow_px: float = 0.0
    overflow_selectors: List[str] = field(default_factory=list)
    broken_images: List[str] = field(default_factory=list)
    contrast_violations: List[Dict[str, Any]] = field(default_factory=list)
    reduced_motion_ok: bool = True
    animations_detected: int = 0
    load_timing_ms: Dict[str, float] = field(default_factory=dict)
    screenshots: Dict[str, str] = field(default_factory=dict)
    webgl_canvas_audit: Dict[str, Any] = field(default_factory=dict)
    loaded_web_fonts: List[str] = field(default_factory=list)
    motion_telemetry: Dict[str, Any] = field(default_factory=dict)
    layout_telemetry: Dict[str, Any] = field(default_factory=dict)
    perceptual_cv_metrics: Dict[str, Any] = field(default_factory=dict)
    saliency_text_clearance: Dict[str, Any] = field(default_factory=dict)
    violations: List[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class _QuietHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        _ = (format, args)


class VisualBrowserAuditor:
    """Orquesta auditoría DOM/CSS/WebGL/FPS/CLS/CV en Chromium real para 3 viewports."""

    def __init__(self, repo_root: Optional[str] = None):
        self.repo_root = os.path.abspath(repo_root) if repo_root else os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def _prepare_target(self, path_or_url: str, html_content: Optional[str]) -> Tuple[str, Optional[http.server.ThreadingHTTPServer], Optional[str]]:
        if html_content is not None and str(html_content).strip():
            tmp_dir = tempfile.mkdtemp(prefix="aleph_visual_")
            Path(os.path.join(tmp_dir, "index.html")).write_text(html_content, encoding="utf-8")
            url, srv = self._start_static_server(tmp_dir, "index.html")
            return url, srv, tmp_dir
        raw = str(path_or_url or "").strip()
        if raw.startswith(("http://", "https://", "file://", "data:")):
            return raw, None, None
        abs_p = os.path.abspath(raw)
        if os.path.isfile(abs_p):
            url, srv = self._start_static_server(os.path.dirname(abs_p), os.path.basename(abs_p))
            return url, srv, None
        if os.path.isdir(abs_p):
            url, srv = self._start_static_server(abs_p, "index.html")
            return url, srv, None
        raise FileNotFoundError(f"Visual target not found: {path_or_url}")

    @staticmethod
    def _start_static_server(directory: str, entry_file: str) -> Tuple[str, http.server.ThreadingHTTPServer]:
        handler = functools.partial(_QuietHTTPHandler, directory=directory)
        httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        return f"http://127.0.0.1:{int(httpd.server_address[1])}/{entry_file}", httpd

    def audit(self, path_or_url: str = "", html_content: Optional[str] = None, output_root: Optional[str] = None, timeout_ms: int = 15000, capture_scroll_storyboard: bool = True) -> VisualAuditReport:
        stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S")
        audit_id = f"va_{stamp}_{uuid.uuid4().hex[:6]}"
        shot_dir = os.path.abspath(os.path.join(output_root or os.path.join(self.repo_root, ".aleph", "runtime", "visual_audits"), audit_id))
        os.makedirs(shot_dir, exist_ok=True)
        url, httpd, tmp_dir = self._prepare_target(path_or_url, html_content)
        try:
            return self._audit_url(audit_id, path_or_url or "inline_html", url, shot_dir, timeout_ms, capture_scroll_storyboard)
        finally:
            if httpd is not None:
                httpd.shutdown()
                httpd.server_close()
            if tmp_dir and os.path.isdir(tmp_dir):
                shutil.rmtree(tmp_dir, ignore_errors=True)

    def _audit_url(self, audit_id: str, label: str, url: str, shot_dir: str, timeout_ms: int, capture_scroll_storyboard: bool = True) -> VisualAuditReport:
        from playwright.sync_api import sync_playwright
        from aleph_core.visual.visual_evolve import analyze_png_perceptual_and_clearance

        console_errors: List[str] = []
        page_errors: List[str] = []
        vp_metrics: Dict[str, Dict[str, Any]] = {}
        screenshots: Dict[str, str] = {}
        overflow_selectors: List[str] = []
        broken_images: List[str] = []
        contrast_violations: List[Dict[str, Any]] = []
        loaded_web_fonts: List[str] = []
        webgl_audit: Dict[str, Any] = {"canvas_count": 0, "canvases": [], "context_lost_count": 0, "monochrome_count": 0, "all_healthy": True}
        motion_telemetry: Dict[str, Any] = {"cls": 0.0, "avg_fps": 0.0, "min_frame_fps": 0.0, "frames_sampled": 0, "long_frames_over_50ms": 0}
        layout_telemetry: Dict[str, Any] = {"clipped_text_count": 0, "clipped_selectors": [], "fixed_header_overlap_count": 0, "overlap_selectors": []}
        perceptual_cv: Dict[str, Any] = {}
        clearance_rep: Dict[str, Any] = {"clearance_score": 100.0, "overlap_ratio": 0.0, "clearance_ok": True, "unshielded_blocks": 0, "colliding_selectors": [], "ultrawide_colliding_selectors": [], "max_underlying_saliency": 0.0}
        max_overflow, animations_total, has_reduced_rule = 0.0, 0, False
        load_timing: Dict[str, float] = {"domcontentloaded_ms": 0.0, "load_ms": 0.0}

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--no-sandbox", "--enable-webgl", "--ignore-gpu-blocklist", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
            try:
                engine = f"Chromium {browser.version or 'headless'}"
                page = browser.new_page(viewport={"width": 1440, "height": 900})
                page.set_default_timeout(timeout_ms)
                page.add_init_script("window.__alephWebglLost = false; window.__alephCls = 0; window.addEventListener('webglcontextlost', () => { window.__alephWebglLost = true; }, true); try { new PerformanceObserver((l) => { for (const e of l.getEntries()) { if (!e.hadRecentInput) window.__alephCls += e.value; } }).observe({ type: 'layout-shift', buffered: true }); } catch (_e) {}")
                page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
                page.on("pageerror", lambda err: page_errors.append(str(err)))
                t0 = time.perf_counter()
                page.goto(url, wait_until="load", timeout=timeout_ms)
                wall_ms = round((time.perf_counter() - t0) * 1000.0, 2)

                for vp_name, vw, vh in VIEWPORTS:
                    page.set_viewport_size({"width": vw, "height": vh})
                    page.evaluate("void(document.documentElement.offsetHeight)")
                    data = page.evaluate(_DOM_EVAL_JS, vp_name)
                    if isinstance(data, dict):
                        max_overflow = max(max_overflow, float(data.get("horizontalOverflowPx", 0.0)))
                        for s in data.get("overflowSelectors") or []:
                            if s not in overflow_selectors:
                                overflow_selectors.append(s)
                        for b in data.get("brokenImages") or []:
                            if b not in broken_images:
                                broken_images.append(b)
                        contrast_violations.extend(data.get("contrastViolations") or [])
                        animations_total = max(animations_total, int(data.get("animationsDetected", 0)))
                        has_reduced_rule = has_reduced_rule or bool(data.get("hasReducedMediaRule"))
                        if load_timing.get("load_ms", 0.0) == 0.0:
                            load_timing["domcontentloaded_ms"] = float(data.get("domContentLoadedMs") or wall_ms)
                            load_timing["load_ms"] = float(data.get("loadEventMs") or wall_ms)
                        vp_metrics[vp_name] = data
                    shot_path = os.path.abspath(os.path.join(shot_dir, f"{vp_name}.png"))
                    try:
                        page.screenshot(path=shot_path, full_page=False)
                    except Exception:
                        page.wait_for_timeout(180)
                        page.screenshot(path=shot_path, full_page=False)
                    screenshots[vp_name] = shot_path
                    if vp_name == "desktop_1440":
                        wf = page.evaluate(_WEBGL_FONTS_JS)
                        if isinstance(wf, dict):
                            loaded_web_fonts = list(wf.get("loadedFonts") or [])
                            c_list = list(wf.get("canvases") or [])
                            lost_n = sum(1 for c in c_list if c.get("contextLost") or c.get("width", 0) <= 0 or c.get("height", 0) <= 0)
                            mono_n = sum(1 for c in c_list if c.get("monochrome"))
                            webgl_audit = {"canvas_count": len(c_list), "canvases": c_list, "context_lost_count": lost_n, "monochrome_count": mono_n, "all_healthy": (lost_n == 0 and mono_n == 0)}
                        ml = page.evaluate(_MOTION_LAYOUT_JS, True)
                        if isinstance(ml, dict):
                            if isinstance(ml.get("motion"), dict):
                                motion_telemetry = dict(ml.get("motion") or {})
                            if isinstance(ml.get("layout"), dict):
                                layout_telemetry = dict(ml.get("layout") or {})
                            perceptual_cv, desk_clr = analyze_png_perceptual_and_clearance(
                                shot_path, vw, vh, list(ml.get("unshieldedRects") or []), float(ml.get("typeScaleRatio") or 2.0)
                            )
                            clearance_rep.update(desk_clr)
                        if capture_scroll_storyboard:
                            max_scroll = int(page.evaluate("Math.max(0, document.documentElement.scrollHeight - window.innerHeight)") or 0)
                            if max_scroll > 80:
                                for pct, key in ((0.35, "scroll_35_1440"), (0.70, "scroll_70_1440")):
                                    page.evaluate("y => window.scrollTo(0, y)", int(max_scroll * pct))
                                    page.wait_for_timeout(350)
                                    s_path = os.path.abspath(os.path.join(shot_dir, f"{key}.png"))
                                    page.screenshot(path=s_path, full_page=False)
                                    screenshots[key] = s_path
                                page.evaluate("window.scrollTo(0, 0)")
                    elif vp_name == "ultrawide_2560":
                        uw_ml = page.evaluate(_MOTION_LAYOUT_JS, False)
                        if isinstance(uw_ml, dict):
                            _uw_cv, uw_clr = analyze_png_perceptual_and_clearance(
                                shot_path, vw, vh, list(uw_ml.get("unshieldedRects") or []), float(uw_ml.get("typeScaleRatio") or 2.0)
                            )
                            clearance_rep["ultrawide_colliding_selectors"] = list(uw_clr.get("colliding_selectors") or [])
                            clearance_rep["ultrawide_clearance_score"] = uw_clr.get("clearance_score", 100.0)
                            clearance_rep["overlap_ratio"] = max(float(clearance_rep.get("overlap_ratio", 0.0)), float(uw_clr.get("overlap_ratio", 0.0)))
                            clearance_rep["clearance_ok"] = bool(clearance_rep.get("clearance_ok", True)) and bool(uw_clr.get("clearance_ok", True))

                reduced_ok = True
                if animations_total > 0 and not has_reduced_rule:
                    page.emulate_media(reduced_motion="reduce")
                    reduced_ok = int(page.evaluate(_REDUCED_CHECK_JS) or 0) == 0
                    page.emulate_media(reduced_motion="no-preference")
            finally:
                browser.close()

        violations: List[str] = []
        if console_errors:
            violations.append(f"console_errors={len(console_errors)}")
        if page_errors:
            violations.append(f"page_errors={len(page_errors)}")
        if max_overflow > 0.0:
            violations.append(f"horizontal_overflow_px={max_overflow}")
        if broken_images:
            violations.append(f"broken_images={len(broken_images)}")
        if contrast_violations:
            violations.append(f"contrast_violations={len(contrast_violations)}")
        if not reduced_ok:
            violations.append("missing_prefers_reduced_motion")
        if not webgl_audit.get("all_healthy", True):
            violations.append(f"webgl_unhealthy(lost={webgl_audit.get('context_lost_count')},mono={webgl_audit.get('monochrome_count')})")
        if float(motion_telemetry.get("cls", 0.0)) > 0.25:
            violations.append(f"cls_exceeded={motion_telemetry.get('cls')}")

        passed = len(violations) == 0
        return VisualAuditReport(
            audit_id=audit_id, target=label, passed=passed, engine=engine, viewports=vp_metrics,
            console_errors=console_errors, page_errors=page_errors, horizontal_overflow_px=max_overflow,
            overflow_selectors=overflow_selectors, broken_images=broken_images, contrast_violations=contrast_violations,
            reduced_motion_ok=reduced_ok, animations_detected=animations_total, load_timing_ms=load_timing,
            screenshots=screenshots, webgl_canvas_audit=webgl_audit, loaded_web_fonts=loaded_web_fonts,
            motion_telemetry=motion_telemetry, layout_telemetry=layout_telemetry,
            perceptual_cv_metrics=perceptual_cv, saliency_text_clearance=clearance_rep,
            violations=violations, summary=f"[{'PASS' if passed else 'FAIL'}] {engine} | overflow={max_overflow:.0f}px | cls={motion_telemetry.get('cls', 0.0)} | pqi={perceptual_cv.get('perceptual_quality_index', 0.0)} | violations={len(violations)}",
        )


def audit_visual_target(path_or_url: str = "", html_content: Optional[str] = None, repo_root: Optional[str] = None, capture_scroll_storyboard: bool = True) -> Dict[str, Any]:
    """Punto de entrada compacto para CLI y MCP dispatch."""
    return VisualBrowserAuditor(repo_root=repo_root).audit(path_or_url=path_or_url, html_content=html_content, capture_scroll_storyboard=capture_scroll_storyboard).to_dict()
