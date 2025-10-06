# Entropy Drift

**Claim:** Alignment decays without feedback; periodic corrections restore coherence.  
**Model:** Scalar a(t) with decay γ and pulse gain g each T steps.

**Run**
```bash
python -m sims run entropy_drift --gamma 0.0015 --pulse_T 1000 --gain 0.25
Outputs: sims/figures/entropy_drift.png, sims/out/entropy_drift.csv

Pass: Lower γ or nonzero pulses increase mean a(t) and slow decay.
Falsifier: a(t) unchanged by pulses vs. no-pulse runs.
