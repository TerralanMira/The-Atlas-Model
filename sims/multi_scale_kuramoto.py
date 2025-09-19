"""
multi_scale_kuramoto.py
-----------------------

Two-layer (inner/outer) Kuramoto simulation that mirrors the
Dual-Phase Field model, importing the engine from algorithms/field_equations.py.

Dependencies: numpy, (optional) matplotlib

Run:
    python sims/multi_scale_kuramoto.py
"""

import numpy as np

try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None

from algorithms.field_equations import DualPhaseConfig, simulate_dual_phase


def main():
    cfg = DualPhaseConfig(
        N_inner=96, N_outer=48,
        sigma_inner=0.6, sigma_outer=0.45,
        K_ii=1.1, K_oo=0.65,
        K_io=0.35, K_oi=0.15,
        use_anchor=True, anchor_strength=0.22,
        dt=0.05, steps=1600, seed=11
    )
    res = simulate_dual_phase(cfg)

    print(f"R_inner(final)={res['R_inner'][-1]:.3f} | "
          f"R_outer(final)={res['R_outer'][-1]:.3f} | "
          f"R_total(final)={res['R_total'][-1]:.3f}")

    if plt is None:
        return

    import matplotlib.pyplot as plt
    t = np.arange(len(res["R_total"]))
    plt.figure()
    plt.plot(t, res["R_inner"], label="R_inner")
    plt.plot(t, res["R_outer"], label="R_outer")
    plt.plot(t, res["R_total"], label="R_total", linestyle="--")
    plt.xlabel("Step")
    plt.ylabel("R (coherence)")
    plt.legend()
    plt.title("Multi-Scale Kuramoto (Dual-Phase)")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
