# File: sims/cymatic_lattice_growth.py
#!/usr/bin/env python3
from __future__ import annotations
import argparse, math
import numpy as np

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--nx", type=int, default=96)
    ap.add_argument("--ny", type=int, default=96)
    ap.add_argument("--steps", type=int, default=1500)
    ap.add_argument("--omega", type=float, default=2.0)  # drive frequency
    ap.add_argument("--k", type=float, default=0.12)     # spatial wavenumber
    ap.add_argument("--damp", type=float, default=0.03)
    ap.add_argument("--thresh", type=float, default=0.9) # deposition threshold
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args(argv)

    rng = np.random.default_rng(args.seed)
    X, Y = np.meshgrid(np.linspace(0,1,args.nx), np.linspace(0,1,args.ny), indexing="ij")
    phase = 2*math.pi*(args.k*X + args.k*Y) + rng.uniform(0,2*math.pi,(args.nx,args.ny))
    v = np.zeros_like(phase)     # velocity-like
    u = np.sin(phase)            # displacement-like
    deposit = np.zeros_like(u)

    print("t,active_fraction,mean_dep")
    dt = 0.05; t=0.0
    for _ in range(args.steps):
        forcing = np.sin(args.omega*t)  # standing wave drive
        lap = -4*u
        lap += np.roll(u,1,0)+np.roll(u,-1,0)+np.roll(u,1,1)+np.roll(u,-1,1)
        v = (1-args.damp)*v + 0.4*lap + 0.6*forcing
        u = u + dt*v
        # “crystallize” where |u| exceeds threshold and keep it
        mask = (np.abs(u) > args.thresh)
        deposit = np.maximum(deposit, mask.astype(float))
        active = float(mask.mean())
        mean_dep = float(deposit.mean())
        print(f"{t:.3f},{active:.6f},{mean_dep:.6f}")
        t += dt
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
