#!/usr/bin/env python3
"""
Atlas Dashboard Builder
- Reads logs from sims (pulse + self-learning + crystal demo)
- Produces PNG charts and a single static HTML dashboard
- No heavy deps: numpy, pandas, matplotlib

Usage (from repo root):
  python scripts/dashboard_build.py \
    --pulse logs/atlas_pulse/atlas_pulse_series.csv \
    --layers logs/atlas_pulse/atlas_pulse_layers.json \
    --sln logs/sln_demo/sln_series.csv \
    --out docs/assets/dashboard

The generated HTML will be at:
  docs/dashboard.html   (plus images under docs/assets/dashboard)
"""

import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

# --------- plotting helpers (matplotlib, single-style) ----------
import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def plot_series(xs, ys, title, ylabel, out_path: Path):
    plt.figure()
    plt.plot(xs, ys)
    plt.xlabel("Step")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def plot_layer_bars(layer_means: dict, title: str, out_path: Path):
    names = list(layer_means.keys())
    vals = [layer_means[k] for k in names]
    plt.figure()
    plt.bar(range(len(names)), vals)
    plt.xticks(range(len(names)), names, rotation=20, ha="right")
    plt.ylabel("Mean (normalized)")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def normalize(vals):
    vals = np.array(list(vals), dtype=float)
    if np.all(~np.isfinite(vals)):
        return np.zeros_like(vals)
    finite = np.isfinite(vals)
    if finite.sum() == 0:
        return np.zeros_like(vals)
    m = vals[finite].min()
    M = vals[finite].max()
    if M - m < 1e-12:
        return np.zeros_like(vals) + 0.5
    out = (vals - m) / (M - m)
    out[~finite] = 0.0
    return out


def build_dashboard(pulse_csv: Path,
                    layers_json: Path | None,
                    sln_csv: Path | None,
                    out_dir: Path,
                    html_out: Path):
    ensure_dir(out_dir)
    # --- Pulse series
    if pulse_csv.exists():
        dfp = pd.read_csv(pulse_csv)
        xs = dfp["step"].values
        ys = dfp["atlas_coherence"].values
        plot_series(xs, ys, "Atlas Coherence (Pulse Series)", "Atlas Coherence", out_dir / "pulse_series.png")
        pulse_mean = float(np.mean(ys))
        pulse_std = float(np.std(ys))
    else:
        xs = np.arange(1)
        ys = np.array([0.0])
        pulse_mean, pulse_std = 0.0, 0.0

    # --- Layer metrics (optional)
    layer_img = None
    layer_means = {}
    if layers_json and layers_json.exists():
        with open(layers_json, "r") as f:
            L = json.load(f)  # {step: {layer: metrics}}
        # Collect simple layer scalars (mean of each layer’s available metrics)
        buckets = {}
        for step, layers in L.items():
            for lname, metrics in layers.items():
                # numeric metrics only
                vals = []
                for v in metrics.values():
                    if isinstance(v, (int, float)) and np.isfinite(v):
                        vals.append(float(v))
                if not vals:
                    continue
                buckets.setdefault(lname, []).append(np.mean(vals))
        # normalize and bar-plot
        for lname, arr in buckets.items():
            layer_means[lname] = float(np.mean(arr))
        if layer_means:
            names = list(layer_means.keys())
            vals = normalize([layer_means[k] for k in names])
            layer_means = {k: float(v) for k, v in zip(names, vals)}
            plot_layer_bars(layer_means, "Layer Contribution (normalized mean)", out_dir / "layer_contrib.png")
            layer_img = "layer_contrib.png"

    # --- Self-learning series (optional)
    sln_img = None
    sln_mean = None
    if sln_csv and sln_csv.exists():
        dfs = pd.read_csv(sln_csv)
        sxs = dfs["step"].values
        sys = dfs["coherence"].values
        plot_series(sxs, sys, "Self-Learning Coherence", "Coherence", out_dir / "sln_series.png")
        sln_img = "sln_series.png"
        sln_mean = float(np.mean(sys))

    # --- Crystal snapshots (optional, if user ran crystal_demo.py in repo root)
    crystal_imgs = []
    for name in ["crystal_lattice.png", "crystal_time_memory.png", "crystal_freq_memory.png"]:
        p = Path(name)
        if p.exists():
            # copy into out_dir
            data = p.read_bytes()
            (out_dir / name).write_bytes(data)
            crystal_imgs.append(name)

    # --- Pulse image path
    (out_dir / "pulse_series.png").exists()  # ensure built

    # --- HTML assembly
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Atlas Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
 body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 24px; }}
 h1,h2 {{ margin: 0 0 8px 0; }}
 section {{ margin: 24px 0; }}
 .card {{ border: 1px solid #e3e3e3; border-radius: 8px; padding: 16px; }}
 .grid {{ display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }}
 img {{ max-width: 100%; height: auto; border: 1px solid #eee; border-radius: 4px; }}
 .meta {{ color: #666; font-size: 0.9rem; }}
 .pill {{ display:inline-block; background:#e8f6f6; color:#0b6b6b; padding:2px 8px; border-radius: 999px; font-size:0.85rem; }}
</style>
</head>
<body>
  <h1>Atlas Dashboard</h1>
  <p class="meta">A static visual of the hum — generated from simulation logs.</p>

  <section class="card">
    <h2>Pulse</h2>
    <p>The orchestrated heartbeat (atlas_coherence). Mean: <span class="pill">{pulse_mean:.4f}</span> · Std: <span class="pill">{pulse_std:.4f}</span></p>
    <img src="assets/dashboard/pulse_series.png" alt="Pulse series">
  </section>

  <section class="card">
    <h2>Layers</h2>
    <p>Relative, normalized contribution inferred from layer metrics (if available).</p>
    {"<img src='assets/dashboard/" + layer_img + "' alt='Layer contribution'>" if layer_img else "<p class='meta'>No layer metrics JSON found yet.</p>"}
  </section>

  <section class="card">
    <h2>Self-Learning (Water/Air)</h2>
    {"<p>Mean coherence: <span class='pill'>" + f"{sln_mean:.4f}" + "</span></p>" if sln_mean is not None else ""}
    {"<img src='assets/dashboard/" + sln_img + "' alt='Self-learning series'>" if sln_img else "<p class='meta'>No SLN series CSV found yet.</p>"}
  </section>

  <section class="card">
    <h2>Crystals</h2>
    <div class="grid">
      {"".join(f"<img src='assets/dashboard/{img}' alt='{img}'>" for img in crystal_imgs) if crystal_imgs else "<p class='meta'>No crystal snapshots found. Run <code>python sims/crystal_demo.py</code> in repo root.</p>"}
    </div>
  </section>

  <section class="card">
    <h2>How to refresh</h2>
    <ol>
      <li>Run one or more sims:
        <ul>
          <li><code>python sims/atlas_pulse_demo.py --steps 30 --seed 7 --out logs/atlas_pulse</code></li>
          <li><code>python sims/self_learning_demo.py --steps 300 --out logs/sln_demo</code></li>
          <li><code>python sims/crystal_demo.py</code></li>
        </ul>
      </li>
      <li>Build visuals:
        <br><code>python scripts/dashboard_build.py --pulse logs/atlas_pulse/atlas_pulse_series.csv --layers logs/atlas_pulse/atlas_pulse_layers.json --sln logs/sln_demo/sln_series.csv --out docs/assets/dashboard</code>
      </li>
      <li>Open <code>docs/dashboard.html</code> locally or publish via GitHub Pages.</li>
    </ol>
  </section>
</body>
</html>
"""
    html_out.write_text(html, encoding="utf-8")
    print(f"Wrote {html_out}")
    print(f"Images in {out_dir}")

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pulse", type=str, default="logs/atlas_pulse/atlas_pulse_series.csv")
    ap.add_argument("--layers", type=str, default="logs/atlas_pulse/atlas_pulse_layers.json")
    ap.add_argument("--sln", type=str, default="logs/sln_demo/sln_series.csv")
    ap.add_argument("--out", type=str, default="docs/assets/dashboard")
    args = ap.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    pulse_csv = Path(args.pulse)
    layers_json = Path(args.layers) if args.layers else None
    sln_csv = Path(args.sln) if args.sln else None
    out_dir = Path(args.out)
    html_out = Path("docs/dashboard.html")
    build_dashboard(pulse_csv, layers_json, sln_csv, out_dir, html_out)
