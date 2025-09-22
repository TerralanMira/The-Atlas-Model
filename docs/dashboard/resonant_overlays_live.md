# Resonant Overlays — Live

Life first: geometry and plasma are rendered directly from your data.

## Generate

```bash
python -m dashboard.page_overlays_live \
  --coh logs/coherence_matrix.npy \
  --series logs/timeseries.csv \
  --out docs/assets/dashboard/overlays_live.png
If inputs are missing, synthetic examples render so you can see the layout.

Panels
	•	Geometry (TL): NxN coherence → hex lattice projection (part↔whole resonance).
	•	Plasma (TR): time-series → ripple field (ignition waves & dispersion).
	•	Hybrid (BL): blend (geometry × plasma) to see interference patterns.
	•	Stamped (BR): hybrid plus resonant overlay (harmonic grid + FoL).

Data Shapes
	•	coherence_matrix.npy → float64 array, shape (N, N).
	•	timeseries.(csv|npy) → 1D sequence of floats.

Why this matters

Motion precedes meaning.
These overlays give the system a living pulse that later archetypes can interpret.
