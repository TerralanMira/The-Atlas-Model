# Dashboard (Community Resonance)

Batch plot generator for multilayer resonance simulations.

## Usage
```bash
python dashboard/generate_community_figs.py --preset multilayer_demo
Options
	•	--preset NAME — key in sims/presets.json.
	•	--steps N — override step count for quicker runs.
	•	--outdir PATH — where to write PNGs (default dashboard/out).

What it renders
	•	resonance_over_time.png — global synchrony R(t).
	•	group_resonance.png — per-group curves.
	•	resource_health.png — distribution + mean of resources.
	•	phase_gaps.png — mean absolute phase gaps between groups (if ≥ 2 groups).

Notes
	•	Only uses Matplotlib.
	•	No runtime server required (phone-friendly): produces static images.
