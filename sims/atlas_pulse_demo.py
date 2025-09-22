#!/usr/bin/env python3
"""
Atlas Pulse Demo

Runs the orchestration pulse for a short series and saves lightweight artifacts
that dashboards or notebooks can ingest.

Outputs:
  - atlas_pulse_series.csv   (step, atlas_coherence)
  - atlas_pulse_layers.json  ({step: {layer: metrics, ...}, ...})
  - atlas_pulse_summary.txt  (mean/std, availability by layer)
  - (optional) atlas_pulse_series.png if matplotlib is present

Usage:
  python sims/atlas_pulse_demo.py --steps 30 --seed 7 --out logs/atlas_pulse
"""

import argparse
import json
import os
from typing import Dict, Any

import numpy as np

try:
    from algorithms.atlas_orchestrator import AtlasConfig, run_once
except Exception as e:
    raise SystemExit(
        "Import error: ensure algorithms/atlas_orchestrator.py exists and is importable.\n"
        f"{e}"
    )

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def maybe_plot(xs, ys, out_path: str):
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return
    plt.figure()
    plt.plot(xs, ys)
    plt.xlabel("Step")
    plt.ylabel("Atlas Coherence")
    plt.title("Atlas Pulse Series")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def main():
    ap = argparse.ArgumentParser(description="Run a short Atlas pulse series.")
    ap.add_argument("--steps", type=int, default=25, help="Number of pulse steps")
    ap.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    ap.add_argument("--out", type=str, default="logs/atlas_pulse", help="Output directory")
    args = ap.parse_args()

    ensure_dir(args.out)

    cfg = AtlasConfig(seed=args.seed)
    series = []
    layers_log: Dict[int, Dict[str, Any]] = {}

    # Pulse loop
    for t in range(args.steps):
        out = run_once(cfg)
        series.append(float(out["atlas_coherence"]))
        layers_log[t] = out["layers"]

    series = np.array(series, dtype=float)
    mean_val = float(np.mean(series))
    std_val  = float(np.std(series))

    # Save CSV
    csv_path = os.path.join(args.out, "atlas_pulse_series.csv")
    with open(csv_path, "w") as f:
        f.write("step,atlas_coherence\n")
        for i, v in enumerate(series):
            f.write(f"{i},{v:.6f}\n")

    # Save JSON (per-step layer metrics)
    json_path = os.path.join(args.out, "atlas_pulse_layers.json")
    with open(json_path, "w") as f:
        json.dump(layers_log, f, indent=2)

    # Save summary
    summary_path = os.path.join(args.out, "atlas_pulse_summary.txt")
    # Gather which layers reported at least once
    layer_names = set()
    for d in layers_log.values():
        layer_names.update(d.keys())
    with open(summary_path, "w") as f:
        f.write("Atlas Pulse Summary\n")
        f.write("===================\n")
        f.write(f"Steps       : {args.steps}\n")
        f.write(f"Seed        : {args.seed}\n")
        f.write(f"Mean        : {mean_val:.6f}\n")
        f.write(f"Std         : {std_val:.6f}\n")
        f.write(f"Layers seen : {', '.join(sorted(layer_names)) if layer_names else 'none'}\n")

    # Optional plot
    png_path = os.path.join(args.out, "atlas_pulse_series.png")
    maybe_plot(np.arange(args.steps), series, png_path)

    print(f"Saved:\n  {csv_path}\n  {json_path}\n  {summary_path}")
    if os.path.exists(png_path):
        print(f"  {png_path}")

if __name__ == "__main__":
    main()
