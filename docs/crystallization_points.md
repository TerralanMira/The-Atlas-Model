# Crystallization Points

Crystallization points are **persistent anchors of coherence**.  
They form when local alignment stays high *and* resources are sufficient; they dissolve if starved.

This layer makes the **“locks in”** from Resonant Reality testable.

---

## Model

- Graph: small-world network; nodes are agents with phases and resources `r∈[0,1]`.
- Dynamics: neighbor-mean Kuramoto + noise.
- **Crystallize** when:
  - sliding-window local coherence `R_local` ≥ threshold, and
  - resource `r` ≥ threshold.
- **Anchor effects**:
  - stronger effective coupling near anchors,
  - lower noise on anchors,
  - slow decay if resources drop (half-life).

Outputs:
- `R(t)` global coherence,
- `R_local(t,i)` local coherence per node,
- `anchors_count(t)` active anchors,
- `r_hist(t,i)` resources.

---

## Run

```bash
python -c "from sims.crystallization_points import simulate,CrystalConfig; print(simulate(CrystalConfig())['summary'])"
Tune:
	•	thresh_R_local, thresh_resource → formation gate
	•	K_anchor_boost, noise_anchor_drop → anchor strength
	•	anchor_half_life, starve_threshold → resilience vs adaptability

⸻

Interpret
	•	Healthy scaffolding: anchors emerge where coherence is earned and resources are ample; they persist between pulses without freezing the field.
	•	Brittle ossification: anchors everywhere, r trending down → structure overdraws energy.
	•	Drift: no anchors, or they decay instantly → coherence lacks carriers.

⸻

Extend
	•	Couple to Schumann Pulse and Ritual Windows:
	•	pulses raise R_local → crystallization,
	•	windows lower noise → anchor formation,
	•	between events, anchors hold memory.
	•	Add spatial geometry (grid/coords) and render anchor maps on the dashboard.
	•	Track anchor lineages: where anchors migrate; which ones seed others.
