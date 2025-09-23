Generate dashboard figures for the multilayer community resonance simulation.

- Runs sims/multilayer_resonance.simulate(preset)
- Computes global and group resonance, resource stats, and phase gaps
- Saves PNG plots to dashboard/out (or --outdir)

Matplotlib only; no seaborn, no styles set.
"""

import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# Local imports without installing as package
try:
    from sims.multilayer_resonance import simulate
except Exception:
    import sys
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from sims.multilayer_resonance import simulate

def complex_R(phases_row):
    """|R| for one time slice (array of phases)."""
    return np.abs(np.mean(np.exp(1j * phases_row)))

def group_indices(groups):
    by = {}
    for i, g in enumerate(groups):
        by.setdefault(g, []).append(i)
    return by

def mean_abs_phase_gap(phases_row, idx_a, idx_b):
    """Mean absolute wrapped phase gap between two groups at a timestep."""
    if len(idx_a) == 0 or len(idx_b) == 0:
        return np.nan
    a = np.mean(np.exp(1j * phases_row[idx_a]))
    b = np.mean(np.exp(1j * phases_row[idx_b]))
    # gap between mean phases
    gap = np.angle(a) - np.angle(b)
    # wrap to [-pi, pi]
    gap = np.arctan2(np.sin(gap), np.cos(gap))
    return np.abs(gap)

def draw_interventions(ax, interventions, steps):
    """Shade intervention windows on a time axis [0..steps)."""
    if not interventions:
        return
    for iv in interventions:
        t0 = iv.get("t_start", None)
        t1 = iv.get("t_end", None)
        if t0 is None or t1 is None:
            continue
        ax.axvspan(t0, t1, alpha=0.08, linewidth=0)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--preset", type=str, default="multilayer_demo")
    p.add_argument("--presets_path", type=str, default=str(Path(__file__).with_name("../sims/presets.json")))
    p.add_argument("--steps", type=int, default=None, help="override steps (optional)")
    p.add_argument("--outdir", type=str, default=str(Path(__file__).with_name("out")))
    args = p.parse_args()

    presets_path = Path(args.presets_path).resolve()
    with open(presets_path, "r") as f:
        presets = json.load(f)
    if args.preset not in presets:
        raise KeyError(f"Preset '{args.preset}' not found in {presets_path}")

    preset = presets[args.preset]
    if args.steps is not None:
        preset = dict(preset)
        preset["steps"] = int(args.steps)

    # keep groups & interventions for plotting overlays
    groups = preset.get("groups", None)
    interventions = preset.get("interventions", [])

    # run simulation
    result = simulate(preset)
    TH_comm = result["community_layer_phases"]  # (T, N)
    steps, N = TH_comm.shape

    # compute global R(t)
    R = np.array([complex_R(TH_comm[t]) for t in range(steps)])

    # compute per-group R_g(t) if groups present
    group_R = {}
    idx_map = {}
    if groups is not None and len(groups) == N:
        idx_map = group_indices(groups)
        for g, idxs in idx_map.items():
            grp_curve = []
            for t in range(steps):
                grp_curve.append(complex_R(TH_comm[t, idxs]))
            group_R[g] = np.array(grp_curve)

    # compute phase gaps if at least two groups
    gaps_curve = None
    if len(idx_map) >= 2:
        # order groups deterministically by name
        group_names = sorted(idx_map.keys())
        # average absolute gap across all unique pairs
        all_pairs = []
        for i in range(len(group_names)):
            for j in range(i+1, len(group_names)):
                all_pairs.append((group_names[i], group_names[j]))
        gaps = []
        for t in range(steps):
            vals = []
            for ga, gb in all_pairs:
                vals.append(mean_abs_phase_gap(TH_comm[t], idx_map[ga], idx_map[gb]))
            gaps.append(np.nanmean(vals))
        gaps_curve = np.array(gaps)

    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    # 1) Global R(t)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(R)
    draw_interventions(ax, interventions, steps)
    ax.set_xlabel("Time")
    ax.set_ylabel("Global Resonance R(t)")
    ax.set_title("Global Resonance Over Time")
    fig.tight_layout()
    fig.savefig(outdir / "resonance_over_time.png", dpi=160)
    plt.close(fig)

    # 2) Group curves
    if group_R:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for g, curve in sorted(group_R.items()):
            ax.plot(curve, label=str(g))
        draw_interventions(ax, interventions, steps)
        ax.set_xlabel("Time")
        ax.set_ylabel("Group Resonance Rᵍ(t)")
        ax.set_title("Per-Group Resonance")
        ax.legend(loc="best", frameon=False)
        fig.tight_layout()
        fig.savefig(outdir / "group_resonance.png", dpi=160)
        plt.close(fig)

    # 3) Phase gaps
    if gaps_curve is not None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(gaps_curve)
        draw_interventions(ax, interventions, steps)
        ax.set_xlabel("Time")
        ax.set_ylabel("Mean Phase Gap |Δψ|")
        ax.set_title("Mean Absolute Phase Gap Between Groups")
        fig.tight_layout()
        fig.savefig(outdir / "phase_gaps.png", dpi=160)
        plt.close(fig)

    # 4) Resource health — we only have final mean from simulate; for a plot,
    # we can approximate by re-running shorter windows or extend simulator to return r(t).
    # For now: render a placeholder bar using final mean so the panel exists.
    final_r_mean = result.get("final_resources_mean", None)
    if final_r_mean is not None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.bar([0], [final_r_mean])
        ax.set_xticks([0])
        ax.set_xticklabels(["final mean r"])
        ax.set_ylim(0, 1)
        ax.set_ylabel("Resource Level")
        ax.set_title("Resource Health (Final Mean)")
        fig.tight_layout()
        fig.savefig(outdir / "resource_health.png", dpi=160)
        plt.close(fig)

    # Console summary: handy for quick read
    print("Saved figures to:", outdir)
    print("Global R(t): min={:.3f}  max={:.3f}  mean={:.3f}".format(R.min(), R.max(), R.mean()))
    if group_R:
        for g, curve in sorted(group_R.items()):
            print(f"  {g:>10s}  mean R={curve.mean():.3f}  max={curve.max():.3f}")
    if gaps_curve is not None:
        print("Mean |Δψ| over time:", np.nanmean(gaps_curve))
