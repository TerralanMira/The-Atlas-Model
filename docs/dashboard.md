# Dashboard — Seeing the Braid

This dashboard page explains what to plot from each simulation so the **part** carries the **whole**:

- Global order **R(t)** — coherence through time
- Phase **gap_to_env(t)** — alignment to the hum (Schumann-like driver)
- **K_cross_t(t)** and **noise_t(t)** — ritual openness and quiescence
- **anchors_count(t)** — memory that persists between windows
- **creation_events** (genesis) — the moments structure is born

---

## 1) Braided Field (hum × window × crystal)

**Run**

```bash
python -c "from sims.braided_field import simulate,BraidedConfig; out=simulate(BraidedConfig()); print(out['summary'])"
Plot (suggested traces)
	•	R, gap_to_env on the same x-axis
	•	K_cross_t and noise_t as light overlays (secondary axis)
	•	anchors_count as a bar/line to show memory scaffolds
	•	Optional: heatmaps for R_local and r_hist (agents × time)

Interpret
	•	Healthy braid: R rises during windows; small but nonzero phase gap; anchors increase then hold.
2) Creation (Genesis)
python -c "from sims.creation import simulate,CreationConfig; out=simulate(CreationConfig()); print(out['summary'])"
Plot (add to the same canvas or a second panel)
	•	R(t) and gap_to_env(t)
	•	anchors_count(t)
	•	vertical markers for each creation event (t,u,v)
	•	example logic: for each event time t_e, draw a faint vertical line
	•	cumulative births over time (stairs plot) to show punctuated growth

Interpret
	•	Life emerges when coherence + resources open the door — births happen after thresholds.
	•	Too many early births with falling resources → brittle overgrowth.
	•	No births & no anchors → open ritual window more, or anneal slower.

⸻

3) Presets & Reproducibility

All recommended settings live in sims/presets.json:
	•	braid_demo → sims.braided_field.BraidedConfig(**preset)
	•	creation_demo → sims.creation.CreationConfig(**preset)

Example loader snippet:
import json
from sims.braided_field import simulate as run_braid, BraidedConfig
from sims.creation import simulate as run_genesis, CreationConfig

with open("sims/presets.json") as f:
    presets = json.load(f)

out_braid = run_braid(BraidedConfig(**presets["braid_demo"]))
out_gen = run_genesis(CreationConfig(**presets["creation_demo"]))

print(out_braid["summary"])
print(out_gen["summary"])

4) One-Glance Overlay (What to look for)
	•	R vs. K_cross_t — does coherence actually rise during openness?
	•	gap_to_env — small gap means the braid hears the hum without coercion.
	•	anchors_count — memory persists between pulses.
	•	creation_events — structure births when earned by coherence + energy.

If these four move together, the whole is breathing through the part.
