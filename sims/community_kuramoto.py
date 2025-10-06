# File: sims/community_kuramoto.py
#!/usr/bin/env python3
from __future__ import annotations
import argparse, math
from dataclasses import dataclass
import numpy as np

@dataclass
class Params:
    n: int = 256
    K: float = 1.2
    rho: float = 0.6          # observation rate (lowers effective noise)
    lam0: float = 0.20        # initial ethics weight
    R_star: float = 0.75      # target coherence
    eta: float = 0.02         # adaptation rate dλ/dt
    sigma: float = 0.45       # base noise
    dt: float = 0.02
    T: float = 40.0
    seed: int = 1
    graph: str = "ring"       # ring|all|smallworld
    shock_t: float = 20.0
    shock_sigma: float = 1.2

def build_graph(n, kind="ring"):
    if kind == "all":
        A = np.ones((n,n)) - np.eye(n)
    elif kind == "smallworld":
        k = max(2, n//20)
        A = np.zeros((n,n))
        for i in range(n):
            for d in range(1,k+1):
                A[i,(i+d)%n]=1; A[i,(i-d)%n]=1
        rng = np.random.default_rng(42)
        for i in range(n):
            if rng.random() < 0.03:
                j = rng.integers(0,n); A[i,:]=0; A[i,j]=1
        A = np.maximum(A, A.T); np.fill_diagonal(A,0)
    else:
        A = np.zeros((n,n))
        for i in range(n):
            A[i,(i-1)%n]=1; A[i,(i+1)%n]=1
    deg = A.sum(axis=1, keepdims=True); deg[deg==0]=1
    return A/deg

def order_parameter(theta):
    return abs(np.exp(1j*theta).mean())

def main(argv=None):
    ap = argparse.ArgumentParser()
    for field, typ in Params.__annotations__.items():
        default = getattr(Params, field)
        ap.add_argument(f"--{field}", type=typ if typ!=bool else None, default=default)
    args = ap.parse_args(argv)
    p = Params(**{k: getattr(args,k) for k in Params.__annotations__})

    rng = np.random.default_rng(p.seed)
    A = build_graph(p.n, p.graph)
    theta = rng.uniform(-math.pi, math.pi, size=p.n)
    omega = rng.normal(0, 0.5, size=p.n)
    lam = p.lam0
    alpha = 0.98; m = 0.0

    steps = int(p.T/p.dt); t=0.0
    print("t,R,m,lam")
    for _ in range(steps):
        sigma_eff = p.sigma*math.exp(-p.rho)
        shock = (p.shock_sigma if abs(t-p.shock_t) < p.dt*1.5 else 0.0)
        sin_diff = np.sin(theta[np.newaxis,:]-theta[:,np.newaxis])
        coupling = p.K*(A*sin_diff).sum(axis=1)
        ethics_grad = (A*np.sin(theta[:,None]-theta[None,:])).sum(axis=1)
        dtheta = omega + coupling - lam*ethics_grad
        noise = rng.normal(0, sigma_eff+shock, size=p.n)
        theta = (theta + p.dt*dtheta + math.sqrt(p.dt)*noise + math.tau) % math.tau

        R = order_parameter(theta)
        m = alpha*m + (1-alpha)*R
        # ethics adaptation: push lam toward value that yields R≈R*
        lam += p.eta * (p.R_star - R)
        lam = max(0.0, min(2.0, lam))
        print(f"{t:.3f},{R:.6f},{m:.6f},{lam:.6f}")
        t += p.dt
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
