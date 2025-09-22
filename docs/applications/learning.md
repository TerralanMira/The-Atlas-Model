# Learning — Spaced Resonance

**Seed:** 10-minute resonance block: 5×1-minute cycles (retrieve → reflect → breathe).  
**Setup:**
- Track subjective coherence per minute (0–1) → `logs/atlas_pulse/atlas_pulse_series.csv`.
- Optional layer hints per session in `logs/atlas_pulse/atlas_pulse_layers.json`:
  - `"Air": {"novelty_spread": 0.6}`, `"Crystal": {"schema_lock": 0.7}`.

**View:**
- **Pulse Page** to see session rhythm and between-session consolidation:  
  ```bash
  python -m dashboard.page_pulse --out docs/assets/dashboard/pulse_page.png
  Awareness Page to visualize attention modulation across topics:
  python -m dashboard.page_awareness --out docs/assets/dashboard/awareness_page.png
  Interpret:
	•	Healthy pattern: small Plasma spikes on retrieval, then Crystal rising across weeks.
	•	If Air overwhelms (too many topics), narrow scope; if Water is flat, add cadence breaks.

Why it works:
Retrieval (Plasma) reshapes maps; short breaths (Water) stabilize; spreading (Air) prevents ruts; schemas (Crystal) retain.
