# File: sims/kuramoto_schumann_hybrid.py
#!/usr/bin/env python3
from __future__ import annotations
import argparse, math
import numpy as np

def schumann_forcing(t, f0=7.83, amp=0.25, duty=0.6):
    # square-envelope sinusoid: active for a duty fraction each second
    gate = 1.0 if (t%1.0) < duty else 0.0
    return amp * gate * math.sin(2*math.pi*f0*t)

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=256)
    ap.add_argument("--K", type=float, default=1.1)
    ap.add_argument("--rho", type=float, default=0.5)
    ap.add_argument("--sigma", type=float, default=0.45)
    ap.add_argument("--f0", type=float, default=7.83)
    ap.add_argument("--amp", type=float, default=0.25)
    ap.add_argument("--duty", type=float, default=0.6)
    ap.add_argument("--dt", type=float, default=0.002)
    ap.add_argument("--T", type=float, default=20.0)
    ap.add_argument("--seed", type=int, default=2)
    args = ap.parse_args(argv)

    rng = np.random.default_rng(args.seed)
    theta = rng.uniform(-math.pi, math.pi, size=args.n)
    omega = rng.normal(0, 0.5, size=args.n)
    t=0.0; steps=int(args.T/args.dt)
    print("t,R,F")
    for _ in range(steps):
        sigma_eff = args.sigma*math.exp(-args.rho)
        F = schumann_forcing(t, args.f0, args.amp, args.duty)
        # all-to-all Kuramoto + global forcing injected as phase bias
        z = np.exp(1j*theta).mean()
        R, psi = abs(z), math.atan2(z.imag, z.real)
        dtheta = omega + args.K*R*np.sin(psi - theta) + F
        noise = rng.normal(0, sigma_eff, size=args.n)
        theta = (theta + args.dt*dtheta + math.sqrt(args.dt)*noise + math.tau) % math.tau
        print(f"{t:.3f},{R:.6f},{F:.6f}")
        t += args.dt
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
