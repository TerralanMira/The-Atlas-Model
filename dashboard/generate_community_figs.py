"""
Generate dashboard figures for multilayer community resonance.

Now includes:
- env phase trace
- resource time series (mean +/- band)
- before/after comparison around first intervention

Matplotlib only; no seaborn, no styles.
"""

import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

try:
    from sims.multilayer_resonance import simulate
except Exception:
    import sys
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from sims.multilayer_resonance import simulate

def complex_R(phases_row):
    return np.abs(np.mean(np.exp(1j * phases_row)))

def group_indices(groups):
    by = {}
    for i, g in enumerate(groups):
        by.setdefault(g, []).append(i)
    return by

def mean_abs_phase_gap(phases_row, idx_a, idx_b):
    if len(idx_a) == 0 or len(idx_b) == 0:
        return np.nan
    a = np.mean(np.exp(1j * phases_row[idx_a]))
    b = np.mean(np.exp(1j * phases_row[idx_b]))
    gap = np.angle(a) - np.angle(b)
    gap = np.arctan2(np.sin(gap), np.cos(gap))
    return np.abs(gap)

def draw_interventions(ax, interventions, steps):
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
    p.add_argument("--steps", type=int, default=None)
    p.add_argument("--outdir", type=str, default=str(Path(__file__).with_name("out")))
    args = p.parse_args()

    presets_path = Path(args.presets_path).resolve()
    with open(presets_path, "r") as f:
        presets = json.load(f)
    if args.preset not in presets:
        raise KeyError(f"Preset '{args.preset}' not found in {presets_path}")
    preset = presets[argspreset] if False else presets[args.preset]  # keep lints happy

    if args.steps is not None:
        preset = dict(preset)
        preset["steps"] = int(args.steps)

    result = simulate(preset)
    TH_comm = result["community_layer_phases"]  # (T, N)
    r_hist = result.get("r_history", None)
    env_phase = result.get("env_phase", None)
    interventions = result.get("interventions", [])
    groups = result.get("groups", None)
    steps, N = TH_comm.shape

    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    # Global R(t)
    R = np.array([complex_R(TH_comm[t]) for t in range(steps)])
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

    # Groups
    idx_map = {}
    if groups is not None and len(groups) == N:
        for i, g in enumerate(groups):
            idx_map.setdefault(g, []).append(i)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for g, idxs in sorted(idx_map.items()):
            curve = [complex_R(TH_comm[t, idxs]) for t in range(steps)]
            ax.plot(curve, label=str(g))
        draw_interventions(ax, interventions, steps)
        ax.set_xlabel("Time")
        ax.set_ylabel("Group Resonance Rᵍ(t)")
        ax.set_title("Per-Group Resonance")
        ax.legend(loc="best", frameon=False)
        fig.tight_layout()
        fig.savefig(outdir / "group_resonance.png", dpi=160)
        plt.close(fig)

    # Phase gaps (avg across all pairs)
    if len(idx_map) >= 2:
        names = sorted(idx_map.keys())
        pairs = [(names[i], names[j]) for i in range(len(names)) for j in range(i+1, len(names))]
        gaps = []
        for t in range(steps):
            vals = [mean_abs_phase_gap(TH_comm[t], idx_map[a], idx_map[b]) for a, b in pairs]
            gaps.append(np.nanmean(vals))
        gaps = np.array(gaps)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(gaps)
        draw_interventions(ax, interventions, steps)
        ax.set_xlabel("Time")
        ax.set_ylabel("Mean Phase Gap |Δψ|")
        ax.set_title("Mean Absolute Phase Gap Between Groups")
        fig.tight_layout()
        fig.savefig(outdir / "phase_gaps.png", dpi=160)
        plt.close(fig)

    # Environment phase
    if env_phase is not None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(env_phase)
        draw_interventions(ax, interventions, steps)
        ax.set_xlabel("Time")
        ax.set_ylabel("φ_env(t) [rad]")
        ax.set_title("Environment Phase Over Time")
        fig.tight_layout()
        fig.savefig(outdir / "environment_phase.png", dpi=160)
        plt.close(fig)

    # Resource time series (mean ± band)
    if r_hist is not None:
        mean_r = np.mean(r_hist, axis=1)
        std_r = np.std(r_hist, axis=1)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(mean_r)
        ax.fill_between(np.arange(len(mean_r)), mean_r - std_r, mean_r + std_r, alpha=0.15)
        draw_interventions(ax, interventions, steps)
        ax.set_xlabel("Time")
        ax.set_ylabel("Resource level r(t)")
        ax.set_title("Resource Health Over Time (mean ± std)")
        fig.tight_layout()
        fig.savefig(outdir / "resource_over_time.png", dpi=160)
        plt.close(fig)

    # Before/After comparator around first intervention (if windows available)
    windows = result.get("windows", None)
    if windows is not None:
        pre = slice(windows["pre"][0], windows["pre"][1])
        post = slice(windows["post"][0], windows["post"][1])
        R_pre = R[pre].mean() if pre.stop > pre.start else np.nan
        R_post = R[post].mean() if post.stop > post.start else np.nan

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.bar([0, 1], [R_pre, R_post])
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["pre", "post"])
        ax.set_ylim(0, 1)
        ax.set_ylabel("Mean R")
        ax.set_title("Before / After (first intervention)")
        fig.tight_layout()
        fig.savefig(outdir / "before_after_intervention.png", dpi=160)
        plt.close(fig)

    # Console summary
    print("Saved figures to:", outdir)
    print("Global R(t): min={:.3f}  max={:.3f}  mean={:.3f}".format(R.min(), R.max(), R.mean()))
    if len(idx_map) >= 1:
        for g, idxs in sorted(idx_map.items()):
            curve = [complex_R(TH_comm[t, idxs]) for t in range(steps)]
            print(f"  {g:>10s}  mean R={np.mean(curve):.3f}  max={np.max(curve):.3f}")
