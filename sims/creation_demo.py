# sims/creation_demo.py
"""
Demo: run the Synchronization-Led Emergence toy model and save outputs.

Saves:
- data/creation/run_{seed}.csv
- figures/creation_R_K_{seed}.png

Usage:
    python -m sims.creation_demo
"""

from __future__ import annotations
from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

from sims.creation import CreationConfig, simulate

def run_and_save(seed: int = 7) -> Path:
    cfg = CreationConfig(seed=seed, steps=6000, dt=0.002)
    out = simulate(cfg)

    # ensure dirs
    data_dir = Path("data/creation"); data_dir.mkdir(parents=True, exist_ok=True)
    fig_dir = Path("figures"); fig_dir.mkdir(parents=True, exist_ok=True)

    # CSV
    csv_path = data_dir / f"run_{seed}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["t_sec","R","K","gap_to_env","anchors_frac"])
        t = np.arange(len(out["R"])) * cfg.dt
        for i in range(len(t)):
            w.writerow([f"{t[i]:.6f}", f"{out['R'][i]:.6f}", f"{out['K'][i]:.6f}",
                        f"{out['gap_to_env'][i]:.6f}", f"{out['anchors_frac'][i]:.6f}"])

    # PNG
    t = np.arange(len(out["R"])) * cfg.dt
    fig, ax = plt.subplots(2,1, figsize=(9,6), sharex=True)
    ax[0].plot(t, out["R"], label="R(t)")
    ax[0].axhline(cfg.R_event, ls="--", c="gray", label="R_event")
    ax[0].set_ylabel("Coherence R")
    ax[0].legend(loc="best")
    ax[1].plot(t, out["K"], label="K(t)")
    ax[1].set_ylabel("Coupling K")
    ax[1].set_xlabel("Time (s)")
    ax[1].legend(loc="best")
    # mark events
    ev = out["creation_events"]
    for row in ev:
        ax[0].axvline(row[0], color="tab:red", alpha=0.5)
        ax[1].axvline(row[0], color="tab:red", alpha=0.5)
    fig.suptitle(f"Emergence demo (seed={cfg.seed}) | events={out['summary']['events_count']}")
    png_path = fig_dir / f"creation_R_K_{seed}.png"
    fig.tight_layout()
    fig.savefig(png_path, dpi=160)
    plt.close(fig)

    return csv_path

if __name__ == "__main__":
    p = run_and_save(seed=7)
    print(f"Wrote {p}")
