Dual-Phase Field dynamics + Soul-in-Field signature.

This module implements two families of equations referenced across the
Field Applications papers:

1) Dual-Phase Field Equation
   - Inner phase (Φ_I): the "within" (e.g., a group of humans).
   - Outer phase (Φ_O): the "without" (e.g., place/planetary anchor/civic grid).
   - Coherence emerges when Φ_I is aligned (inner coupling)
     and Φ_O is properly tuned (outer/anchor coupling).
   - We model both as coupled Kuramoto-style oscillators with a simple driver
     option for a Schumann-like anchor on the outer layer.

2) Soul-in-Field Equation
   - Person-level resonance signature using origin magnitude (MΩ),
     memory echo (β), permeability (π), wonder (W), and awareness signals:
     Integrity (I), Stamina/Presence (Ψ), Humility (H), Sovereignty (S).
   - Choice is modeled as a (soft) collapse from a distribution of options.

Both sets of functions are designed to be lightweight and directly usable in
notebooks, scripts, or higher-level pipelines.

References (source archive):
- Dual_Phase_Field_Equation.pdf
- Soul_in_Field_Equation.pdf
- Soul_and_Resonance.pdf
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Dict, Optional
import numpy as np


# ---------------------------------------------------------------------
# Utility: Order parameter (Kuramoto)
# ---------------------------------------------------------------------

def order_parameter(theta: np.ndarray) -> Tuple[float, float]:
    """
    Compute Kuramoto order parameter for a set of phases.

    Parameters
    ----------
    theta : np.ndarray
        Array of phases (radians), shape (N,).

    Returns
    -------
    (R, psi) : (float, float)
        R ∈ [0,1] coherence magnitude; psi = mean phase (radians).
    """
    z = np.exp(1j * theta).mean()
    R = np.abs(z)
    psi = np.angle(z)
    return float(R), float(psi)


# ---------------------------------------------------------------------
# Dual-Phase Field: dynamics & simulation
# ---------------------------------------------------------------------

@dataclass
class DualPhaseConfig:
    # Inner (group) layer
    N_inner: int = 64
    sigma_inner: float = 0.6      # freq spread
    K_ii: float = 1.0             # inner↔inner coupling

    # Outer (environment) layer
    N_outer: int = 32
    sigma_outer: float = 0.4
    K_oo: float = 0.5             # outer↔outer coupling

    # Cross-layer coupling
    K_io: float = 0.3             # inner influenced by outer
    K_oi: float = 0.15            # outer influenced by inner (often smaller)

    # Anchor on outer layer (e.g., Schumann 7.83 Hz proxy)
    use_anchor: bool = True
    anchor_strength: float = 0.20 # K_e: outer pulled by anchor
    anchor_phase_speed: float = 0.0  # dφ/dt for anchor (0 = fixed phase)
    anchor_phase_init: float = 0.0   # initial anchor phase

    # Integration
    dt: float = 0.05
    steps: int = 2000
    seed: Optional[int] = 7


def _coupling_term(theta: np.ndarray, K: float) -> np.ndarray:
    """
    All-to-all coupling term Σ sin(θ_j − θ_i) (vectorized).

    Returns
    -------
    np.ndarray of shape (N,)
    """
    # Compute pairwise sin differences efficiently
    # sin(θj - θi) = Im{exp(i(θj - θi))}
    ej = np.exp(1j * theta)
    mean_field = ej.mean()
    # Using mean-field identity: Σ_j sin(θ_j - θ_i) = N * R * sin(ψ - θ_i)
    R = np.abs(mean_field)
    psi = np.angle(mean_field)
    return K * R * np.sin(psi - theta)


def simulate_dual_phase(cfg: DualPhaseConfig) -> Dict[str, np.ndarray]:
    """
    Simulate two coupled oscillator populations (inner & outer) with optional
    external anchor on the outer layer.

    Dynamics (per oscillator i):
      dθ_i^I/dt = ω_i^I + K_ii * Σ_I sin(θ_j^I − θ_i^I)
                           + K_io * sin(ψ_O − θ_i^I)
      dθ_k^O/dt = ω_k^O + K_oo * Σ_O sin(θ_m^O − θ_k^O)
                           + K_oi * sin(ψ_I − θ_k^O)
                           + K_e  * sin(φ_anchor − θ_k^O)   (optional)

    Mean phases ψ_I, ψ_O are from each population’s order parameter.

    Returns
    -------
    dict with keys:
      'theta_inner', 'theta_outer' : final phases (arrays)
      'R_inner', 'R_outer', 'R_total' : coherence time series (arrays) length = steps
      'psi_inner', 'psi_outer' : mean phase time series (arrays)
    """
    if cfg.seed is not None:
        rng = np.random.default_rng(cfg.seed)
    else:
        rng = np.random.default_rng()

    # Natural frequencies (Gaussian around 0)
    omega_i = rng.normal(0.0, cfg.sigma_inner, size=cfg.N_inner)
    omega_o = rng.normal(0.0, cfg.sigma_outer, size=cfg.N_outer)

    # Initial phases uniform [0, 2π)
    theta_i = rng.uniform(0, 2*np.pi, size=cfg.N_inner)
    theta_o = rng.uniform(0, 2*np.pi, size=cfg.N_outer)

    # Anchor phase
    phi_anchor = cfg.anchor_phase_init

    R_inner = np.zeros(cfg.steps)
    R_outer = np.zeros(cfg.steps)
    R_total = np.zeros(cfg.steps)
    psi_inner = np.zeros(cfg.steps)
    psi_outer = np.zeros(cfg.steps)

    for t in range(cfg.steps):
        # Order parameters for each layer
        Ri, psiI = order_parameter(theta_i)
        Ro, psiO = order_parameter(theta_o)
        Rt, _ = order_parameter(np.concatenate([theta_i, theta_o]))

        R_inner[t], R_outer[t], R_total[t] = Ri, Ro, Rt
        psi_inner[t], psi_outer[t] = psiI, psiO

        # Mean-field coupling terms
        coup_ii = _coupling_term(theta_i, cfg.K_ii)
        coup_oo = _coupling_term(theta_o, cfg.K_oo)

        # Cross-layer influence via mean phase difference
        cross_io = cfg.K_io * np.sin(psiO - theta_i)
        cross_oi = cfg.K_oi * np.sin(psiI - theta_o)

        # Anchor pulls the OUTER layer, if enabled
        if cfg.use_anchor:
            anchor_term = cfg.anchor_strength * np.sin(phi_anchor - theta_o)
        else:
            anchor_term = 0.0

        # Euler update
        dtheta_i = omega_i + coup_ii + cross_io
        dtheta_o = omega_o + coup_oo + cross_oi + anchor_term

        theta_i = (theta_i + cfg.dt * dtheta_i) % (2*np.pi)
        theta_o = (theta_o + cfg.dt * dtheta_o) % (2*np.pi)

        # Advance anchor phase (optional)
        phi_anchor = (phi_anchor + cfg.dt * cfg.anchor_phase_speed) % (2*np.pi)

    return {
        "theta_inner": theta_i,
        "theta_outer": theta_o,
        "R_inner": R_inner,
        "R_outer": R_outer,
        "R_total": R_total,
        "psi_inner": psi_inner,
        "psi_outer": psi_outer,
    }


# ---------------------------------------------------------------------
# Soul-in-Field: signature, resonance, and choice collapse
# ---------------------------------------------------------------------

@dataclass
class SoulSignature:
    """Container for person-level resonance parameters."""
    MOmega: float           # origin magnitude (authentic tone), >0
    beta_echo: float        # memory echo β ∈ [0,1]
    pi: float               # permeability π ∈ [0,1]
    W: float                # wonder W ∈ [0,1]
    I: float                # integrity ∈ [0,1]
    Psi: float              # stamina/presence ∈ [0,1]
    H: float                # humility ∈ [0,1]
    S: float                # sovereignty ∈ [0,1]


def soul_resonance(sig: SoulSignature,
                   R_between: float) -> float:
    """
    Compute person–in–field resonance readout.

    From the archive’s Infinity Relation backbone:
      ∞_rel = MΩ · π · (A_self · A_other · R_between)

    Here we let:
      A_self  = geometric mean of (I, Ψ, H, S, W, β)
      A_other = 1.0  (can be folded in via R_between when modeling pairs/groups)

    Parameters
    ----------
    sig : SoulSignature
    R_between : float
        Relational coherence with others ∈ [0,1].

    Returns
    -------
    float
        Resonance "power" (unnormalized).
    """
    # clamp helpers
    def c(x): return float(max(0.0, min(1.0, x)))

    vals = np.array([c(sig.I), c(sig.Psi), c(sig.H), c(sig.S), c(sig.W), c(sig.beta_echo)])
    # geometric mean for multiplicative synergy (0 values mute the chord)
    A_self = float(np.prod(vals) ** (1.0 / len(vals)))
    out = sig.MOmega * c(sig.pi) * (A_self * c(R_between))
    return out


def hold_near(value: float, target: float = 0.99, k: float = 0.3) -> float:
    """
    Pull a value softly toward a target (used to avoid hard closure at 1.0).

    value_next = value + k * (target - value)
    """
    return value + k * (target - value)


def softmax_choice(utilities: np.ndarray,
                   temperature: float = 1.0,
                   bias: Optional[np.ndarray] = None,
                   rng: Optional[np.random.Generator] = None) -> int:
    """
    Choice collapse as softmax (stochastic) selection.

    Parameters
    ----------
    utilities : np.ndarray
        Scores for each option.
    temperature : float
        Lower → sharper (argmax-like). Higher → flatter.
    bias : Optional[np.ndarray]
        Optional additive bias per option (same shape as utilities).
    rng : np.random.Generator
        Optional RNG; if None, a default generator is used.

    Returns
    -------
    int
        Index of chosen option.
    """
    if rng is None:
        rng = np.random.default_rng()

    u = np.array(utilities, dtype=float)
    if bias is not None:
        u = u + np.array(bias, dtype=float)

    # avoid overflow; stable softmax
    u = u / max(1e-9, temperature)
    u = u - u.max()
    p = np.exp(u)
    p = p / p.sum()
    return int(rng.choice(len(u), p=p))


# ---------------------------------------------------------------------
# Demo / self-test
# ---------------------------------------------------------------------

if __name__ == "__main__":
    # --- 1) Dual-Phase quick demo ---
    cfg = DualPhaseConfig(
        N_inner=80, N_outer=40,
        K_ii=1.2, K_oo=0.6,
        K_io=0.35, K_oi=0.12,
        use_anchor=True, anchor_strength=0.22,
        steps=1200, dt=0.05, seed=42
    )
    res = simulate_dual_phase(cfg)
    print(f"[DualPhase] R_inner(final)={res['R_inner'][-1]:.3f} | "
          f"R_outer(final)={res['R_outer'][-1]:.3f} | "
          f"R_total(final)={res['R_total'][-1]:.3f}")

    # --- 2) Soul-in-Field quick demo ---
    sig = SoulSignature(
        MOmega=1.4, beta_echo=0.78, pi=0.72, W=0.76,
        I=0.82, Psi=0.75, H=0.70, S=0.86
    )
    rel = 0.68
    power = soul_resonance(sig, rel)
    print(f"[Soul] ∞_rel={power:.3f} (before hold)")
    print(f"[Soul] held→ {hold_near(power, target=0.99):.3f}")

    # --- 3) Choice collapse demo ---
    utilities = np.array([0.2, 0.6, 0.55])
    choice = softmax_choice(utilities, temperature=0.5)
    print(f"[Choice] picked option index: {choice}")
