# Harmonic Observation

**Claim:** Observation lowers effective noise and stabilizes coherence.  
**Model:** Kuramoto with σ_eff = σ · e^{-ρ}, optional ethics stabilizer λ.

**Run**
```bash
python -m sims run harmonic_observation --n 256 --K 1.2 --rho 0.6 --lam 0.2
Outputs: sims/figures/harmonic_observation_R.png, sims/out/harmonic_observation_metrics.csv

Pass: At equal K, increasing ρ monotonically increases mean R and reduces variance.
Falsifier: R statistics unchanged across ρ sweeps (check σ, dt, seeds).
