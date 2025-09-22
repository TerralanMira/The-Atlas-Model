# Cities — Flow & Quiet Zones

**Seed:** Phase-align a single corridor (street, hallway, data queue) to reduce turbulence.  
**Setup:**
- Capture a simple flow proxy: counts per minute → `logs/atlas_pulse/atlas_pulse_series.csv`
  (`step,atlas_coherence` can be a normalized flow-smoothness score).
- Sketch a “charge map” of congestion risk as a 2D array and save for experiments (optional).

**View:**
- **Fields Page** to compare element panels:  
  ```bash
  python -m dashboard.page_fields --out docs/assets/dashboard/fields_page.png
  •	Pulse Page to track corridor coherence over days:
  python -m dashboard.page_pulse --out docs/assets/dashboard/pulse_page.png
  Interpret:
	•	Water/Air panels suggest signage/timing adjustments (continuity vs diffusion).
	•	Plasma arcs show ignition points (bottlenecks); Crystal shows stabilization (new patterns).
	•	Nudge one parameter at a time; re-render next day to see the effect.

Why it works:
Micro-alignments compound: when the corridor’s “breath” regularizes, ignition events (clogs) drop and new structure persists.
