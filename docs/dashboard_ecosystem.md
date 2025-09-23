# Ecosystem Overlays — Reading the Field

**Why:** Resonance doesn’t arise in a vacuum. This panel pairs community dynamics with external rhythms and resource health.

## Panels
- **Environment Phase φ_env(t)** — the driver(s) steering entrainment (e.g., Schumann, seasonal).
- **Resource Health r(t)** — capacity rising/falling over time, mean ± variability.
- **Before/After Interventions** — mean R pre/post the first intervention window.

## Use
```bash
python dashboard/generate_community_figs.py --preset multilayer_demo
Images saved under dashboard/out/:
	•	environment_phase.png
	•	resource_over_time.png
	•	before_after_intervention.png

Interpret
	•	φ_env(t) stable + R(t) rising → clean entrainment.
	•	r(t) ↑ with shrinking group gaps → healthier, less brittle coherence.
	•	Pre→Post lift in mean R validates the intervention; if not, adjust K, γ, noise, or bridges in sims/presets.json.
