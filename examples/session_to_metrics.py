"""
Example: Convert a Resonant Reality session (JSON) into Atlas metrics
and visualize the results.

Usage:
    python examples/session_to_metrics.py --in examples/rr_sample.json --plot
"""

import json
import argparse
import matplotlib.pyplot as plt
from pathlib import Path

# import shared helpers from algorithms
from algorithms.utils import signals_product, recommend_K_range


def compute_metrics(session: dict) -> dict:
    """
    Compute resonance metrics from a session.
    """
    signals = session.get("signals", {})
    R_total = signals_product(signals)
    K_low, K_high = recommend_K_range(R_total)

    return {
        "R_total": R_total,
        "K_range": (K_low, K_high),
        "participants": session.get("participants", 0),
        "node_type": session.get("node_type", "unknown"),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="infile", required=True,
                        help="Path to session JSON file")
    parser.add_argument("--plot", action="store_true",
                        help="Plot results")
    args = parser.parse_args()

    session = json.loads(Path(args.infile).read_text())
    metrics = compute_metrics(session)

    print("=== Metrics ===")
    for k, v in metrics.items():
        print(f"{k}: {v}")

    if args.plot:
        plt.bar(["R_total"], [metrics["R_total"]])
        plt.ylim(0, 1)
        plt.title("Resonance Metric (R)")
        plt.show()


if __name__ == "__main__":
    main()
