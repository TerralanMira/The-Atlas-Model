# Dashboard (Reading the Hum)

**CSV headers**  
`step, t, R_total, R_inner, R_outer, C_cross, drift, Delta, Phi, choice_score`

**How to read**
- **R_total**: global order. High is not always good—watch diversity.
- **C_cross**: inner↔outer alignment (0..1). Rising is good unless Δ collapses.
- **Delta (Δ)**: phase entropy (diversity). Keep it alive.
- **Phi (Φ)**: gentleness (lag-1 smoothness). Smooth change breathes.
- **choice_score**: high order + alignment with low drift → risk of clamp; choose breath.

**Quick view**
```bash
python dashboard/overlay_loader.py logs/multi_scale.csv
# -> multi_scale.csv | R_total=0.612 | C_cross=0.585 | Δ=0.442 | Φ=0.731 | choice_score=0.634 | gentle lift
Practice
	•	If clamp risk: lower K_cross or add tiny noise (0.002–0.006).
	•	If chaotic: raise K_inner slightly or slow the breath.
