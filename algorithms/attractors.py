"""
algorithms/attractors.py

Attractor models and bifurcation utilities for The Atlas Model.

Implements:
  • Discrete maps: logistic, circle map (phase map), Henon (optional)
  • Continuous flows: Lorenz63, Rossler
  • Integrators: Euler, RK4
  • Bifurcation scan helpers (parameter sweeps)
  • Utilities to convert 1D maps → phase signals (for resonance coupling)

NumPy-only; no plotting.

License: MIT
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Tuple, Dict, Any, Optional
import numpy as np


# ──────────────────────────────────────────────────────────────────────────────
# Integrators
# ──────────────────────────────────────────────────────────────────────────────

def euler(f: Callable[[float, np.ndarray, Dict[str, Any]], np.ndarray],
          t: float, x: np.ndarray, dt: float, params: Dict[str, Any]) -> np.ndarray:
    return x + dt * f(t, x, params)

def rk4(f: Callable[[float, np.ndarray, Dict[str, Any]], np.ndarray],
        t: float, x: np.ndarray, dt: float, params: Dict[str, Any]) -> np.ndarray:
    k1 = f(t, x, params)
    k2 = f(t + 0.5*dt, x + 0.5*dt*k1, params)
    k3 = f(t + 0.5*dt, x + 0.5*dt*k2, params)
    k4 = f(t + dt, x + dt*k3, params)
    return x + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)


# ──────────────────────────────────────────────────────────────────────────────
# Discrete maps
# ──────────────────────────────────────────────────────────────────────────────

def logistic_map(x: float, r: float) -> float:
    """
    Logistic map: x_{n+1} = r x_n (1 - x_n), x ∈ (0,1), r ∈ (0,4].
    """
    xn = r * x * (1.0 - x)
    # confine numerically
    if np.isnan(xn) or np.isinf(xn):
        xn = 0.5
    return float(np.clip(xn, 0.0, 1.0))

def circle_map(theta: float, K: float, Omega: float) -> float:
    """
    Circle map (standard map variant, phase map):
      θ_{n+1} = θ_n + Ω - (K / (2π)) sin(2π θ_n)   (mod 1)
    Returns wrapped to [0,1).
    """
    next_theta = theta + Omega - (K/(2.0*np.pi)) * np.sin(2.0*np.pi*theta)
    return float(np.mod(next_theta, 1.0))

def henon_map(x: float, y: float, a: float = 1.4, b: float = 0.3) -> Tuple[float, float]:
    """
    Hénon map:
      x' = 1 - a x^2 + y
      y' = b x
    """
    x_next = 1.0 - a * (x**2) + y
    y_next = b * x
    return float(x_next), float(y_next)


# ──────────────────────────────────────────────────────────────────────────────
# Continuous flows
# ──────────────────────────────────────────────────────────────────────────────

def lorenz63(t: float, xyz: np.ndarray, p: Dict[str, Any]) -> np.ndarray:
    """
    Lorenz 1963:
      x' = σ(y - x)
      y' = x(ρ - z) - y
      z' = xy - βz
    """
    sigma = p.get("sigma", 10.0)
    rho   = p.get("rho", 28.0)
    beta  = p.get("beta", 8.0/3.0)
    x, y, z = xyz
    return np.array([sigma*(y - x), x*(rho - z) - y, x*y - beta*z], dtype=float)

def rossler(t: float, xyz: np.ndarray, p: Dict[str, Any]) -> np.ndarray:
    """
    Rössler:
      x' = -(y + z)
      y' = x + a y
      z' = b + z(x - c)
    """
    a = p.get("a", 0.2)
    b = p.get("b", 0.2)
    c = p.get("c", 5.7)
    x, y, z = xyz
    return np.array([-(y + z), x + a*y, b + z*(x - c)], dtype=float)


# ──────────────────────────────────────────────────────────────────────────────
# Time series generators
# ──────────────────────────────────────────────────────────────────────────────

def run_map(f: Callable, x0: np.ndarray, steps: int, burn: int = 100, **kwargs) -> np.ndarray:
    """
    Iterate a discrete map f for 'steps' after 'burn' warmup.
    x0 can be scalar or tuple → returns array of shape (steps, D)
    """
    # handle scalar or tuple initial conditions
    if isinstance(x0, tuple):
        state = list(map(float, x0))
    else:
        state = [float(x0)]
    D = len(state)
    for _ in range(max(burn, 0)):
        if D == 1:
            state[0] = f(state[0], **kwargs)
        elif D == 2:
            state[0], state[1] = f(state[0], state[1], **kwargs)
        else:
            raise ValueError("Only 1D or 2D maps supported in run_map.")
    out = np.zeros((steps, D), dtype=float)
    for t in range(steps):
        if D == 1:
            state[0] = f(state[0], **kwargs)
        else:
            state[0], state[1] = f(state[0], state[1], **kwargs)
        out[t] = state
    return out.squeeze()

def run_flow(f: Callable, x0: np.ndarray, dt: float, steps: int,
             method: str = "rk4", params: Optional[Dict[str, Any]] = None) -> np.ndarray:
    """
    Integrate a continuous flow with Euler or RK4.
    Returns array shape (steps+1, D), including initial state.
    """
    params = params or {}
    integ = rk4 if method.lower() == "rk4" else euler
    x = np.array(x0, dtype=float)
    D = x.size
    out = np.zeros((steps + 1, D), dtype=float)
    t = 0.0
    out[0] = x
    for k in range(1, steps + 1):
        x = integ(f, t, x, dt, params)
        out[k] = x
        t += dt
    return out


# ──────────────────────────────────────────────────────────────────────────────
# Bifurcation scans (parameter sweeps)
# ──────────────────────────────────────────────────────────────────────────────

def logistic_bifurcation(r_min: float = 2.5, r_max: float = 4.0, r_steps: int = 400,
                         burn: int = 400, sample: int = 100, x0: float = 0.5) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute logistic map bifurcation points:
      For each r, iterate burn steps, then record 'sample' points.
    Returns (R, X) with shapes (r_steps*sample,), (r_steps*sample,)
    """
    rs = np.linspace(r_min, r_max, r_steps)
    R = []
    X = []
    for r in rs:
        x = float(x0)
        for _ in range(burn):
            x = logistic_map(x, r)
        for _ in range(sample):
            x = logistic_map(x, r)
            R.append(r)
            X.append(x)
    return np.array(R, dtype=float), np.array(X, dtype=float)

def circle_map_rotation_number(K: float, Omega: float, steps: int = 4096, burn: int = 1024,
                               theta0: float = 0.12345) -> float:
    """
    Compute rotation number ρ ≈ lim (θ_N - θ_0)/N for the circle map.
    """
    theta = float(theta0)
    for _ in range(burn):
        theta = circle_map(theta, K=K, Omega=Omega)
    theta_start = theta
    for _ in range(steps):
        theta = circle_map(theta, K=K, Omega=Omega)
    return float((theta - theta_start) % 1.0)  # wrapped per step; indicative


# ──────────────────────────────────────────────────────────────────────────────
# Map → phase signal (for coupling to resonance sims)
# ──────────────────────────────────────────────────────────────────────────────

def map_to_phase(series: np.ndarray, center: float = 0.5, width: float = 0.5) -> np.ndarray:
    """
    Convert a real sequence to a phase signal in [0, 2π) by a smooth wrapping:
      φ = 2π * sigmoid((x - center)/width)
    Useful to inject chaotic/periodic maps as phase drivers.
    """
    x = np.asarray(series, dtype=float).ravel()
    s = 1.0 / (1.0 + np.exp(-(x - center)/max(width, 1e-6)))
    return (2.0 * np.pi * s) % (2.0 * np.pi)


# ──────────────────────────────────────────────────────────────────────────────
# Convenience presets
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class LorenzPreset:
    sigma: float = 10.0
    rho: float = 28.0
    beta: float = 8.0/3.0
    dt: float = 0.01
    steps: int = 10000
    x0: Tuple[float, float, float] = (1.0, 1.0, 1.0)

def run_lorenz(p: LorenzPreset = LorenzPreset()) -> np.ndarray:
    return run_flow(lorenz63, np.array(p.x0), dt=p.dt, steps=p.steps,
                    method="rk4", params={"sigma": p.sigma, "rho": p.rho, "beta": p.beta})

@dataclass
class RosslerPreset:
    a: float = 0.2
    b: float = 0.2
    c: float = 5.7
    dt: float = 0.02
    steps: int = 15000
    x0: Tuple[float, float, float] = (0.1, 0.0, 0.0)

def run_rossler(p: RosslerPreset = RosslerPreset()) -> np.ndarray:
    return run_flow(rossler, np.array(p.x0), dt=p.dt, steps=p.steps,
                    method="rk4", params={"a": p.a, "b": p.b, "c": p.c})


# ──────────────────────────────────────────────────────────────────────────────
# __all__
# ──────────────────────────────────────────────────────────────────────────────

__all__ = [
    # integrators
    "euler", "rk4",
    # maps
    "logistic_map", "circle_map", "henon_map", "run_map",
    # flows
    "lorenz63", "rossler", "run_flow",
    # presets
    "LorenzPreset", "run_lorenz", "RosslerPreset", "run_rossler",
    # bifurcations
    "logistic_bifurcation", "circle_map_rotation_number",
    # utilities
    "map_to_phase",
]
