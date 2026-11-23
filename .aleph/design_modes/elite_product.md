# MODE: ELITE_PRODUCT
Domain: SaaS apps, Linear/Vercel/Raycast workspaces, dashboards, billing.
Stack: Next.js/React19 + TypeScript strict + CSS @layer OKLCH dual tokens (light/dark).
1. Spatial: Bento 4/8px grid, crisp 1px borders, coherent radius scale, tracking-tight display, 14-16px body.
2. States: full 7-state components (default, hover, active, focus-visible, disabled, loading, error); zero dead actions.
3. Physics: transform/opacity only (never wildcard/layout transitions) + prefers-reduced-motion.
4. Craft: real metrics, SVG/chart/code stages in Bento cards; zero Lorem or violet slop. Verify via `aleph visual-audit`.
