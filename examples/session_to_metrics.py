"""
examples/session_to_metrics.py
------------------------------

Convert a Resonant Reality-style session JSON (the Bridge Handshake input)
into Atlas metrics and recommendations. Optionally plot a simple R(t)
trajectory using the R_Growth differential form.

Usage:
    python examples/session_to_metrics.py --in rr_sample.json --out atlas_out.json --plot
"""

import json
import math
import argparse
from pathlib import Path

try:
    import matplotlib.pyplot as plt  # plotting is optional
except Exception:
    plt = None


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def signals_product(signals: dict) -> float:
    """Multiply known signals in [0,1]; if missing, treat as 0.7 (neutral)."""
    keys = ["I", "Ψ", "H", "S", "β", "π", "W"]
    prod = 1.0
    for k in keys:
        v = signals.get(k)
        if v is None:
            v = 0.7
        v = clamp(float(v))
        prod *= v
    return prod


def recommend_K_range(node_type: str, kp_index: float) -> list[float]:
    """
    Very simple heuristic for recommended coupling range [K_min, K_max]
    based on node type and geomagnetic activity (kp_index).
    """
    node_type = (node_type or "plaza").lower()
    # base ranges per node geometry
    base = {
        "plaza": (0.80, 1.20),
        "garden": (0.65, 1.00),
        "hearth": (0.55, 0.90),
        "wild": (0.70, 1.10),
    }.get(node_type, (0.70, 1.10))

    # adjust for geomagnetic turbulence: higher kp → tighten range slightly
    kmin, kmax = base
    kp = float(kp_index or 2.0)
    tighten = clamp((kp - 2.0) * 0.02, 0.0, 0.10)  # up to 0.10 tightening
    span = kmax - kmin
    kmin_adj = kmin + span * tighten * 0.5
    kmax_adj = kmax - span * tighten * 0.5
    return [round(kmin_adj, 2), round(kmax_adj, 2)]


def simple_resilience(pi: float, W: float, H: float) -> float:
    """
    Resilience score (0–1) using permeability, wonder, and humility.
    """
    pi = clamp(pi); W = clamp(W); H = clamp(H)
    # weighted mean emphasizing permeability
    return clamp(0.5 * pi + 0.3 * W + 0.2 * H)


def simulate_R_trajectory(prod: float, steps: int = 200, dt: float = 0.05,
                          alpha: float = 1.1, delta: float = 0.6, R0: float = 0.5):
    """
    Integrate dR/dt = alpha * prod - delta * R
    Saturates below 1.0; returns array of R(t).
    """
    R = R0
    hist = []
    for _ in range(steps):
        dR = alpha * prod - delta * R
        R = clamp(R + dt * dR)
        hist.append(R)
    return hist


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="infile", required=False, help="RR handshake JSON input")
    ap.add_argument("--out", dest="outfile", required=False, help="write Atlas output JSON")
    ap.add_argument("--plot", action="store_true", help="plot simple R(t) trajectory")
    args = ap.parse_args()

    # Example default input (if none provided)
    default_input = {
        "kp_index": 3.5,
        "schumann_amp": 7.8,
        "node_type": "plaza",
        "architecture": "open",
        "cosmic_timing": "solstice",
        "participants": 25,
        "signals": {"I": 0.8, "Ψ": 0.7, "H": 0.9, "S": 0.85, "β": 0.6, "π": 0.75, "W": 0.95}
    }

    if args.infile:
        data = json.loads(Path(args.infile).read_text())
    else:
        data = default_input

    signals = data.get("signals", {})
    prod = signals_product(signals)

    # Simple projected metrics
    # Interpret "gain" relative to a neutral baseline
    R_hist = simulate_R_trajectory(prod, steps=200, dt=0.05, alpha=1.1, delta=0.6, R0=0.5)
    R_gain = clamp(R_hist[-1] - R_hist[0])  # end - start as projected gain

    # RMSSD_gain: stub a proportional mapping from product
    RMSSD_gain = round(18.0 * prod, 2)  # ms

    # Resilience score
    res_score = round(simple_resilience(signals.get("π", 0.7),
                                        signals.get("W", 0.7),
                                        signals.get("H", 0.7)), 2)

    # Recommended coupling range
    K_range = recommend_K_range(data.get("node_type"), data.get("kp_index"))

    # Risk flags
    risk_flags = []
    if (data.get("kp_index", 2.0) or 0) >= 5.0:
        risk_flags.append("geomagnetic_high")
    if signals.get("π", 0.0) < 0.4:
        risk_flags.append("low_permeability")
    if signals.get("S", 0.0) < 0.4:
        risk_flags.append("sovereignty_risk")

    atlas_out = {
        "R_gain": round(R_gain, 3),
        "RMSSD_gain": RMSSD_gain,
        "resilience_score": res_score,
        "recommended_K": K_range,
        "risk_flags": risk_flags,
        "notes": "Hold near R≈0.99; prefer invitational cadence; tighten coupling if kp is high."
    }

    # Print to console
    print(json.dumps(atlas_out, indent=2))

    # Write to file if requested
    if args.outfile:
        Path(args.outfile).write_text(json.dumps(atlas_out, indent=2))

    # Optional plot
    if args.plot:
        if plt is None:
            print("\n[plot] matplotlib not available; skipping plot.")
        else:
            import matplotlib.pyplot as plt
            plt.figure()
            plt.plot(R_hist)
            plt.xlabel("Step")
            plt.ylabel("R (coherence)")
            plt.title("Projected R(t) from signals product")
            plt.tight_layout()
            plt.show()


if __name__ == "__main__":
    main()
