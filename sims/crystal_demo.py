#!/usr/bin/env python3
"""
Crystal Demo — visualize lattice, time-memory, and resonance-memory.

If precomputed .npy files exist in the working directory, this script loads them:
  - crystal_lattice.npy
  - crystal_time_memory.npy
  - crystal_freq_memory.npy
Else, it generates them by running algorithms.crystal_growth.grow_crystal().

Outputs:
  - crystal_lattice.png
  - crystal_time_memory.png
  - crystal_freq_memory.png
  - crystal_summary.txt  (basic stats)

Usage:
  python sims/crystal_demo.py
"""

import os
import numpy as np
import matplotlib.pyplot as plt

def save_img(array2d, title, out_path):
    plt.figure()
    plt.imshow(array2d, aspect="equal")
    plt.title(title)
    plt.colorbar()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def load_or_generate():
    needed = [
        "crystal_lattice.npy",
        "crystal_time_memory.npy",
        "crystal_freq_memory.npy",
    ]
    if all(os.path.exists(f) for f in needed):
        L = np.load("crystal_lattice.npy")
        Tm = np.load("crystal_time_memory.npy")
        Fm = np.load("crystal_freq_memory.npy")
        return L, Tm, Fm

    # Generate if missing
    try:
        from algorithms.crystal_growth import CrystalConfig, grow_crystal
    except Exception as e:
        raise SystemExit(
            "Could not import algorithms.crystal_growth. "
            "Ensure algorithms/crystal_growth.py exists.\n"
            f"Import error: {e}"
        )

    cfg = CrystalConfig()
    rng = np.random.default_rng(7)
    L, Tm, Fm, _, _ = grow_crystal(cfg, rng)

    np.save("crystal_lattice.npy", L)
    np.save("crystal_time_memory.npy", Tm)
    np.save("crystal_freq_memory.npy", Fm)
    return L, Tm, Fm

def write_summary(L, Tm, Fm, out_path="crystal_summary.txt"):
    area = float(L.sum())
    occupied_ratio = area / (L.size + 1e-8)
    # Only consider accreted sites for stats
    mask = (L > 0)
    times = Tm[mask]
    freqs = Fm[mask]
    with open(out_path, "w") as f:
        f.write("Crystal Summary\n")
        f.write("================\n")
        f.write(f"Grid size              : {L.shape[0]} x {L.shape[1]}\n")
        f.write(f"Occupied sites (area)  : {int(area)}\n")
        f.write(f"Occupied ratio         : {occupied_ratio:.4f}\n")
        if times.size > 0:
            f.write(f"Accretion time (min/mean/max): {times.min()} / {times.mean():.2f} / {times.max()}\n")
        if freqs.size > 0:
            f.write(f"Resonance memory (min/mean/max): {freqs.min():.4f} / {freqs.mean():.4f} / {freqs.max():.4f}\n")

def main():
    L, Tm, Fm = load_or_generate()

    # Visualizations
    save_img(L,  "Crystal Lattice (occupied=1)",      "crystal_lattice.png")
    # Replace -1 (never accreted) with NaN for clearer color scaling
    Tm_vis = Tm.astype(float)
    Tm_vis[Tm_vis < 0] = np.nan
    save_img(Tm_vis, "Accretion Time Memory",         "crystal_time_memory.png")
    save_img(Fm,     "Resonance Memory (local hum)",  "crystal_freq_memory.png")

    # Summary
    write_summary(L, Tm, Fm)
    print("Saved: crystal_lattice.png, crystal_time_memory.png, crystal_freq_memory.png, crystal_summary.txt")

if __name__ == "__main__":
    main()
