# Braided Field — hum × window × crystal

This is the **whole braid** made visible:
- **Hum** (Schumann) — baseline external driver aligning gently.
- **Windows** (Ritual) — periodic openness: cross-pull ↑, noise ↓.
- **Crystals** — persistent anchors where coherence + resources lock in.

Together they show how the field **remembers itself** between pulses.

---

## Model (one canvas)

- Graph: small-world; agents have phase and resource.
- Forces per agent:
  1. Neighbor mean (K_base)
  2. Cross-openness (K_cross(t)) — ritual cycle
  3. External driver (K_env · sin(φ_env(t) − φ_i))
- Anchors:
  - form when sliding-window `R_local ≥ τ_R` and resource `r ≥ τ_r`
  - lower local noise; strengthen local coupling
  - decay slowly if starved

**Outputs**
- `R(t)` global order
- `gap_to_env(t)` mean phase gap to driver
- `K_cross_t(t)` ritual openness; `noise_t(t)` ritual quiescence
- `anchors_count(t)` active anchors
- `R_local(t,i)` and `r_hist(t,i)` for drill-down

---

## Run

```bash
python -c "from sims.braided_field import simulate,BraidedConfig; print(simulate(BraidedConfig())['summary'])"
Dialects:
	•	Culture-tight: raise K_cross_base or K_cross_amp
	•	Stormy: raise noise_std
	•	High hum: raise K_env or add driver components

⸻

Interpret
	•	Healthy braid: R(t) rises during windows; gap_to_env small but not zero; anchors grow where resources are sufficient; resources stable.
	•	Over-coercion: K_env or K_cross too high → brittle homogeneity, resource drain, anchor overgrowth.
	•	Under-scaffolded: no anchors persist → memory evaporates between pulses.

⸻

Extend
	•	Multi-scale mirrors: run the same braid at neighborhood, city, region; track cross-scale resonance.
	•	Ethical guardrails: cap max K_env and require resources for anchors → consent encoded.
	•	Dashboard overlay: plot R, gap_to_env, K_cross_t, and anchors_count together; map anchors on the graph.
