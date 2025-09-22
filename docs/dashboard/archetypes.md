# Archetypes — Meaning Layer

Life moves first; then we see the pattern and name it.  
Archetypes tint the living overlays so the meaning is legible at a glance.

## Palette & Symbol

Each archetype maps to:
- **Palette**: background, mid, highlight, accent (rgba 0–1).
- **Symbol**: a simple glyph (circle/triangle/hex/spiral) placed on peaks.

| Archetype | Essence                  | Palette (bg, mid, hi, acc)     | Symbol   |
|-----------|--------------------------|---------------------------------|----------|
| Seer      | clarity / insight        | deep-navy, teal, mint, white    | circle   |
| Weaver    | relation / pattern       | indigo, violet, lilac, gold     | triangle |
| Forge     | ignition / transformation| charcoal, ember, orange, yellow | hex      |
| Grove     | growth / stabilization   | forest, moss, leaf, cream       | spiral   |

> Palettes are applied as **tints** on top of the generated fields; symbols stamp local maxima.

## How It Works

1. Compute overlays (geometry from coherence; plasma from time series).  
2. **Archetype → tint** adjusts hue/contrast for legibility.  
3. **Archetype → symbol** stamps 3–7 high-salience points.  
4. Result is still data-true, now **story-readable**.

## Use in Pages

- `dashboard/page_overlays_live.py --archetype Seer`  
- The same switch can be added to Pulse / Awareness pages.

## Extend

Add new entries in `algorithms/archetypes.py`:
- define palette RGBA tuples in \[0,1],
- pick a symbol: `"circle" | "triangle" | "hex" | "spiral"`.

Meaning remains a layer on top of life—the hum through color and sign.
