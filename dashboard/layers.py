Dashboard plotting helpers:
- temporal layering for a single run
- transfer diagnostics for cross-group resonance
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

def plot_temporal_layers(results: dict, outdir="out_layers", title="Temporal Layering"):
    """
    Stack plots of R_global(t), resource mean (if present), and env phase (if present).
    Saves a PNG to outdir/temporal_layers.png
    """
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True)

    fig, axs = plt.subplots(3, 1, figsize=(8, 10), sharex=True)
    axs[0].plot(results["R"], label="Global R")
    axs[0].legend(frameon=False); axs[0].set_ylabel("R(t)")

    r_hist = results.get("r_hist")
    if r_hist is not None:
        axs[1].plot(np.mean(r_hist, axis=1), label="Resource mean")
        axs[1].legend(frameon=False); axs[1].set_ylabel("r(t)")
    else:
        axs[1].text(0.5, 0.5, "No resource series", ha="center", va="center", transform=axs[1].transAxes)
        axs[1].set_axis_off()

    env_phase = results.get("env_phase")
    if env_phase is not None:
        axs[2].plot(env_phase, label="Env φ")
        axs[2].legend(frameon=False); axs[2].set_ylabel("φ_env(t)")
        axs[2].set_xlabel("time")
    else:
        axs[2].text(0.5, 0.5, "No env phase", ha="center", va="center", transform=axs[2].transAxes)
        axs[2].set_axis_off()

    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(out / "temporal_layers.png", dpi=160)
    plt.close(fig)

def plot_transfer_diagnostics(results: dict, outdir="out_transfer", title="Resonance Transfer"):
    """
    For sims.resonance_transfer outputs:
    - R_groups(t) for each group
    - R_global(t)
    - mean phase gap(t)
    Saves PNGs to outdir.
    """
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True)

    Rg = results["R_groups"]
    Rg_mean = Rg.mean(axis=0)
    Rg_std = Rg.std(axis=0)
    Rg_T = Rg.shape[0]
    t = np.arange(Rg_T)

    # groups coherence
    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot(111)
    for g in range(Rg.shape[1]):
        ax.plot(Rg[:, g], label=f"R_group{g}")
    ax.set_ylabel("R_group(t)"); ax.set_xlabel("time"); ax.legend(frameon=False)
    ax.set_title(f"{title} — Groups")
    fig.tight_layout(); fig.savefig(out / "groups_R.png", dpi=160); plt.close(fig)

    # global coherence
    fig = plt.figure(figsize=(8, 3))
    ax = fig.add_subplot(111)
    ax.plot(results["R_global"], label="R_global")
    ax.set_ylabel("R_global"); ax.set_xlabel("time"); ax.legend(frameon=False)
    ax.set_title(f"{title} — Global")
    fig.tight_layout(); fig.savefig(out / "global_R.png", dpi=160); plt.close(fig)

    # phase gap
    fig = plt.figure(figsize=(8, 3))
    ax = fig.add_subplot(111)
    ax.plot(results["gap"], label="mean phase gap")
    ax.set_ylabel("gap(t) [rad]"); ax.set_xlabel("time"); ax.legend(frameon=False)
    ax.set_title(f"{title} — Mean Phase Gap")
    fig.tight_layout(); fig.savefig(out / "gap.png", dpi=160); plt.close(fig)
