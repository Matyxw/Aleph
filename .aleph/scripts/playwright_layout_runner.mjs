#!/usr/bin/env node
/**
 * .aleph/scripts/playwright_layout_runner.mjs
 * Oráculo Físico de Layout con Playwright / Chromium CDP WebDriver (Plan V5/V7 - Track 3).
 *
 * Mide píxeles reales en un motor Chromium/Blink real:
 * - scrollWidth - clientWidth <= 0 (invariante de 0 overflow horizontal)
 * - Dimensiones mínimas de touch targets (40x40 / 44x44px)
 * - Jerarquía semántica de titulares (h1 -> h2 -> h3, sin saltos)
 * - Evaluación en 6 Viewports Canónicos:
 *     1. mobile_320:  320 x 568
 *     2. mobile_375:  375 x 812
 *     3. tablet_768:  768 x 1024
 *     4. tablet_1024: 1024 x 768
 *     5. desktop_1440: 1440 x 900
 *     6. desktop_1920: 1920 x 1080
 */

import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const VIEWPORTS = [
  { name: 'mobile_320', category: 'mobile', width: 320, height: 568 },
  { name: 'mobile_375', category: 'mobile', width: 375, height: 812 },
  { name: 'tablet_768', category: 'tablet', width: 768, height: 1024 },
  { name: 'tablet_1024', category: 'tablet', width: 1024, height: 768 },
  { name: 'desktop_1440', category: 'desktop', width: 1440, height: 900 },
  { name: 'desktop_1920', category: 'desktop', width: 1920, height: 1080 }
];

const DEFAULT_CHROME_PATHS = [
  '/usr/bin/chromium',
  '/usr/bin/chromium-browser',
  '/usr/bin/google-chrome',
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
  process.env.LOCALAPPDATA ? path.join(process.env.LOCALAPPDATA, 'Google\\Chrome\\Application\\chrome.exe') : null
].filter(Boolean);

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    htmlFile: null,
    output: null,
    chromePath: null,
    timeoutMs: 15000
  };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--html-file' && args[i + 1]) {
      options.htmlFile = path.resolve(args[++i]);
    } else if (args[i] === '--output' && args[i + 1]) {
      options.output = path.resolve(args[++i]);
    } else if (args[i] === '--chrome-path' && args[i + 1]) {
      options.chromePath = path.resolve(args[++i]);
    } else if (args[i] === '--timeout' && args[i + 1]) {
      options.timeoutMs = parseInt(args[++i], 10);
    }
  }

  if (!options.htmlFile) {
    console.error(JSON.stringify({
      error: 'Argumento obligatorio ausente: --html-file <path>',
      is_passing: false
    }));
    process.exit(1);
  }

  return options;
}

function resolveChromeExecutable(customPath) {
  if (customPath && fs.existsSync(customPath)) {
    return customPath;
  }
  for (const p of DEFAULT_CHROME_PATHS) {
    if (p && fs.existsSync(p)) {
      return p;
    }
  }
  return null;
}

async function runPhysicalAudit() {
  const options = parseArgs();

  if (!fs.existsSync(options.htmlFile)) {
    const errPayload = {
      error: `Archivo HTML no existe: ${options.htmlFile}`,
      is_passing: false,
      horizontal_overflow_px: 999.0
    };
    if (options.output) fs.writeFileSync(options.output, JSON.stringify(errPayload, null, 2));
    console.log(JSON.stringify(errPayload));
    process.exit(1);
  }

  let playwrightMod = null;
  try {
    playwrightMod = await import('playwright');
  } catch (_err) {
    playwrightMod = null;
  }

  // Fallback soberano a Chromium real vía puente Python Selenium/CDP si el paquete npm playwright no está instalado
  if (!playwrightMod) {
    const scriptDir = path.dirname(fileURLToPath(import.meta.url));
    const alephDir = path.dirname(scriptDir);
    const pyCode = `
import json, sys
sys.path.insert(0, ${JSON.stringify(path.join(alephDir, 'lib'))})
from aleph_render_oracle import LivePlaywrightOracle
html_path = ${JSON.stringify(options.htmlFile)}
out_path = ${options.output ? JSON.stringify(options.output) : "None"}
with open(html_path, 'r', encoding='utf-8') as f:
    html_str = f.read()
report_dict = LivePlaywrightOracle.audit_via_chromium_cdp_dict(html_str, timeout_sec=${options.timeoutMs / 1000.0})
if out_path:
    import os
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as out_f:
        json.dump(report_dict, out_f, indent=2, ensure_ascii=False)
print(json.dumps(report_dict))
sys.exit(0 if report_dict.get('is_passing', False) else 2)
`;
    const pyProc = spawnSync('python3', ['-c', pyCode], { encoding: 'utf-8', timeout: options.timeoutMs + 10000 });
    if (pyProc.stdout) process.stdout.write(pyProc.stdout);
    if (pyProc.stderr && pyProc.status !== 0 && pyProc.status !== 2) process.stderr.write(pyProc.stderr);
    process.exit(pyProc.status ?? 1);
  }

  const { chromium } = playwrightMod;
  const chromePath = resolveChromeExecutable(options.chromePath);
  const launchOpts = {
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu', '--hide-scrollbars']
  };
  if (chromePath) {
    launchOpts.executablePath = chromePath;
  }

  let browser;
  try {
    browser = await chromium.launch(launchOpts);
  } catch (_err) {
    delete launchOpts.executablePath;
    browser = await chromium.launch(launchOpts);
  }

  const fileUrl = pathToFileURL(options.htmlFile).href;
  const viewportResults = {};
  let maxHorizontalOverflow = 0.0;
  const allHeadingViolations = new Set();
  const allSmallTargets = new Set();
  const allVisualViolations = new Set();

  try {
    for (const vp of VIEWPORTS) {
      const context = await browser.newContext({
        viewport: { width: vp.width, height: vp.height },
        deviceScaleFactor: 1
      });
      const page = await context.newPage();

      await page.goto(fileUrl, { waitUntil: 'domcontentloaded', timeout: options.timeoutMs });
      await page.waitForTimeout(80);

      const metrics = await page.evaluate((currentVp) => {
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
          const m = colorStr.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
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
                    const desc = group.className ? `.${group.className.trim().split(/\s+/).join('.')}` : group.tagName.toLowerCase();
                    visualViolations.push(`Ley de Co-linearidad de Acciones violada: Botones en '${desc}' no están alineados en el eje horizontal en Desktop (delta Y = ${deltaY.toFixed(1)}px > 4.0px)`);
                    break;
                  }
                }
              }
            }
          }
        }

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
            const linkTxt = link.innerText.trim().replace(/\s+/g, ' ');
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
      }, vp.name);

      viewportResults[vp.name] = {
        viewport: `${vp.width}x${vp.height}`,
        overflowX: metrics.overflowX,
        scrollWidth: metrics.scrollWidth,
        clientWidth: metrics.clientWidth,
        smallTargets: metrics.smallTargets,
        headingViolations: metrics.headingViolations,
        headingsCount: metrics.headingsCount,
        visualViolations: metrics.visualViolations,
        photometrics: metrics.photometrics
      };

      if (metrics.overflowX > maxHorizontalOverflow) {
        maxHorizontalOverflow = metrics.overflowX;
      }
      metrics.headingViolations.forEach(v => allHeadingViolations.add(v));
      metrics.smallTargets.forEach(t => allSmallTargets.add(t));
      if (metrics.visualViolations) {
        metrics.visualViolations.forEach(v => allVisualViolations.add(v));
      }

      await context.close();
    }
  } finally {
    if (browser) {
      await browser.close();
    }
  }

  const isPassing = maxHorizontalOverflow <= 0 && allHeadingViolations.size === 0 && allVisualViolations.size === 0;

  const report = {
    engine: `Chromium/Blink (Playwright v${chromium._playwright ? '1.x' : 'live'})`,
    browser_version: browser ? browser.version() : 'unknown',
    is_passing: isPassing,
    horizontal_overflow_px: maxHorizontalOverflow,
    viewports: viewportResults,
    heading_hierarchy_violations: Array.from(allHeadingViolations),
    small_touch_targets: Array.from(allSmallTargets),
    visual_design_violations: Array.from(allVisualViolations),
    photometric_audit: {
      accent_budget_passed: !Array.from(allVisualViolations).some(v => v.includes('Presupuesto de Acento')),
      action_colinearity_passed: !Array.from(allVisualViolations).some(v => v.includes('Co-linearidad')),
      protective_surface_passed: !Array.from(allVisualViolations).some(v => v.includes('Superficie Protectora')),
      visual_density_passed: !Array.from(allVisualViolations).some(v => v.includes('Densidad Visual')),
      menu_wrapping_passed: !Array.from(allVisualViolations).some(v => v.includes('enlace de menú'))
    },
    timestamp: new Date().toISOString()
  };

  if (options.output) {
    fs.mkdirSync(path.dirname(options.output), { recursive: true });
    fs.writeFileSync(options.output, JSON.stringify(report, null, 2), 'utf-8');
  }

  console.log(JSON.stringify(report));
  process.exit(isPassing ? 0 : 2);
}

runPhysicalAudit().catch(err => {
  const failure = {
    error: err.message,
    stack: err.stack,
    is_passing: false,
    horizontal_overflow_px: 999.0
  };
  console.error(JSON.stringify(failure));
  process.exit(1);
});
