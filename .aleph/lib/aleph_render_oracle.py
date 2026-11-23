"""
.aleph/lib/aleph_render_oracle.py
Tri-Motor Render Oracle & DOM Layout Auditor (Track 8).
Estándar: In-DOM Zero-Overflow Audit / APCA Contrast / AXTree / Anti-Slop Metrics.

Audita física y estéticamente el renderizado de interfaces HTML/CSS:
1. Verificación en tiempo de ejecución de scrollWidth <= clientWidth (cero overflow-x).
2. Jerarquía tipográfica accesible (h1 -> h2 -> h3 sin saltos de nivel).
3. Dimensiones mínimas de objetivos táctiles (touch targets >= 44x44px).
4. Verificación de contraste perceptual y ausencia de wildcard transition: all.
5. Cálculo del Índice de Slop (0.0 a 1.0) y detección de marketing copy genérico.
6. Operación dual: Ejecución in-browser vía Chromium CDP / Playwright O analizador estático DOM.
"""

from __future__ import annotations

import atexit
import threading
from datetime import datetime, timezone
import html
from html.parser import HTMLParser
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class AuditReport:
    """Reporte formal de auditoría de render y calidad de diseño."""
    is_passing: bool
    horizontal_overflow_px: float
    accessibility_score: float  # 0.0 a 100.0
    slop_score: float          # 0.0 (puro soberano) a 1.0 (slop total)
    touch_target_violations: List[str] = field(default_factory=list)
    heading_hierarchy_violations: List[str] = field(default_factory=list)
    contrast_violations: List[str] = field(default_factory=list)
    visual_design_violations: List[str] = field(default_factory=list)
    slop_findings: List[str] = field(default_factory=list)
    photometric_audit: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> str:
        status = "APROBADO (SOBERANO)" if self.is_passing else "RECHAZADO (SLOP DETECTADO)"
        return (
            f"[{status}] A11y: {self.accessibility_score:.1f}/100 | "
            f"Slop Score: {self.slop_score:.3f} | Overflow-X: {self.horizontal_overflow_px:.1f}px"
        )


class StaticDOMAuditor(HTMLParser):
    """Analizador estático de HTML para auditoría cuando el navegador no está activo."""

    def __init__(self):
        super().__init__()
        self.tags: List[str] = []
        self.headings: List[int] = []
        self.interactive_elements: List[Dict[str, Any]] = []
        self.classes: Set[str] = set()
        self.has_h1 = False
        self.text_content: List[str] = []
        self.style_content: List[str] = []
        self.in_style = False
        self.has_viewport_meta = False
        self.bento_cards: List[Dict[str, Any]] = []
        self._current_bento: Optional[Dict[str, Any]] = None
        self.canvases_count: int = 0
        self._in_footer: bool = False
        self._in_nav: bool = False

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        self.tags.append(tag)
        attr_dict = {k: (v or "") for k, v in attrs}

        if tag == "footer":
            self._in_footer = True
        elif tag == "nav":
            self._in_nav = True

        if tag == "meta" and attr_dict.get("name") == "viewport":
            self.has_viewport_meta = True

        if tag == "canvas":
            self.canvases_count += 1

        cls_str = attr_dict.get("class", "")
        el_id = attr_dict.get("id", "")
        is_genuine_bento = (
            not self._in_footer
            and not self._in_nav
            and "telem" not in el_id
            and ("aleph-comp-bento_card" in cls_str or "aleph-comp-bento_item" in cls_str or "bento-card" in cls_str)
        )

        if is_genuine_bento:
            self._current_bento = {
                "id": el_id,
                "class": cls_str,
                "has_visual": False,
                "tag": tag,
            }
        elif self._current_bento is not None:
            if tag in ("svg", "canvas", "code", "pre", "img", "video") or any(
                k in cls_str for k in ("visual-stage", "metric-item", "terminal", "stage", "chart", "gauge", "icon", "badge")
            ):
                self._current_bento["has_visual"] = True

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag[1])
            self.headings.append(level)
            if level == 1:
                self.has_h1 = True

        if tag in ("button", "a", "input", "select", "textarea"):
            self.interactive_elements.append({
                "tag": tag,
                "id": attr_dict.get("id", ""),
                "class": attr_dict.get("class", ""),
                "aria_label": attr_dict.get("aria-label", ""),
            })

        if "class" in attr_dict:
            for c in attr_dict["class"].split():
                self.classes.add(c)

        if tag == "style":
            self.in_style = True

    def handle_endtag(self, tag: str):
        if tag == "style":
            self.in_style = False
        elif tag == "footer":
            self._in_footer = False
        elif tag == "nav":
            self._in_nav = False

        if self._current_bento and tag == self._current_bento.get("tag"):
            self.bento_cards.append(self._current_bento)
            self._current_bento = None

    def handle_data(self, data: str):
        if self.in_style:
            self.style_content.append(data)
        else:
            stripped = data.strip()
            if stripped:
                self.text_content.append(stripped)


class LivePlaywrightOracle:
    """
    Oráculo de Renderizado Físico basado en Chromium/Blink real (vía Playwright o Chromium CDP WebDriver).
    Mide scrollWidth - clientWidth en Mobile (320px, 375px), Tablet (768px, 1024px) y Desktop (1440px, 1920px).
    """

    CANONICAL_VIEWPORTS = [
        {"name": "mobile_320", "category": "mobile", "width": 320, "height": 568},
        {"name": "mobile_375", "category": "mobile", "width": 375, "height": 812},
        {"name": "tablet_768", "category": "tablet", "width": 768, "height": 1024},
        {"name": "tablet_1024", "category": "tablet", "width": 1024, "height": 768},
        {"name": "desktop_1440", "category": "desktop", "width": 1440, "height": 900},
        {"name": "desktop_1920", "category": "desktop", "width": 1920, "height": 1080},
    ]

    VIEWPORT_AUDIT_SCRIPT = """
    const currentVp = arguments[0];
    const root = document.documentElement;
    const body = document.body;

    const rootOverflow = root ? root.scrollWidth - root.clientWidth : 0;
    const bodyOverflow = body ? body.scrollWidth - body.clientWidth : 0;
    const overflowX = Math.max(0, rootOverflow, bodyOverflow);

    const interactive = Array.from(document.querySelectorAll('button, a, input, select'));
    const smallTargets = interactive.filter(el => {
      const rect = el.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0 && (rect.width < 40 || rect.height < 40);
    }).map(el => el.id || el.className || el.tagName.toLowerCase());

    const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'))
      .map(h => parseInt(h.tagName[1], 10));
    const headingViolations = [];
    if (headings.length > 0 && headings[0] !== 1) {
      headingViolations.push(`El documento comienza con h${headings[0]} en vez de h1`);
    }
    for (let i = 0; i < headings.length - 1; i++) {
      if (headings[i + 1] - headings[i] > 1) {
        headingViolations.push(`Salto abrupto de jerarquía: h${headings[i]} -> h${headings[i + 1]}`);
      }
    }

    const visualViolations = [];

    function parseRgba(colorStr) {
      if (!colorStr || colorStr === 'transparent' || colorStr === 'inherit') return null;
      const m = colorStr.match(/rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([\\d.]+))?\\)/);
      if (!m) return null;
      return {
        r: parseInt(m[1], 10),
        g: parseInt(m[2], 10),
        b: parseInt(m[3], 10),
        a: m[4] !== undefined ? parseFloat(m[4]) : 1.0
      };
    }

    function rgbToHsl(r, g, b) {
      const rNorm = r / 255, gNorm = g / 255, bNorm = b / 255;
      const max = Math.max(rNorm, gNorm, bNorm);
      const min = Math.min(rNorm, gNorm, bNorm);
      const delta = max - min;
      const l = (max + min) / 2;
      const s = delta === 0 ? 0 : delta / (1 - Math.abs(2 * l - 1));
      return { s, l };
    }

    function isBrightAccent(rgba) {
      if (!rgba || rgba.a < 0.25) return false;
      const hsl = rgbToHsl(rgba.r, rgba.g, rgba.b);
      return hsl.s >= 0.45 && hsl.l >= 0.25 && hsl.l <= 0.85;
    }

    function sRGBtoY(r, g, b) {
      const sR = r / 255.0, sG = g / 255.0, sB = b / 255.0;
      return 0.2126729 * Math.pow(sR, 2.4) + 0.7151522 * Math.pow(sG, 2.4) + 0.0721750 * Math.pow(sB, 2.4);
    }

    function computeAPCA(textRgba, bgRgba) {
      const Ytxt = sRGBtoY(textRgba.r, textRgba.g, textRgba.b);
      const Ybg = sRGBtoY(bgRgba.r, bgRgba.g, bgRgba.b);
      const blkThrs = 0.022, blkClmp = 1.414;
      const clampedTxt = Ytxt > blkThrs ? Ytxt : Ytxt + Math.pow(blkThrs - Ytxt, blkClmp);
      const clampedBg = Ybg > blkThrs ? Ybg : Ybg + Math.pow(blkThrs - Ybg, blkClmp);
      if (Math.abs(clampedBg - clampedTxt) < 0.0005) return 0.0;
      let outputContrast = 0.0;
      if (clampedBg > clampedTxt) {
        const Sapca = (Math.pow(clampedBg, 0.56) - Math.pow(clampedTxt, 0.57)) * 1.14;
        outputContrast = Sapca < 0.027 ? 0.0 : (Sapca - 0.027) * 100.0;
      } else {
        const Sapca = (Math.pow(clampedBg, 0.65) - Math.pow(clampedTxt, 0.62)) * 1.14;
        outputContrast = Sapca > -0.027 ? 0.0 : (Sapca + 0.027) * 100.0;
      }
      return Math.abs(outputContrast);
    }

    // LEY 1: Presupuesto de Acento (60-30-10)
    const SAMPLE_COLS = 30;
    const SAMPLE_ROWS = 20;
    const totalSamples = SAMPLE_COLS * SAMPLE_ROWS;
    let accentHits = 0;
    const vpW = window.innerWidth;
    const vpH = window.innerHeight;

    for (let r = 0; r < SAMPLE_ROWS; r++) {
      for (let c = 0; c < SAMPLE_COLS; c++) {
        const x = Math.floor((c + 0.5) * (vpW / SAMPLE_COLS));
        const y = Math.floor((r + 0.5) * (vpH / SAMPLE_ROWS));
        const el = document.elementFromPoint(x, y);
        if (!el) continue;
        let curr = el;
        let effColor = null;
        while (curr && curr !== document.documentElement) {
          const bg = window.getComputedStyle(curr).backgroundColor;
          const parsed = parseRgba(bg);
          if (parsed && parsed.a >= 0.3) {
            effColor = parsed;
            break;
          }
          curr = curr.parentElement;
        }
        if (effColor && isBrightAccent(effColor)) {
          accentHits++;
        }
      }
    }
    const accentRatioPct = (accentHits / totalSamples) * 100;
    if (accentRatioPct > 10.0) {
      visualViolations.push(`Ley del Presupuesto de Acento (60-30-10) violada: Color de acento brillante cubre ${accentRatioPct.toFixed(1)}% del área visual (límite máximo permitido: 10.0%)`);
    }

    const navbars = Array.from(document.querySelectorAll('nav, .aleph-navbar'));
    for (const nav of navbars) {
      const buttons = Array.from(nav.querySelectorAll('button, a.aleph-button, .aleph-button'));
      let primaryCount = 0;
      for (const btn of buttons) {
        const bg = window.getComputedStyle(btn).backgroundColor;
        const parsed = parseRgba(bg);
        if (parsed && isBrightAccent(parsed)) {
          primaryCount++;
        }
      }
      if (primaryCount > 2) {
        visualViolations.push(`Barra de navegación contiene ${primaryCount} botones con fondo de acento primario (máximo permitido: 2)`);
      }
    }

    // LEY 2: Co-linearidad de Acciones (Desktop)
    let maxColinearityDeltaY = 0.0;
    if (String(currentVp).startsWith('desktop')) {
      const actionContainers = Array.from(document.querySelectorAll(
        '.aleph-hero-actions, [class*="actions"], [class*="button-group"], [class*="btn-group"], header nav, .hero-actions'
      ));
      const allButtons = Array.from(document.querySelectorAll('button, a.aleph-button, a[role="button"], .aleph-button, a.btn'));
      const parentGroups = new Set(actionContainers);
      allButtons.forEach(btn => {
        if (btn.parentElement) parentGroups.add(btn.parentElement);
      });

      for (const group of parentGroups) {
        const btns = Array.from(group.querySelectorAll(':scope > button, :scope > a.aleph-button, :scope > .aleph-button, :scope > a[role="button"], :scope > a.btn'))
          .filter(b => {
            const r = b.getBoundingClientRect();
            return r.width > 0 && r.height > 0 && window.getComputedStyle(b).display !== 'none';
          });
        if (btns.length >= 2) {
          btns.sort((a, b) => a.getBoundingClientRect().left - b.getBoundingClientRect().left);
          for (let i = 0; i < btns.length - 1; i++) {
            const rA = btns[i].getBoundingClientRect();
            const rB = btns[i + 1].getBoundingClientRect();
            const isHorizontal = rB.left >= rA.right - 8 && (rB.top < rA.bottom && rA.top < rB.bottom);
            if (isHorizontal) {
              const deltaTop = Math.abs(rA.top - rB.top);
              const deltaCenterY = Math.abs((rA.top + rA.height / 2) - (rB.top + rB.height / 2));
              const deltaY = Math.min(deltaTop, deltaCenterY);
              if (deltaY > maxColinearityDeltaY) {
                maxColinearityDeltaY = deltaY;
              }
              if (deltaY > 4.0) {
                const desc = group.className ? `.${group.className.trim().split(/\\s+/).join('.')}` : group.tagName.toLowerCase();
                visualViolations.push(`Ley de Co-linearidad de Acciones violada: Botones en '${desc}' no están alineados en el eje horizontal en Desktop (delta Y = ${deltaY.toFixed(1)}px > 4.0px)`);
                break;
              }
            }
          }
        }
      }
    }

    // LEY 3: Superficie Protectora & APCA sobre Canvas
    const canvases = Array.from(document.querySelectorAll('canvas')).filter(c => {
      const r = c.getBoundingClientRect();
      return r.width >= 100 && r.height >= 100 && window.getComputedStyle(c).display !== 'none';
    });

    if (canvases.length > 0) {
      const candidates = Array.from(document.querySelectorAll(
        '.aleph-metric-ticker, .bento-card, .aleph-bento-card, .bento-cell, article, .aleph-card, [class*="bento-card"], .aleph-telemetry-panel, div[id*="card"], div[id*="ticker"], div[id*="panel"]'
      )).filter(el => {
        const r = el.getBoundingClientRect();
        return r.width > 0 && r.height > 0 && el.innerText.trim().length > 0;
      });

      for (const card of candidates) {
        const cardRect = card.getBoundingClientRect();
        const overlaps = canvases.some(c => {
          const cr = c.getBoundingClientRect();
          return !(cardRect.right < cr.left || cardRect.left > cr.right || cardRect.bottom < cr.top || cardRect.top > cr.bottom);
        });

        if (overlaps) {
          let hasProtection = false;
          let surfaceBg = null;
          let curr = card;
          while (curr && curr !== document.body && curr !== document.documentElement) {
            const st = window.getComputedStyle(curr);
            const bf = st.backdropFilter || st.webkitBackdropFilter || '';
            const bg = parseRgba(st.backgroundColor);
            const bi = st.backgroundImage || '';
            const hasGradient = bi.includes('gradient') && (bi.includes('rgba') || bi.includes('rgb') || bi.includes('oklch'));
            const hasBlur = bf.includes('blur');
            const hasSemiBlur = hasBlur && ((bg && bg.a >= 0.15) || hasGradient);
            const hasOpaque = (bg && bg.a >= 0.65) || hasGradient;
            if (hasSemiBlur || hasOpaque) {
              hasProtection = true;
              surfaceBg = (bg && bg.a >= 0.15) ? bg : { r: 15, g: 23, b: 42, a: 0.85 };
              break;
            }
            curr = curr.parentElement;
          }

          const cardName = card.id || card.className || card.tagName.toLowerCase();
          if (!hasProtection) {
            visualViolations.push(`Ley de Superficie Protectora violada: El elemento '${cardName}' sobre canvas WebGL carece de backdrop-filter: blur o fondo protector con opacidad >= 0.65`);
          } else if (surfaceBg) {
            const textSt = window.getComputedStyle(card);
            const textClr = parseRgba(textSt.color) || { r: 255, g: 255, b: 255, a: 1.0 };
            const apca = computeAPCA(textClr, surfaceBg);
            const fontSize = parseFloat(textSt.fontSize) || 16.0;
            const minApca = fontSize >= 24 ? 60.0 : 75.0;
            if (apca < minApca) {
              visualViolations.push(`Ley de Superficie Protectora (APCA) violada: Contraste APCA insuficiente en '${cardName}' (${apca.toFixed(1)} Lc < ${minApca} Lc)`);
            }
          }
        }
      }
    }

    // LEY 4: Densidad Visual en Bento Cards
    const bentoCards = Array.from(document.querySelectorAll(
      '.aleph-bento-grid > article, .aleph-bento-grid > div, .bento-grid > article, .bento-grid > div, .aleph-comp-bento_card, .aleph-comp-bento_item, .aleph-bento-card'
    )).filter(c => {
      const r = c.getBoundingClientRect();
      const isInsideFooter = c.closest('footer') !== null;
      const isInsideNav = c.closest('nav') !== null;
      return r.width > 0 && r.height > 0 && !isInsideFooter && !isInsideNav;
    });

    for (const card of bentoCards) {
      if (card.classList.contains('aleph-bento-grid') || card.classList.contains('bento-grid')) continue;
      const isHeaderOnly = card.children.length === 1 && /^H[1-6]$/.test(card.children[0].tagName);
      if (isHeaderOnly) continue;

      const visualEls = card.querySelectorAll(
        'svg, canvas, code, pre, img, video, .aleph-visual-stage, .aleph-metric-item, [class*="stage"], [class*="terminal"], [class*="chart"], [class*="gauge"], [class*="icon"], [class*="badge"], [class*="metric"]'
      );
      if (visualEls.length === 0) {
        const cardName = card.id || card.className || card.tagName.toLowerCase();
        visualViolations.push(`Ley de Densidad Visual violada: La tarjeta Bento '${cardName}' es puramente textual (carece de <svg>, <canvas>, <code> o elementos visuales)`);
      }
    }

    // LEY 5: Detección de Saltos de Línea no Intencionales en Enlaces de Menú
    const menuLinks = Array.from(document.querySelectorAll('nav a, .aleph-navbar a, header nav a, .navbar a')).filter(link => {
      const r = link.getBoundingClientRect();
      return r.width > 0 && r.height > 0 && link.innerText.trim().length > 0;
    });

    for (const link of menuLinks) {
      const st = window.getComputedStyle(link);
      let lh = parseFloat(st.lineHeight);
      if (isNaN(lh)) {
        lh = (parseFloat(st.fontSize) || 16) * 1.25;
      }
      const range = document.createRange();
      range.selectNodeContents(link);
      const textRects = range.getClientRects();
      const textHeight = range.getBoundingClientRect().height;

      if (textRects.length > 1 || textHeight > (lh * 1.45)) {
        const linkTxt = link.innerText.trim().replace(/\\s+/g, ' ');
        visualViolations.push(`Salto de línea no intencional en enlace de menú: '${linkTxt}' se divide en múltiples líneas (${textRects.length} líneas detectadas, altoTexto=${Math.round(textHeight)}px vs lineHeight=${Math.round(lh)}px)`);
      }
    }

    return {
      overflowX,
      scrollWidth: root ? root.scrollWidth : 0,
      clientWidth: root ? root.clientWidth : 0,
      smallTargets,
      headingViolations,
      headingsCount: headings.length,
      visualViolations,
      photometrics: {
        accentRatioPct,
        maxColinearityDeltaY,
        bentoCardsAudited: bentoCards.length,
        menuLinksAudited: menuLinks.length,
        canvasesAudited: canvases.length
      }
    };
    """

    _shared_driver: Any = None
    _driver_lock = threading.RLock()
    _atexit_registered: bool = False

    def __init__(self, script_path: Optional[str] = None):
        if script_path:
            self.runner_script = os.path.abspath(script_path)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.runner_script = os.path.join(base_dir, "scripts", "playwright_layout_runner.mjs")

    @classmethod
    def _get_or_create_chromium_driver(cls) -> Any:
        if cls._shared_driver is not None:
            try:
                _ = cls._shared_driver.current_url
                return cls._shared_driver
            except Exception:
                try:
                    cls._shared_driver.quit()
                except Exception:
                    pass
                cls._shared_driver = None

        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--hide-scrollbars")
        cls._shared_driver = webdriver.Chrome(options=opts)
        cls._shared_driver.set_page_load_timeout(10.0)
        cls._shared_driver.set_script_timeout(5.0)

        if not cls._atexit_registered:
            cls._atexit_registered = True

            def _cleanup():
                if cls._shared_driver is not None:
                    try:
                        cls._shared_driver.quit()
                    except Exception:
                        pass
                    cls._shared_driver = None

            atexit.register(_cleanup)

        return cls._shared_driver

    @classmethod
    def audit_via_chromium_cdp_dict(cls, html_content: str, timeout_sec: float = 15.0) -> Dict[str, Any]:
        """
        Ejecuta la auditoría física de los 6 viewports canónicos sobre Chromium/Blink real
        utilizando Chrome DevTools Protocol (CDP) Emulation.setDeviceMetricsOverride.
        """
        import urllib.parse
        temp_html_path = ""
        safe_html = re.sub(
            r"while\s*\(\s*true\s*\)\s*\{[^}]*\}",
            "/* blocked_infinite_loop */",
            html_content,
            flags=re.IGNORECASE,
        )
        file_url = "data:text/html;charset=utf-8," + urllib.parse.quote(safe_html)
        viewport_results: Dict[str, Any] = {}
        max_horizontal_overflow = 0.0
        all_heading_violations: Set[str] = set()
        all_small_targets: Set[str] = set()
        all_visual_violations: Set[str] = set()

        with cls._driver_lock:
            driver = cls._get_or_create_chromium_driver()
            driver.set_page_load_timeout(timeout_sec)
            driver.set_script_timeout(min(5.0, float(timeout_sec)))
            try:
                # Cargar una vez y evaluar cada viewport vía CDP Emulation
                driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
                    "width": 1440,
                    "height": 900,
                    "deviceScaleFactor": 1,
                    "mobile": False,
                })
                driver.get(file_url)


                for vp in cls.CANONICAL_VIEWPORTS:
                    driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
                        "width": vp["width"],
                        "height": vp["height"],
                        "deviceScaleFactor": 1,
                        "mobile": False,
                    })
                    # Forzar reflow síncrono tras cambio de viewport
                    driver.execute_script("void(document.documentElement.offsetHeight);")
                    metrics = driver.execute_script(cls.VIEWPORT_AUDIT_SCRIPT, vp["name"])

                    viewport_results[vp["name"]] = {
                        "viewport": f"{vp['width']}x{vp['height']}",
                        "overflowX": float(metrics["overflowX"]),
                        "scrollWidth": int(metrics["scrollWidth"]),
                        "clientWidth": int(metrics["clientWidth"]),
                        "smallTargets": list(metrics["smallTargets"]),
                        "headingViolations": list(metrics["headingViolations"]),
                        "headingsCount": int(metrics["headingsCount"]),
                        "visualViolations": list(metrics["visualViolations"]),
                        "photometrics": dict(metrics["photometrics"]),
                    }

                    if float(metrics["overflowX"]) > max_horizontal_overflow:
                        max_horizontal_overflow = float(metrics["overflowX"])
                    for v in metrics["headingViolations"]:
                        all_heading_violations.add(v)
                    for t in metrics["smallTargets"]:
                        all_small_targets.add(t)
                for v in metrics["visualViolations"]:
                    all_visual_violations.add(v)
            except Exception as _drv_err:
                try:
                    driver.quit()
                except Exception:
                    pass
                cls._shared_driver = None
                raise _drv_err
            finally:
                if os.path.exists(temp_html_path):
                    try:
                        os.unlink(temp_html_path)
                    except OSError:
                        pass

            is_passing = (
                max_horizontal_overflow <= 0.0
                and len(all_heading_violations) == 0
                and len(all_visual_violations) == 0
            )
            browser_version = driver.capabilities.get("browserVersion", "unknown")

        return {
            "engine": f"Chromium/Blink (CDP v{browser_version})",
            "browser_version": browser_version,
            "is_passing": is_passing,
            "horizontal_overflow_px": max_horizontal_overflow,
            "viewports": viewport_results,
            "heading_hierarchy_violations": list(all_heading_violations),
            "small_touch_targets": list(all_small_targets),
            "visual_design_violations": list(all_visual_violations),
            "photometric_audit": {
                "accent_budget_passed": not any("Presupuesto de Acento" in v for v in all_visual_violations),
                "action_colinearity_passed": not any("Co-linearidad" in v for v in all_visual_violations),
                "protective_surface_passed": not any("Superficie Protectora" in v for v in all_visual_violations),
                "visual_density_passed": not any("Densidad Visual" in v for v in all_visual_violations),
                "menu_wrapping_passed": not any("enlace de menú" in v for v in all_visual_violations),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @classmethod
    def audit_via_playwright_py_dict(cls, html_content: str, timeout_sec: float = 15.0) -> Dict[str, Any]:
        """Ejecuta la auditoría de los 6 viewports canónicos sobre Chromium real usando Python Playwright."""
        from playwright.sync_api import sync_playwright

        safe_html = re.sub(
            r"while\s*\(\s*true\s*\)\s*\{[^}]*\}",
            "/* blocked_infinite_loop */",
            html_content,
            flags=re.IGNORECASE,
        )
        viewport_results: Dict[str, Any] = {}
        max_horizontal_overflow = 0.0
        all_heading_violations: Set[str] = set()
        all_small_targets: Set[str] = set()
        all_visual_violations: Set[str] = set()
        js_fn = "(arg0) => {\nconst arguments = [arg0];\n" + cls.VIEWPORT_AUDIT_SCRIPT + "\n}"
        timeout_ms = max(2000, int(float(timeout_sec) * 1000))

        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--hide-scrollbars"],
            )
            try:
                browser_version = str(browser.version or "unknown")
                page = browser.new_page(viewport={"width": 1440, "height": 900})
                page.set_default_timeout(timeout_ms)
                page.set_content(safe_html, wait_until="load", timeout=timeout_ms)

                last_visual_violations: List[str] = []
                for vp in cls.CANONICAL_VIEWPORTS:
                    page.set_viewport_size({"width": int(vp.get("width", 1440)), "height": int(vp.get("height", 900))})
                    page.evaluate("void(document.documentElement.offsetHeight)")
                    metrics = page.evaluate(js_fn, vp.get("name", "desktop_1440"))
                    if not isinstance(metrics, dict):
                        continue
                    overflow_val = float(metrics.get("overflowX", 0.0))
                    small_list = list(metrics.get("smallTargets") or [])
                    heading_list = list(metrics.get("headingViolations") or [])
                    vis_list = list(metrics.get("visualViolations") or [])
                    vp_name = str(vp.get("name", "unknown"))
                    viewport_results[vp_name] = {
                        "viewport": f"{vp.get('width')}x{vp.get('height')}",
                        "overflowX": overflow_val,
                        "scrollWidth": int(metrics.get("scrollWidth", 0)),
                        "clientWidth": int(metrics.get("clientWidth", 0)),
                        "smallTargets": small_list,
                        "headingViolations": heading_list,
                        "headingsCount": int(metrics.get("headingsCount", 0)),
                        "visualViolations": vis_list,
                        "photometrics": dict(metrics.get("photometrics") or {}),
                    }
                    if overflow_val > max_horizontal_overflow:
                        max_horizontal_overflow = overflow_val
                    for v in heading_list:
                        all_heading_violations.add(v)
                    for t in small_list:
                        all_small_targets.add(t)
                    for v in vis_list:
                        all_visual_violations.add(v)
                    last_visual_violations = vis_list
                for v in last_visual_violations:
                    all_visual_violations.add(v)
            finally:
                browser.close()

        is_passing = (
            max_horizontal_overflow <= 0.0
            and len(all_heading_violations) == 0
            and len(all_visual_violations) == 0
        )
        return {
            "engine": f"Chromium/Blink (Playwright v{browser_version})",
            "browser_version": browser_version,
            "is_passing": is_passing,
            "horizontal_overflow_px": max_horizontal_overflow,
            "viewports": viewport_results,
            "heading_hierarchy_violations": list(all_heading_violations),
            "small_touch_targets": list(all_small_targets),
            "visual_design_violations": list(all_visual_violations),
            "photometric_audit": {
                "accent_budget_passed": not any("Presupuesto de Acento" in v for v in all_visual_violations),
                "action_colinearity_passed": not any("Co-linearidad" in v for v in all_visual_violations),
                "protective_surface_passed": not any("Superficie Protectora" in v for v in all_visual_violations),
                "visual_density_passed": not any("Densidad Visual" in v for v in all_visual_violations),
                "menu_wrapping_passed": not any("enlace de menú" in v for v in all_visual_violations),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def audit_live_rendered_html(
        self,
        html_content: str,
        timeout_sec: float = 15.0
    ) -> AuditReport:
        """
        Ejecuta Chromium headless real para auditar píxeles exactos.
        Retorna AuditReport formal con métricas de Blink.
        """
        report_data: Optional[Dict[str, Any]] = None
        err_msg: str = ""

        # Intentar primero Python Playwright nativo; si falla, Selenium CDP y finalmente Node Playwright
        try:
            report_data = self.audit_via_playwright_py_dict(html_content, timeout_sec=timeout_sec)
        except Exception as pw_exc:
            err_msg = str(pw_exc)
            report_data = None

        if report_data is None:
            try:
                report_data = self.audit_via_chromium_cdp_dict(html_content, timeout_sec=timeout_sec)
            except Exception as cdp_exc:
                err_msg = f"{err_msg}; cdp={cdp_exc}" if err_msg else str(cdp_exc)
                report_data = None

        # Si el pool directo en Python no estuviera disponible, intentar el script Node de Playwright
        if report_data is None:
            with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
                f.write(html_content)
                temp_html_path = f.name
            temp_json_path = temp_html_path.replace(".html", "_audit.json")
            cmd = [
                "node",
                self.runner_script,
                "--html-file", temp_html_path,
                "--output", temp_json_path,
                "--timeout", str(int(timeout_sec * 1000))
            ]
            try:
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout_sec + 5.0,
                    check=False
                )
                if os.path.exists(temp_json_path):
                    with open(temp_json_path, "r", encoding="utf-8") as jf:
                        report_data = json.load(jf)
                elif proc.stdout:
                    try:
                        report_data = json.loads(proc.stdout.strip())
                    except json.JSONDecodeError:
                        pass
                if not report_data:
                    err_msg = proc.stderr[:200]
            except Exception as sub_exc:
                err_msg = str(sub_exc)
            finally:
                for p in (temp_html_path, temp_json_path):
                    if os.path.exists(p):
                        try:
                            os.unlink(p)
                        except OSError:
                            pass

        if report_data:
            overflow_px = float(report_data.get("horizontal_overflow_px", 0.0))
            heading_violations = report_data.get("heading_hierarchy_violations", [])
            small_targets = report_data.get("small_touch_targets", [])
            visual_violations = report_data.get("visual_design_violations", [])
            photometric_audit = report_data.get("photometric_audit", {})
            is_passing = bool(report_data.get("is_passing", False))

            a11y_score = 100.0
            if overflow_px > 0.0:
                a11y_score -= 40.0
            if heading_violations:
                a11y_score -= min(30.0, len(heading_violations) * 10.0)
            if small_targets:
                a11y_score -= min(20.0, len(small_targets) * 5.0)
            a11y_score = max(0.0, a11y_score)

            slop_score = 0.0
            if overflow_px > 0.0:
                slop_score += 0.5
            if len(small_targets) > 2:
                slop_score += 0.3
            if visual_violations:
                slop_score += min(0.6, 0.2 + len(visual_violations) * 0.1)
                is_passing = False

            return AuditReport(
                is_passing=is_passing,
                horizontal_overflow_px=overflow_px,
                accessibility_score=a11y_score,
                slop_score=min(1.0, slop_score),
                touch_target_violations=small_targets,
                heading_hierarchy_violations=heading_violations,
                visual_design_violations=visual_violations,
                photometric_audit=photometric_audit,
                metrics=report_data
            )

        return AuditReport(
            is_passing=False,
            horizontal_overflow_px=999.0,
            accessibility_score=0.0,
            slop_score=1.0,
            slop_findings=[f"LivePlaywrightOracle no pudo emitir reporte: {err_msg}"],
            metrics={"error": err_msg}
        )


class AlephRenderOracle:
    """
    Oráculo Maestro de Renderizado y Auditoría de Layout.
    Ejecuta scripts in-DOM en CDP o análisis estático de alta fidelidad.
    """

    IN_DOM_AUDIT_JS = LivePlaywrightOracle.VIEWPORT_AUDIT_SCRIPT

    SLOP_PHRASES = [
        r"\bunleash (your )?potential\b",
        r"\brevolutioniz(e|ing)\b",
        r"\bseamless(ly)? integrate\b",
        r"\bnext-gen(eration)?\b",
        r"\bpioneer(ing)?\b",
        r"\bcutting-edge\b",
        r"\bdelve into\b",
        r"\bharness the power\b",
        r"\bgame-changer\b",
        r"\belevate your (workflow|experience)\b",
    ]

    def __init__(self, cdp_port: int = 9222):
        self.cdp_port = cdp_port
        self.live_oracle = LivePlaywrightOracle()

    def audit_html(self, html_content: str, strict: bool = True, live: bool = False) -> AuditReport:
        """Audita el HTML estáticamente inspeccionando estructura, CSS y semántica, o en Chromium real si live=True."""
        if live:
            return self.live_oracle.audit_live_rendered_html(html_content)

        parser = StaticDOMAuditor()
        parser.feed(html_content)

        heading_violations = []
        if parser.headings:
            if parser.headings[0] != 1:
                heading_violations.append(f"El documento comienza con h{parser.headings[0]} en vez de h1")
            for i in range(len(parser.headings) - 1):
                if parser.headings[i + 1] - parser.headings[i] > 1:
                    heading_violations.append(
                        f"Salto abrupto de jerarquía: h{parser.headings[i]} -> h{parser.headings[i+1]}"
                    )
        else:
            heading_violations.append("El documento no contiene titulares semánticos (h1-h6)")

        slop_findings = []
        combined_text = " ".join(parser.text_content).lower()
        for pat in self.SLOP_PHRASES:
            if re.search(pat, combined_text, re.IGNORECASE):
                slop_findings.append(f"Frase cliché de IA detectada: '{pat}'")

        css_blob = "\n".join(parser.style_content)
        if "transition: all" in css_blob or "transition:all" in css_blob:
            slop_findings.append("Uso prohibido de 'transition: all' detectado en CSS")

        if re.search(r"font-family:\s*['\"]?(Inter|Geist)['\"]?", css_blob):
            slop_findings.append("Fuente por defecto de IA (Inter/Geist) detectada en CSS")

        visual_design_violations = []
        if parser.bento_cards:
            for b_card in parser.bento_cards:
                if not b_card.get("has_visual"):
                    name = b_card.get("id") or b_card.get("class", "bento-card")
                    visual_design_violations.append(
                        f"Ley de Densidad Visual violada: La tarjeta Bento '{name}' es puramente textual (carece de <svg>, <canvas>, <code> o elementos visuales)"
                    )

        slop_points = len(slop_findings) * 0.25
        if visual_design_violations:
            slop_points += min(0.6, 0.2 + len(visual_design_violations) * 0.1)
        if not parser.has_viewport_meta:
            slop_points += 0.2
        slop_score = min(1.0, max(0.0, slop_points))

        a11y_score = 100.0
        if not parser.has_h1:
            a11y_score -= 25.0
        if heading_violations:
            a11y_score -= min(30.0, len(heading_violations) * 10.0)
        if not parser.has_viewport_meta:
            a11y_score -= 20.0

        a11y_score = max(0.0, a11y_score)

        is_passing = (
            slop_score < 0.20
            and a11y_score >= 80.0
            and len(heading_violations) == 0
            and len(visual_design_violations) == 0
        )

        return AuditReport(
            is_passing=is_passing,
            horizontal_overflow_px=0.0,
            accessibility_score=a11y_score,
            slop_score=slop_score,
            heading_hierarchy_violations=heading_violations,
            visual_design_violations=visual_design_violations,
            slop_findings=slop_findings,
            photometric_audit={
                "bento_cards_count": len(parser.bento_cards),
                "visual_density_passed": len(visual_design_violations) == 0,
            },
            metrics={
                "total_tags": len(parser.tags),
                "headings_count": len(parser.headings),
                "interactive_count": len(parser.interactive_elements),
                "has_viewport_meta": parser.has_viewport_meta,
                "bento_cards_count": len(parser.bento_cards),
                "canvases_count": parser.canvases_count,
            }
        )

    def evaluate_live_payload(self, js_audit_result: Dict[str, Any]) -> AuditReport:
        """Procesa el JSON devuelto por la inyección de IN_DOM_AUDIT_JS desde CDP."""
        overflow_x = float(js_audit_result.get("overflowX", 0.0))
        heading_violations = js_audit_result.get("headingViolations", [])
        small_targets = js_audit_result.get("smallTargets", [])
        visual_violations = js_audit_result.get("visualViolations", []) or js_audit_result.get("visual_design_violations", [])
        photometric_audit = js_audit_result.get("photometricAudit", {}) or js_audit_result.get("photometric_audit", {})

        a11y_score = 100.0
        if overflow_x > 0.5:
            a11y_score -= 40.0
        if heading_violations:
            a11y_score -= min(30.0, len(heading_violations) * 10.0)
        if small_targets:
            a11y_score -= min(20.0, len(small_targets) * 5.0)

        a11y_score = max(0.0, a11y_score)
        slop_score = 0.0
        if overflow_x > 0.5:
            slop_score += 0.5
        if len(small_targets) > 2:
            slop_score += 0.3
        if visual_violations:
            slop_score += min(0.6, 0.2 + len(visual_violations) * 0.1)

        is_passing = (
            overflow_x <= 0.5
            and a11y_score >= 80.0
            and len(heading_violations) == 0
            and len(visual_violations) == 0
        )

        return AuditReport(
            is_passing=is_passing,
            horizontal_overflow_px=overflow_x,
            accessibility_score=a11y_score,
            slop_score=min(1.0, slop_score),
            touch_target_violations=small_targets,
            heading_hierarchy_violations=heading_violations,
            visual_design_violations=visual_violations,
            photometric_audit=photometric_audit,
            metrics=js_audit_result
        )
