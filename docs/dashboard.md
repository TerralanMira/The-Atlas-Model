# Dashboard (Reading the Hum)

You don’t need plots to hear the field — start with numbers.

**CSV columns** (from sims):
- `R_total` — global order (0..1)
- `R_inner`, `R_outer` — layer orders
- `C_cross` — inner↔outer alignment proxy (0..1)

**Quick reads**
- **Clamp risk**: R_total high while diversity (spread you feel) is low and change is tiny.
- **Gentle lift**: R_total↑ with smooth steps; cross-alignment rises without flattening.

**CLI helper**
```bash
python dashboard/overlay_loader.py logs/multi_scale.csv
Expect a one-line summary + qualitative note (clamp risk / gentle learning / mixed).
