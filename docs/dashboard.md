# Dashboard (reading the hum)

**CSV columns from sims**
- `R_total`, `R_inner`, `R_outer` — coherence at each scale
- `C_cross` — inner↔outer alignment proxy (0..1)

**Quick reads**
- **Clamp risk**: R_total high *and* diversity low (you’ll feel it) *and* drift tiny.
- **Gentle lift**: R_total↑ while steps are smooth; cross rises without Δ collapse.

**CLI helper**
```bash
python dashboard/overlay_loader.py logs/multi_scale.csv
