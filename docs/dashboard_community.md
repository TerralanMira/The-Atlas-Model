# Community Resonance — Dashboard

This layer visualizes multilayer resonance: global synchrony, group alignments, resource health, and effects of interventions.

## What it shows
- **R(t)**: global resonance over time.
- **Rᵍ(t)**: per-group resonance curves (inner/practice/city/etc.).
- **Δψ(t)**: phase gaps between groups (optional overlay).
- **Resource Health**: distribution and mean over time.
- **Intervention Windows**: shaded spans when presets change coupling/noise/bridges.

## How it works
Under the hood, we run `sims/multilayer_resonance.py` with a chosen preset (see `sims/presets.json`), collect phases and groups, then render with Matplotlib (pure, no seaborn).

## Quickstart
```bash
# from repo root
python dashboard/generate_community_figs.py --preset multilayer_demo
Outputs go to dashboard/out/:
	•	resonance_over_time.png
	•	group_resonance.png
	•	resource_health.png
	•	phase_gaps.png (if groups ≥ 2)

Customize
	•	Tune sims/presets.json (N, L, K, γ, drivers, interventions).
	•	Switch --preset to compare scenarios.
	•	Hook into a live web UI later (Streamlit/Gradio); plots here are portable PNGs.

Read the plots
	•	Rising R(t) with stable plateaus → coherent field forming.
	•	Converging Rᵍ(t) across groups → cross-group alignment (less siloing).
	•	Narrowing phase gaps → shared rhythm building.
	•	Improving resource stats → capacity amplifies coupling; coherence sustains capacity.

These instruments sit on the bridge between models and communities: truthful measurements, legible change.
