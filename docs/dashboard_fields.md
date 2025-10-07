# Dashboard Field Dictionary

This page defines the canonical fields produced by Atlas sims and used by plots/dashboards.

## Core Metrics
- **step** *(int)* — simulation step (0-indexed).
- **R** *(float, 0..1)* — global coherence |⟨e^{iθ}⟩|.
- **psi** *(float, rad)* — mean phase angle of the field.
- **R_blocks_mean** *(float)* — mean coherence across blocks (for block models).
- **R_H, R_A, R_all** *(float)* — human, AI, and combined coherence (atlas_coherence).
- **energy** *(float)* — model-specific energy/lyapunov proxy if defined.
- **loss / drift** *(float)* — entropy or alignment drift metric (entropy_drift).

## Observation Layer (Hum Kernel)
- **rho (ρ)** *(float)* — observation dial; increases effective damping of noise.
- **lam (λ)** *(float)* — ethics/stability; gentle pull toward shared phase.
- **mu (μ)** *(float)* — memory mix; EMA of prior state features.
- **sigma_eff_scale** *(float)* — multiplier applied to base σ (noise).
- **coupling_bias** *(float)* — additive coupling bias derived from λ and R.
- **memory_mix** *(float)* — EMA weight actually applied this step.

## Provenance
- **sim_name** *(str)* — simulation identifier.
- **run_id** *(str)* — unique id per run; ties CSV ↔ JSONL logs.
- **seed** *(int)* — PRNG seed.

> **Contract:** any dashboard or notebook should read these fields without schema drift. Add new fields with clear units; never repurpose names.
