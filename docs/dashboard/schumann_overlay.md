# Schumann Overlay — Background Rhythm Visual

This overlay shows the canonical Schumann pulse used by Atlas as a background rhythm for entrainment visuals.

## How to generate

1. Create the pulse:
```bash
python -m sims.schumann_sim --input logs/timeseries.csv --out logs/schumann/pulse.npy --overlay docs/assets/dashboard/schumann_overlay.png
Compute entrainment:
python -m algorithms.schumann --pulse logs/schumann/pulse.npy --flows logs/raw/example.csv --out logs/schumann/entrainment.csv
In the dashboard, add the overlay image docs/assets/dashboard/schumann_overlay.png as a background strip for the Pulse panel.
Use logs/schumann/entrainment.csv to color-code elements by entrainment score in the Awareness panel.
Interpretation
	•	Bright/strong waveform: stable canonical pulse.
	•	Low/flattened waveform: low background rhythm—expect lower entrainment.
