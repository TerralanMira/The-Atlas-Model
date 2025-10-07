# Coherence Thresholds (ρ, λ, μ)

**Goal:** make the observation layer *auditable* and *falsifiable*.

| Parameter | Sweep                  | Expected effect                                   | Metric/Pass |
|-----------|------------------------|----------------------------------------------------|-------------|
| ρ         | 0.0 → 0.9 (Δ=0.1)      | σ_eff ↓; mean R ↑; var(R) ↓                        | pass if d⟨R⟩/dρ > 0 |
| λ         | 0.0 → 0.4 (Δ=0.05)     | fewer spin-outs; shorter recovery after noise      | pass if τ_recover ↓ |
| μ         | 0.0 → 0.9 (Δ=0.1)      | smoother transients; better memory under shocks    | pass if MSE_hist ↓  |

### Protocol
1. Fix baseline sim (e.g., community Kuramoto).
2. For each parameter, sweep others fixed.
3. Inject noise bursts at steps {1000, 2000}; measure **τ_recover** to baseline R.
4. Log JSONL: `sims/out/hum_*.jsonl` and publish summary plots.

### Falsifiers
- Flat or negative slope in ⟨R⟩ vs ρ.
- λ increases instability (more spin-outs).
- μ causes drift (worse MSE vs baseline).
