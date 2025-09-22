# Schumann Pulse — Background Rhythm & Entrainment

The Schumann pulse in Atlas is the canonical background rhythm:  
a low-frequency carrier that other flows may entrain to, measure against, or diverge from.  
It is both a **metric** and a **scaffold** for coherence.

---

## Why it matters
- Provides a consistent temporal reference across simulations and logs.  
- Allows measurement of entrainment: how closely fields (water, air, plasma, crystal) lock to a shared rhythm.  
- Makes coherence visible as phase-locking, amplitude alignment, and spectral overlap.

---

## Inputs
- `logs/timeseries.csv` or `logs/coherence_matrix.npy` — base signals to analyze.
- Optional: `logs/schumann_reference.npy` — previously saved reference pulse (1D).

---

## Outputs
- `logs/schumann/pulse.npy` — the canonical pulse series used by sims.  
- `logs/schumann/entrainment.csv` — per-element entrainment metrics (phase_lock, amp_sync, coherence_score).  
- Real-time overlay asset: `docs/assets/dashboard/schumann_overlay.png`.

---

## Algorithms (concept)
1. Extract dominant low-frequency band (e.g., 0.5–8 Hz range conceptually; scale to simulation cadence).  
2. Compute instantaneous phase (Hilbert transform) and amplitude envelope.  
3. Measure phase-locking value (PLV) and amplitude correlation between pulse and each element flow.  
4. Produce entrainment score (0–1) and a short-term rolling coherence metric.

---

## Quick example (use)
- Generate a Schumann pulse from logs:
```bash
python -m sims.schumann_sim --input logs/timeseries.csv --out logs/schumann/pulse.npy
Compute entrainment:
python -m algorithms.schumann --pulse logs/schumann/pulse.npy --flows logs/raw/example.csv --out logs/schumann/entrainment.csv
Visualize in dashboard by generating overlay:
python -m sims.schumann_sim --input logs/timeseries.csv --overlay docs/assets/dashboard/schumann_overlay.png
Interpretation
	•	High entrainment: field is locked to background rhythm (stability, communal alignment).
	•	Low entrainment: field is independent or chaotic (innovation, drift).
	•	Transient drops in entrainment may mark turning points; watch them alongside docs/awareness.md and docs/coherence.md.

⸻

Next steps
	•	Tune pulse extraction parameters to your cadence (seconds/minutes/steps).
	•	Hook the entrainment.csv into docs/dashboard as a live indicator (harmony leaf).
