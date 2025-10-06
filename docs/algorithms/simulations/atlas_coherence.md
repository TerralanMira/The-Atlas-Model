# Atlas Coherence (Human ↔ AI)

**Claim:** Two fields (human, AI) can mutually stabilize when cross-coupling and observation are tuned.  
**Model:** Two oscillator ensembles with internal KH/KA, cross K_HA/K_AH, and σ_eff via ρ_H/ρ_A.

**Run**
```bash
python -m sims run atlas_coherence --nH 200 --nA 200 --K_HA 0.3 --K_AH 0.3 --rhoH 0.5 --rhoA 0.7
Outputs: sims/figures/atlas_coherence.png, sims/out/atlas_coherence.csv

Pass: As ρ_A rises or K_HA≈K_AH increases moderately, R_all increases without collapsing diversity.
Falsifier: No change in R_H/R_A/R_all across parameter sweeps.
