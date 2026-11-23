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
        if (rule.conditionText && rule.conditionText.includes('prefers-reduced-motion')) {
          hasReducedMediaRule = true;
          break;
        }
      }
    } catch (_err) { /* cross-origin stylesheet */ }
    if (hasReducedMediaRule) break;
  }
  const nav = performance.getEntriesByType('navigation')[0];
  return {
    viewport: vpName,
    width: vw,
    scrollWidth: docSw,
    horizontalOverflowPx: overflowPx,
    overflowSelectors,
    brokenImages,
    contrastViolations,
    animationsDetected,
    hasReducedMediaRule,
    domContentLoadedMs: nav ? Math.max(0, Math.round(nav.domContentLoadedEventEnd - nav.startTime)) : 0,
    loadEventMs: nav ? Math.max(0, Math.round(nav.loadEventEnd - nav.startTime)) : 0,
  };
}"""

_REDUCED_CHECK_JS = """() => {
  let active = 0;
  if (typeof document.getAnimations === 'function') {
    for (const a of document.getAnimations()) {
      if (a.playState === 'running') active += 1;
    }
  }
  for (const el of document.querySelectorAll('*')) {
    const st = window.getComputedStyle(el);
    if (st.animationName && st.animationName !== 'none' && parseFloat(st.animationDuration || '0') > 0 && st.animationPlayState !== 'paused') {
      active += 1;
      break;
    }
  }
  return active;
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
    violations: List[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class _QuietHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        _ = (format, args)


class VisualBrowserAuditor:
    """Orquesta auditoría DOM/CSS/visual en Chromium real para 3 viewports con screenshots."""

    def __init__(self, repo_root: Optional[str] = None):
        if repo_root:
            self.repo_root = os.path.abspath(repo_root)
        else:
            self.repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def _prepare_target(self, path_or_url: str, html_content: Optional[str]) -> Tuple[str, Optional[http.server.ThreadingHTTPServer], Optional[str]]:
        if html_content is not None and str(html_content).strip():
            tmp_dir = tempfile.mkdtemp(prefix="aleph_visual_")
            idx_path = os.path.join(tmp_dir, "index.html")
            Path(idx_path).write_text(html_content, encoding="utf-8")
            url, srv = self._start_static_server(tmp_dir, "index.html")
            return url, srv, tmp_dir
        raw = str(path_or_url or "").strip()
        if raw.startswith(("http://", "https://", "file://", "data:")):
            return raw, None, None
        abs_p = os.path.abspath(raw)
        if os.path.isfile(abs_p):
            serve_dir = os.path.dirname(abs_p)
            rel_name = os.path.basename(abs_p)
            url, srv = self._start_static_server(serve_dir, rel_name)
            return url, srv, None
        if os.path.isdir(abs_p):
            url, srv = self._start_static_server(abs_p, "index.html")
            return url, srv, None
        raise FileNotFoundError(f"Visual target not found: {path_or_url}")

    @staticmethod
    def _start_static_server(directory: str, entry_file: str) -> Tuple[str, http.server.ThreadingHTTPServer]:
        handler = functools.partial(_QuietHTTPHandler, directory=directory)
        httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        port = int(httpd.server_address[1])
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()
        return f"http://127.0.0.1:{port}/{entry_file}", httpd

    def audit(
        self,
        path_or_url: str = "",
        html_content: Optional[str] = None,
        output_root: Optional[str] = None,
        timeout_ms: int = 15000,
    ) -> VisualAuditReport:
        stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d_%H%M%S")
        audit_id = f"va_{stamp}_{uuid.uuid4().hex[:6]}"
        base_out = output_root or os.path.join(self.repo_root, ".aleph", "runtime", "visual_audits")
        shot_dir = os.path.abspath(os.path.join(base_out, audit_id))
        os.makedirs(shot_dir, exist_ok=True)
        url, httpd, tmp_dir = self._prepare_target(path_or_url, html_content)
        try:
            return self._audit_url(audit_id, path_or_url or "inline_html", url, shot_dir, timeout_ms)
        finally:
            if httpd is not None:
                httpd.shutdown()
                httpd.server_close()
            if tmp_dir and os.path.isdir(tmp_dir):
                shutil.rmtree(tmp_dir, ignore_errors=True)

    def _audit_url(
        self, audit_id: str, label: str, url: str, shot_dir: str, timeout_ms: int
    ) -> VisualAuditReport:
        from playwright.sync_api import sync_playwright

        console_errors: List[str] = []
        page_errors: List[str] = []
        vp_metrics: Dict[str, Dict[str, Any]] = {}
        screenshots: Dict[str, str] = {}
        overflow_selectors: List[str] = []
        broken_images: List[str] = []
        contrast_violations: List[Dict[str, Any]] = []
        max_overflow = 0.0
        animations_total = 0
        has_reduced_rule = False
        load_timing: Dict[str, float] = {"domcontentloaded_ms": 0.0, "load_ms": 0.0}

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=["--no-sandbox", "--disable-gpu"])
            try:
                engine = f"Chromium {browser.version or 'headless'}"
                page = browser.new_page(viewport={"width": 1440, "height": 900})
                page.set_default_timeout(timeout_ms)
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
                        ov = float(data.get("horizontalOverflowPx", 0.0))
                        max_overflow = max(max_overflow, ov)
                        for s in data.get("overflowSelectors") or []:
                            if s not in overflow_selectors:
                                overflow_selectors.append(s)
                        for b in data.get("brokenImages") or []:
                            if b not in broken_images:
                                broken_images.append(b)
                        contrast_violations.extend(data.get("contrastViolations") or [])
                        animations_total = max(animations_total, int(data.get("animationsDetected", 0)))
                        has_reduced_rule = has_reduced_rule or bool(data.get("hasReducedMediaRule"))
                        if load_timing["load_ms"] == 0.0:
                            load_timing["domcontentloaded_ms"] = float(data.get("domContentLoadedMs") or wall_ms)
                            load_timing["load_ms"] = float(data.get("loadEventMs") or wall_ms)
                        vp_metrics[vp_name] = data
                    shot_path = os.path.abspath(os.path.join(shot_dir, f"{vp_name}.png"))
                    page.screenshot(path=shot_path, full_page=False)
                    screenshots[vp_name] = shot_path

                reduced_ok = True
                if animations_total > 0 and not has_reduced_rule:
                    page.emulate_media(reduced_motion="reduce")
                    still_active = int(page.evaluate(_REDUCED_CHECK_JS) or 0)
                    reduced_ok = still_active == 0
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

        passed = len(violations) == 0
        summary = f"[{'PASS' if passed else 'FAIL'}] {engine} | overflow={max_overflow:.0f}px | violations={len(violations)}"
        return VisualAuditReport(
            audit_id=audit_id,
            target=label,
            passed=passed,
            engine=engine,
            viewports=vp_metrics,
            console_errors=console_errors,
            page_errors=page_errors,
            horizontal_overflow_px=max_overflow,
            overflow_selectors=overflow_selectors,
            broken_images=broken_images,
            contrast_violations=contrast_violations,
            reduced_motion_ok=reduced_ok,
            animations_detected=animations_total,
            load_timing_ms=load_timing,
            screenshots=screenshots,
            violations=violations,
            summary=summary,
        )


def audit_visual_target(path_or_url: str = "", html_content: Optional[str] = None, repo_root: Optional[str] = None) -> Dict[str, Any]:
    """Punto de entrada compacto para CLI y MCP dispatch."""
    return VisualBrowserAuditor(repo_root=repo_root).audit(path_or_url=path_or_url, html_content=html_content).to_dict()
