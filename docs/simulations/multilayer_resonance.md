# Multilayer Resonance

**Goal:** model communities as layered fields (roles, places, media) with resources, adaptation, and environmental rhythms.

## Model Highlights
- **Layers (L):** multiple graphs for different contexts (e.g., practice, neighborhood, online).
- **Interlayer Coupling (γ):** aligns a person’s phases across layers (role coherence).
- **Adaptive Frequencies (α):** agents drift toward local centroids (learning).
- **Resources (r ∈ [0,1]):** higher r → stronger effective coupling K_i.
- **Environment Driver (φ_env):** external rhythm entrains a chosen layer.

## Dynamics
- Per layer: Kuramoto with per-node K_i(r).
- Across layers: sin(ψ_i_across − θ_{l,i}) drives internal alignment.
- Adaptation: ω_i ← ω_i + α * angle(e^{i(ψ_local − θ_{comm,i})}).
- Resources: dr/dt = gain * R_local * (1 − r) − leak * (1 − R_local) r.

## Inputs
- `sims/presets.json: multilayer_demo` defines N, L, K, γ, env drivers, groups, and interventions.
- Uses `algorithms/environment_drivers.py` and metrics in `algorithms/community_metrics.py`.

## Run
```bash
python sims/multilayer_resonance.py --preset multilayer_demo
Readouts
	•	Mean global synchrony ⟨R⟩ on metrics layer.
	•	Group synchrony R_group[g], phase gaps Δψ(g1,g2).
	•	Final mean resource and frequency drift (health + learning proxies).

Interpret
	•	Rising ⟨R⟩ with shrinking Δψ across groups → healthier cross-layer coherence.
	•	Resource ↑ → K_i ↑ → easier entrainment (but watch for monoculture).
	•	Interventions (bridges, noise reduction) should stabilize R and reduce fragmentation episodically.
