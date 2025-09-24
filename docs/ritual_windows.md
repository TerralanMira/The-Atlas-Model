# Ritual Windows

Rituals are **periodic openings in the field**:  
moments when cross-group bridges strengthen and noise drops, allowing memory to refresh.

---

## Dynamics

- **Cross-coupling rises** (K_cross ↑) → groups open their canopies to one another.  
- **Noise drops** (σ ↓) → signals become clearer, less interference.  
- **Gap narrows** → mean phases align across groups.  
- After the window closes, diversity and noise return, keeping the system adaptive.

---

## Simulation

We encode ritual cycles as sinusoidal modulations of coupling and noise:

```bash
python -c "from sims.ritual_window import simulate,RitualConfig; print(simulate(RitualConfig())['R_global'][:10])"
Outputs:
	•	R_groups(t) : within-group coherence
	•	R_global(t) : global coherence
	•	gap(t) : mean phase difference between groups
	•	K_cross_t, noise_t : the ritual cycle drivers

⸻

Interpret
	•	Healthy rituals: coherence ↑ during windows, then relax back without collapse.
	•	Over-tight windows: K_cross too high, groups fuse → brittle homogeneity.
	•	Too shallow: K_cross too weak, no bridge → isolation persists.

⸻

Extend
	•	Multiple frequencies: combine cycles (daily, seasonal, generational).
	•	Resource tie-in: rituals recharge or deplete shared resources.
	•	Visual dashboards: plot layering of R_global, gap, and K_cross_t.

Ritual windows are memory in time — scheduled coherence that refreshes the whole.
