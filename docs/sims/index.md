# Simulations

All sims expose a `main(args)` so they can be launched with:

```bash
python -m sims --list
python -m sims run community_kuramoto --n 256 --K 1.2 --rho 0.6
Name
Summary
Example
community_kuramoto
Multi-community sync & recovery
python -m sims run community_kuramoto --n 256 --K 1.2
multi_scale_kuramoto
Cross-scale coupling
python -m sims run multi_scale_kuramoto --levels 3
kuramoto_schumann_hybrid
Global cavity + local sync
python -m sims run kuramoto_schumann_hybrid --K 1.0
schumann_sim
Cavity mode toy
python -m sims run schumann_sim --steps 5000
 more rows as modules adopt main(args).
