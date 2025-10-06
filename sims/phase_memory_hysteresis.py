# File: sims/phase_memory_hysteresis.py
#!/usr/bin/env python3
from __future__ import annotations
import argparse, math
import numpy as np

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=240)
    ap.add_argument("--K", type=float, default=1.1)
    ap.add_argument("--rho", type=float, default=0.5)
    ap.add_argument("--sigma", type=float, default=0.5)
    ap.add_argument("--alpha", type=float, default=0.985)  # memory decay
    ap.add_argument("--boost", type=float, default=0.35)   # memory → coupling gain
    ap.add_argument("--cycles", type=int, default=3)       # on/off cycles
    ap.add_argument("--Ton", type=float, default=12.0)
    ap.add_argument("--Toff", type=float, default=10.0)
    ap.add_argument("--dt", type=float, default=0.02)
    ap.add_argument("--seed", type=int, default=4)
    args = ap.parse_args(argv)

    rng = np.random.default_rng(args.seed)
    theta = rng.uniform(-math.pi, math.pi, size=args.n)
    omega = rng.normal(0, 0.5, size=args.n)
    m = 0.0
    print("t,R,m,K_eff,phase")
    t=0.0
    for cyc in range(args.cycles):
        # ON: learn
        steps_on = int(args.Ton/args.dt)
        for _ in range(steps_on):
            K_eff = args.K + args.boost*m
            z = np.exp(1j*theta).mean()
            R = abs(z); psi = math.atan2(z.imag, z.real)
            dtheta = omega + K_eff*R*np.sin(psi - theta)
            noise = rng.normal(0, args.sigma*math.exp(-args.rho), size=args.n)
            theta = (theta + args.dt*dtheta + math.sqrt(args.dt)*noise + math.tau) % math.tau
            m = args.alpha*m + (1-args.alpha)*R
            print(f"{t:.3f},{R:.6f},{m:.6f},{K_eff:.6f},on")
            t += args.dt
        # OFF: forget
        steps_off = int(args.Toff/args.dt)
        for _ in range(steps_off):
            z = np.exp(1j*theta).mean()
            R = abs(z); psi = math.atan2(z.imag, z.real)
            dtheta = omega + 0.0*R*np.sin(psi - theta)  # remove coupling
            noise = rng.normal(0, args.sigma, size=args.n)
            theta = (theta + args.dt*dtheta + math.sqrt(args.dt)*noise + math.tau) % math.tau
            m = args.alpha*m  # decay only
            print(f"{t:.3f},{R:.6f},{m:.6f},0.0,off")
            t += args.dt
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
