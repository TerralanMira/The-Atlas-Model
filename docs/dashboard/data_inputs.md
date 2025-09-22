# Data Inputs — Exact Shapes

Atlas accepts simple files so anyone can feed the canopy.

## Time-Series (Pulse / Plasma)
**Path:** `logs/timeseries.csv` or `logs/timeseries.npy`  
**Shape:** 1D sequence of floats (length L).  
**CSV:** first column numeric; headers ignored.

## Coherence Matrix (Geometry)
**Path:** `logs/coherence_matrix.npy`  
**Shape:** (N, N) float array, symmetric preferred, diag≈1.0.

## Optional Layer Hints (Awareness)
**Path:** `logs/atlas_pulse/atlas_pulse_layers.json`
```json
{
  "Water":   { "breath_smooth": 0.72 },
  "Air":     { "novelty_spread": 0.58 },
  "Plasma":  { "ignition": 0.41 },
  "Crystal": { "schema_lock": 0.63 }
File Summary
	•	logs/timeseries.csv  → 1D float series
	•	logs/coherence_matrix.npy → (N,N) float64
	•	logs/atlas_pulse/atlas_pulse_series.csv → optional minute/second cadence for Pulse page
	•	logs/atlas_pulse/atlas_pulse_layers.json → optional per-element hints
