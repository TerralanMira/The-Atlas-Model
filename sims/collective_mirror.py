#!/usr/bin/env python3
from __future__ import annotations
import argparse, math
import numpy as np

def order_param(theta):
    z = np.exp(1j*theta).mean()
    return abs(z), math.atan2(z.imag, z.real)

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n1", type=int, default=120)
    ap.add_argument("--n2", type=int, default=120)
    ap.add_argument("--K_in", type=float, default=1.1)     # within-group
    ap.add_argument("--K_cross", type=float, default=0.35) # between groups
    ap.add_argument("--rho", type=float, default=0.6)
    ap.add_argument("--sigma", type=float, default=0.45)
    ap.add_argument("--dt", type=float, default=0.02)
    ap.add_argument("--T", type=float, default=40.0)
    ap.add_argument("--seed", type=int, default=3)
    args = ap.parse_args(argv)

    rng = np.random.default_rng(args.seed)
    th1 = rng.uniform(-math.pi, math.pi, size=args.n1)
    th2 = rng.uniform(-math.pi, math.pi, size=args.n2)
    w1 = rng.normal(0, 0.5, size=args.n1)
    w2 = rng.normal(0, 0.5, size=args.n2)

    t=0.0; steps=int(args.T/args.dt)
    print("t,R_all,R1,R2,phase_gap")
    for _ in range(steps):
        sigma_eff = args.sigma*math.exp(-args.rho)
        R1, psi1 = order_param(th1)
        R2, psi2 = order_param(th2)
        R_all, _ = order_param(np.concatenate([th1, th2]))
        # within-group Kuramoto (mean-field form) + cross attraction
        d1 = w1 + args.K_in*R1*np.sin(psi1 - th1) + args.K_cross*R2*np.sin(psi2 - th1)
        d2 = w2 + args.K_in*R2*np.sin(psi2 - th2) + args.K_cross*R1*np.sin(psi1 - th2)
        th1 = (th1 + args.dt*d1 + math.sqrt(args.dt)*rng.normal(0,sigma_eff, size=args.n1) + math.tau) % math.tau
        th2 = (th2 + args.dt*d2 + math.sqrt(args.dt)*rng.normal(0,sigma_eff, size=args.n2) + math.tau) % math.tau
        # phase difference of group means
        gap = (psi2 - psi1 + math.pi)%(2*math.pi) - math.pi
        print(f"{t:.3f},{R_all:.6f},{R1:.6f},{R2:.6f},{gap:.6f}")
        t += args.dt
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
