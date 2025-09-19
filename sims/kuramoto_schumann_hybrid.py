"""
kuramoto_schumann_hybrid.py
---------------------------

Single-population Kuramoto oscillators with an optional
Schumann-like external anchor (7.83 Hz proxy as a fixed phase driver).

Dependencies: numpy, matplotlib (optional for plotting)

Run:
    python sims/kuramoto_schumann_hybrid.py
"""

import numpy as np

try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None


def order_parameter(theta):
    z = np.exp(1j * theta).mean()
    return float(np.abs(z)), float(np.angle(z))


def simulate(
    N=120,
    sigma=0.6,       # natural frequency spread
    K=0.8,           # all-to-all coupling
    use_anchor=True,
    K_e=0.20,        # anchor coupling strength
    phi_anchor=0.0,  # anchor phase (radians)
    dphi_anchor=0.0, # anchor phase speed (0 = fixed)
    dt=0.05,
    steps=2000,
    seed=7
):
    rng = np.random.default_rng(seed)
    omega = rng.normal(0.0, sigma, size=N)
    theta = rng.uniform(0, 2*np.pi, size=N)

    R_hist = np.zeros(steps, dtype=float)

    for t in range(steps):
        # mean field
        z = np.exp(1j * theta).mean()
        R = np.abs(z)
        psi = np.angle(z)
        R_hist[t] = R

        # Kuramoto mean-field identity: K * R * sin(psi - theta)
        coupling_term = K * R * np.sin(psi - theta)

        # Anchor driver (fixed or slowly moving phase)
        anchor_term = K_e * np.sin(phi_anchor - theta) if use_anchor else 0.0

        dtheta = omega + coupling_term + anchor_term
        theta = (theta + dt * dtheta) % (2*np.pi)

        phi_anchor = (phi_anchor + dt * dphi_anchor) % (2*np.pi)

    return {"R": R_hist, "theta": theta}


def main():
    out_off = simulate(use_anchor=False)
    out_on = simulate(use_anchor=True, K_e=0.2)

    if plt is None:
        for label, arr in [("no_anchor", out_off["R"]), ("anchor", out_on["R"])]:
            print(label, f"R_final={arr[-1]:.3f}")
        return

    import matplotlib.pyplot as plt
    plt.figure()
    plt.plot(out_off["R"], label="No anchor")
    plt.plot(out_on["R"], label="Anchor on (K_e=0.2)", alpha=0.9)
    plt.xlabel("Step")
    plt.ylabel("R (coherence)")
    plt.legend()
    plt.title("Kuramoto × Schumann (anchor) hybrid")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
