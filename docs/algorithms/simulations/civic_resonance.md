# Civic Resonance

**Claim:** Cities organize as coupled communities; strong local coherence + modest global coupling yields stable global R.  
**Model:** Blocks with Kintra (local) and Kglobal (city mean).

**Run**
```bash
python -m sims run civic_resonance --n 400 --blocks 8 --Kintra 1.2 --Kglobal 0.4
Outputs: sims/figures/civic_resonance_R.png, sims/out/civic_resonance.csv

Pass: With low Kglobal, block R ≫ global R; increasing Kglobal raises global R while preserving block R.
Falsifier: No differential between block and global across sweeps.
