"""
examples/dual_phase_with_anchor.py
----------------------------------

Run the Dual-Phase simulation with a simple geomagnetic (Kp) driver
that nudges the OUTER coupling and an optional Schumann-like anchor.

Usage:
    python examples/dual_phase_with_anchor.py --steps 1500 --kp 4.2 --anchor
"""

import argparse
import numpy as np

try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None

# Core sim
from algorithms.field_equations import DualPhaseConfig, simulate_dual_phase

# Shared helpers (prefer centralized helpers to avoid drift)
try:
    from algorithms.utils import clamp
except Exception:
    def clamp(x, lo=0.0, hi=1.0):
        return max(lo, min(hi, x))


def kp_series(kp: float, steps: int, smooth: int = 50) -> np.ndarray:
    rng = np.random.default_rng(7)
    t = np.arange(steps)
    slow = 0.3 * np.sin(2 * np.pi * t / max(steps // 3, 1))
    noise = 0.15 * rng.normal(size=steps)
    raw = kp + slow + noise
    raw = np.clip(raw, 0.0, 9.0)
    k = max(1, smooth)
    kernel = np.ones(k) / k
    return np.convolve(raw, kernel, mode="same")


def kp_to_outer_coupling(kp_arr: np.ndarray, base_Koo: float = 0.65) -> np.ndarray:
    s = np.clip(kp_arr / 9.0, 0.0, 1.0)
    return base_Koo * (1.0 - 0.15 * s)


def run_dual_phase(steps: int = 1600, kp_center: float = 3.5, use_anchor: bool = True):
    kp_arr = kp_series(kp_center, steps=steps)
    Koo_arr = kp_to_outer_coupling(kp_arr, base_Koo=0.65)

    cfg = DualPhaseConfig(
        N_inner=96, N_outer=48,
        sigma_inner=0.6, sigma_outer=0.45,
        K_ii=1.1, K_oo=float(Koo_arr[0]),
        K_io=0.35, K_oi=0.15,
        use_anchor=use_anchor, anchor_strength=0.22,
        dt=0.05, steps=steps, seed=11
    )

    out = simulate_dual_phase(cfg)
    R_total = np.asarray(out["R_total"], dtype=float)
    R_inner = np.asarray(out["R_inner"], dtype=float)
    R_outer = np.asarray(out["R_outer"], dtype=float)

    Krel = Koo_arr / max(Koo_arr.max(), 1e-6)
    R_outer_mod = np.clip(R_outer * (0.9 + 0.1 * Krel), 0.0, 1.0)
    R_total_mod = np.clip(0.5 * (R_inner + R_outer_mod), 0.0, 1.0)

    return {
        "R_inner": R_inner,
        "R_outer": R_outer,
        "R_total": R_total,
        "R_total_mod": R_total_mod,
        "K_oo_series": Koo_arr,
        "kp_series": kp_arr,
        "use_anchor": use_anchor,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=1600)
    ap.add_argument("--kp", type=float, default=3.5)
    ap.add_argument("--anchor", action="store_true")
    args = ap.parse_args()

    res = run_dual_phase(steps=args.steps, kp_center=args.kp, use_anchor=args.anchor)

    print(f"R_inner(final)={res['R_inner'][-1]:.3f} | "
          f"R_outer(final)={res['R_outer'][-1]:.3f} | "
          f"R_total(final)={res['R_total'][-1]:.3f} | "
          f"R_total_mod(final)={res['R_total_mod'][-1]:.3f}")

    if plt is None:
        return

    import matplotlib.pyplot as plt
    t = np.arange(len(res["R_total"]))
    fig = plt.figure(figsize=(10, 7))

    ax1 = plt.subplot(3, 1, 1)
    ax1.plot(t, res["R_inner"], label="R_inner")
    ax1.plot(t, res["R_outer"], label="R_outer")
    ax1.plot(t, res["R_total"], label="R_total", linestyle="--")
    ax1.plot(t, res["R_total_mod"], label="R_total (K_oo mod viz)", linestyle=":")
    ax1.set_ylabel("R (coherence)")
    ax1.legend(loc="lower right")

    ax2 = plt.subplot(3, 1, 2)
    ax2.plot(t, res["K_oo_series"])
    ax2.set_ylabel("K_oo(t)")

    ax3 = plt.subplot(3, 1, 3)
    ax3.plot(t, res["kp_series"])
    ax3.set_ylabel("Kp(t)")
    ax3.set_xlabel("Step")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
