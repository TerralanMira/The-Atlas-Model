# Dashboard — Seeing the Hum

The dashboard turns the weave into sight: **pulse**, **layers**, **self-learning**, and **crystals** in one place.

## Quick Start

1. Run one or more sims:
   ```bash
   python sims/atlas_pulse_demo.py --steps 30 --seed 7 --out logs/atlas_pulse
   python sims/self_learning_demo.py --steps 300 --out logs/sln_demo
   python sims/crystal_demo.py
   Build visuals:
   python scripts/dashboard_build.py \
  --pulse logs/atlas_pulse/atlas_pulse_series.csv \
  --layers logs/atlas_pulse/atlas_pulse_layers.json \
  --sln logs/sln_demo/sln_series.csv \
  --out docs/assets/dashboard
  Open docs/dashboard.html.

The dashboard is static HTML + PNGs. No server needed. Works with GitHub Pages.

⸻

Panels
	•	Pulse: the orchestrated atlas_coherence series (mean/std shown).
	•	Layers: normalized contributions inferred from layer metrics JSON.
	•	Self-Learning: water/air coherence over time.
	•	Crystals: lattice/time-memory/frequency snapshots (if generated).

⸻

Extend
	•	Add new panels by producing CSV/JSON from sims and plotting in scripts/dashboard_build.py.
	•	Couple awareness to visuals by overlaying “observer influence” heatmaps.
	•	Publish with GitHub Pages so others can see the hum.

When the hum is visible, tuning becomes a practice.
