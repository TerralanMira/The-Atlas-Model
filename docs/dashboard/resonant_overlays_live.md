# Resonant Overlays — Live

Panels:
- **Geometry (TL)**: coherence (NxN) → hex lattice energy field.  
- **Plasma (TR)**: time-series → ripple field with dispersion.  
- **Hybrid (BL)**: geometry × plasma blend.  
- **Stamped (BR)**: hybrid + resonant grid + archetype tints & symbols.

**Generate:**
```bash
python -m dashboard.page_overlays_live \
  --coh logs/coherence_matrix.npy \
  --series logs/timeseries.csv \
  --archetype Seer \
  --out docs/assets/dashboard/overlays_live.png
Inputs: see Data Inputs.
