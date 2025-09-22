# Resonant Overlays — Live

Life first: geometry and plasma are rendered directly from your data.  
Meaning next: **archetypes** tint and stamp the patterns so the story is legible.

## Generate

```bash
# with defaults (synthetic data)
python -m dashboard.page_overlays_live --archetype Seer --out docs/assets/dashboard/overlays_live.png

# with your data
python -m dashboard.page_overlays_live \
  --coh logs/coherence_matrix.npy \
  --series logs/timeseries.csv \
  --archetype Forge \
  --out docs/assets/dashboard/overlays_live.png
Panels
	•	Geometry (TL) — NxN coherence → hex lattice.
	•	Plasma (TR) — time-series → ripple field.
	•	Hybrid (BL) — blended interference.
	•	Stamped (BR) — hybrid + resonant overlay + archetype tint & symbols.

Archetypes

Pick one: Seer, Weaver, Forge, Grove.
Define more in algorithms/archetypes.py.

Why it matters

Motion becomes legible meaning.
Teams can point at the same picture and move together.
