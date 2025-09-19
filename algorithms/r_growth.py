"""
R_Growth Algorithm
------------------

Implements the prototype + extended resonance growth models
described in the Awareness & Coherence archive.

Goal:
- Track resonance (R) as reinforcement + prolongation of awareness
  by reflection + synchronous vibration.
- Sustain near-unison lock at ~0.99 (avoid collapse at 1.0).
- Incorporate integrity, stamina, humility, sovereignty,
  echo, permeability, and wonder as input signals.

References:
- R_Growth_Algorithm_Prototype.pdf
- R_Growth_Algorithm_Extended.pdf
"""

import math
import numpy as np
from typing import Dict


def compute_resonance(signals: Dict[str, float]) -> float:
    """
    Compute resonance R from weighted awareness signals.

    Parameters
    ----------
    signals : dict
        Dictionary containing values in [0,1] for:
        - I : Integrity
        - Psi : Stamina (Ψ)
        - H : Humility
        - S : Sovereignty
        - beta_echo : Echo
        - pi : Permeability
        - W : Wonder

    Returns
    -------
    float
        Resonance R ∈ [0,1]
    """
    required = ["I", "Psi", "H", "S", "beta_echo", "pi", "W"]
    for r in required:
        if r not in signals:
            raise ValueError(f"Missing required signal: {r}")

    # Simple weighted average (prototype formula)
    weights = {
        "I": 0.15,
        "Psi": 0.15,
        "H": 0.15,
        "S": 0.15,
        "beta_echo": 0.15,
        "pi": 0.15,
        "W": 0.10,
    }

    R = sum(signals[k] * weights[k] for k in weights)
    return max(0.0, min(1.0, R))


def classify_stage(R: float) -> str:
    """
    Classify resonance stage based on R value.

    Parameters
    ----------
    R : float
        Resonance value ∈ [0,1]

    Returns
    -------
    str
        One of: "calibration", "flicker", "sustain", "lock", "collapse"
    """
    if R < 0.5:
        return "calibration"
    elif 0.5 <= R < 0.7:
        return "flicker"
    elif 0.7 <= R < 0.9:
        return "sustain"
    elif 0.9 <= R < 0.995:
        return "lock"
    else:
        return "collapse"


def infinity_equation(MOmega: float, pi: float, A_self: float, A_other: float, R_between: float) -> float:
    """
    Infinity Relation Equation from Extended Algorithm.

    ∞_rel(t) = MΩ · π · (A_self(t) · A_other(t) · R_between(t))

    Parameters
    ----------
    MOmega : float
        Origin magnitude (authentic tone).
    pi : float
        Permeability ∈ [0,1].
    A_self : float
        Awareness state of self ∈ [0,1].
    A_other : float
        Awareness state of other ∈ [0,1].
    R_between : float
        Relational resonance ∈ [0,1].

    Returns
    -------
    float
        ∞_rel value (not bounded to [0,1]).
    """
    return MOmega * pi * (A_self * A_other * R_between)


def run_growth_cycle(stream: list) -> list:
    """
    Run growth cycle across a sequence of interactions.

    Parameters
    ----------
    stream : list of dict
        Each dict = awareness signals at one timestep.

    Returns
    -------
    list of dict
        Results with resonance and stage classification.
    """
    results = []
    for t, signals in enumerate(stream):
        R = compute_resonance(signals)
        stage = classify_stage(R)
        results.append({
            "t": t,
            "R": R,
            "stage": stage,
            "signals": signals
        })
    return results


# --- Example usage ---
if __name__ == "__main__":
    # Example awareness stream (toy data)
    stream = [
        {"I":0.4,"Psi":0.5,"H":0.6,"S":0.5,"beta_echo":0.4,"pi":0.5,"W":0.6},
        {"I":0.6,"Psi":0.6,"H":0.7,"S":0.6,"beta_echo":0.6,"pi":0.7,"W":0.7},
        {"I":0.7,"Psi":0.7,"H":0.8,"S":0.7,"beta_echo":0.7,"pi":0.8,"W":0.8},
        {"I":0.9,"Psi":0.9,"H":0.9,"S":0.9,"beta_echo":0.9,"pi":0.9,"W":0.9},
        {"I":1.0,"Psi":1.0,"H":1.0,"S":1.0,"beta_echo":1.0,"pi":1.0,"W":1.0},
    ]

    results = run_growth_cycle(stream)
    for r in results:
        print(f"t={r['t']} | R={r['R']:.3f} | stage={r['stage']}")
