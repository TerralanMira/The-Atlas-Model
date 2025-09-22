# Health — Nervous System Coherence

**Seed:** 60-second cadence (exhale-extend + micro-pause) 3×/day.  
**Setup:**
- Log a time series `logs/atlas_pulse/atlas_pulse_series.csv` with columns:
  - `step,atlas_coherence` (one sample per second is fine)
- Optionally record layer hints to `logs/atlas_pulse/atlas_pulse_layers.json`
  (e.g., `"Water": {"breath_smooth": 0.7}`, `"Crystal": {"routine": 0.6}`).

**View:**
- Generate **Pulse Page**:  
  ```bash
  python -m dashboard.page_pulse --out docs/assets/dashboard/pulse_page.png
  Generate Awareness Page (optional overlay comparison):
  python -m dashboard.page_awareness --out docs/assets/dashboard/awareness_page.png
  Interpret:
	•	A healthy shift shows smoother Pulse (fewer spikes), and rising Crystal contribution.
	•	If Plasma spikes early, lower intensity; if Water collapses, shorten sessions.
	•	Re-run weekly; compare PNGs side-by-side in your notes.

Why it works:
Breath continuity (Water) spreads attention (Air), lowers ignition threshold variance (Plasma), and crystallizes routine (Crystal).
Awareness completes the loop.
