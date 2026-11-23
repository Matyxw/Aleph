# MODE: HYPER_SPEED
Domain: trading, orderbook, terminal, clinical, telemetry, dense tables.
Stack: Astro, Svelte5, SolidJS or Vanilla + CSS @layer. Zero bloat JS.
1. Latency: contain: layout paint, tabular-nums, keyboard-first shortcuts (Cmd+K, j/k, Esc), virtualized >100 rows.
2. Zero CLS & zero scroll-x across 390/1440/2560; fixed column tracks, sticky headers, zero fluff banners.
3. Legibility: WCAG >= 7:1 (APCA >= 75 Lc) for numbers; semantic accent <8% viewport.
4. Motion: <=120ms transform/opacity + @media (prefers-reduced-motion: reduce). Verify via `aleph visual-audit`.
