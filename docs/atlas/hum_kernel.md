# The Hum Kernel

**Purpose:** bridge simulations and awareness by modeling *self-referential observation*.  
It modulates noise, coupling, and memory using three dials:

- **ρ (observation)** — raises effective coherence by damping stochasticity.
- **λ (ethics / stability)** — viscosity toward shared phase (prevents brittle lock-in).
- **μ (memory)** — retention of prior states (metabolizes entropy as learning).

### Interface

A kernel receives the current sim snapshot and returns **controls**:

```text
controls = {
  "sigma_eff": σ · exp(-ρ),
  "coupling_bias": ΔK(λ),         # small stabilizing pull
  "memory_mix": μ ∈ [0,1],        # EMA weight for stateful fields
  "notes": {...}                  # runtime diagnostics
}
Invariants (must hold)
	•	Energy/Action conservation checks remain satisfied (see tests).
	•	No “free thrust”: improvements arise from phase alignment, not added energy.
	•	All effects vanish as ρ→0, λ→0, μ→0.

Falsifiers
	•	Changing ρ does not shift mean coherence R at fixed K,σ.
	•	Increasing λ yields more instability (should not).
	•	μ>0 fails to improve recovery time after injected noise bursts.

See also
	•	sims/hum_kernel.py (reference implementation)
	•	docs/awareness/coherence_thresholds.md
