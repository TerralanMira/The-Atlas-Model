#!/usr/bin/env python3
"""
Earth Layer Demo

Runs the Earth composite step over a lattice and saves:
- earth_coherence_over_time.png : amplitude/phase/combined coherence vs steps
- earth_final_scalar.png        : final scalar state as an image
- earth_final_phases.png        : final phases (wrapped) as an image
- earth_states_trajectory.csv   : scalar states over time (steps x N)
- earth_phases_trajectory.csv   : phases over time (steps x N)
- earth_coherence_trajectory.csv: amplitude, phase, combined per step

Usage:
  python sims/earth_demo.py --rows 30 --cols 30 --steps 300 --seed 42 --save-dir logs/earth_demo
"""

import argparse
import os
import numpy as np
import matplotlib.pyplot as plt

try:
    from algorithms.earth_structures import (
        lattice_adjacency, row_normalize,
        ThresholdField, MultiWellPotential,
        EarthStepConfig, earth_step,
        variance_coherence, phase_locking_value, combined_coherence
    )
except Exception as e:
    raise SystemExit(
        "Import error: ensure algorithms/earth_structures.py exists and is importable.\n"
        f"{e}"
    )

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def save_line_plot(xs, ys_list, labels, title, out_path, xlabel="Step", ylabel="Value"):
    plt.figure()
    for y, lbl in zip(ys_list, labels):
        plt.plot(xs, y, label=lbl)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def save_grid_image(arr_1d, n_rows, n_cols, title, out_path):
    plt.figure()
    grid = arr_1d.reshape(n_rows, n_cols)
    plt.imshow(grid, aspect="equal")
    plt.title(title)
    plt.colorbar()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def parse_args():
    p = argparse.ArgumentParser(description="Run Earth layer lattice demo.")
    p.add_argument("--rows", type=int, default=25, help="Grid rows")
    p.add_argument("--cols", type=int, default=25, help="Grid cols")
    p.add_argument("--steps", type:int, default=250, help="Simulation steps")
    p.add_argument("--seed", type=int, default=None, help="Random seed")
    p.add_argument("--save-dir", type=str, default="logs/earth_demo", help="Output directory")
    return p.parse_args()

def main():
    args = parse_args()
    ensure_dir(args.save_dir)

    if args.seed is not None:
        np.random.seed(args.seed)

    n_rows, n_cols = args.rows, args.cols
    N = n_rows * n_cols

    # Structure (periodic torus)
    A = lattice_adjacency(n_rows, n_cols, periodic=True)
    A_norm = row_normalize(A)

    # Fields
    thresholds = ThresholdField.gradient(n_rows, n_cols, low=0.05, high=0.25)
    potential = MultiWellPotential.triwell(centers=(-0.8, 0.0, 0.8), weights=(1.0, 0.5, 1.0), stiffness=0.8)

    # States
    rng = np.random.default_rng(args.seed)
    state = rng.normal(0.0, 0.4, size=N).astype(float)     # scalar field
    phases = rng.uniform(0, 2*np.pi, size=N).astype(float) # phases
    omega  = rng.normal(0.0, 0.05, size=N).astype(float)   # intrinsic freq

    cfg = EarthStepConfig()

    # Logs
    state_traj = []
    phases_traj = []
    amp_log, phs_log, comb_log = [], [], []

    for t in range(args.steps):
        state, phases = earth_step(state, phases, omega, A, A_norm, thresholds, potential, cfg)

        # Log
        state_traj.append(state.copy())
        phases_traj.append(phases.copy())
        amp_log.append(variance_coherence(state))
        phs_log.append(phase_locking_value(phases))
        comb_log.append(combined_coherence(state, phases))

    state_traj = np.array(state_traj)   # (steps, N)
    phases_traj = np.array(phases_traj) # (steps, N)
    coh_traj = np.column_stack([amp_log, phs_log, comb_log])

    # Save CSVs
    np.savetxt(os.path.join(args.save_dir, "earth_states_trajectory.csv"), state_traj, delimiter=",")
    np.savetxt(os.path.join(args.save_dir, "earth_phases_trajectory.csv"), phases_traj, delimiter=",")
    np.savetxt(os.path.join(args.save_dir, "earth_coherence_trajectory.csv"), coh_traj, delimiter=",",
               header="amplitude_coh,phase_coh,combined_coh", comments="")

    # Save plots
    save_line_plot(
        xs=np.arange(args.steps),
        ys_list=[amp_log, phs_log, comb_log],
        labels=["Amplitude", "Phase", "Combined"],
        title="Earth: Coherence Over Time",
        out_path=os.path.join(args.save_dir, "earth_coherence_over_time.png")
    )

    save_grid_image(state, n_rows, n_cols, "Earth: Final Scalar State",
                    os.path.join(args.save_dir, "earth_final_scalar.png"))

    # Wrap phases to [0, 2π) then scale visually
    phases_wrapped = (phases % (2*np.pi))
    save_grid_image(phases_wrapped, n_rows, n_cols, "Earth: Final Phases",
                    os.path.join(args.save_dir, "earth_final_phases.png"))

    print(f"Saved outputs to: {args.save_dir}")
    print(f"Final coherence (amplitude / phase / combined): "
          f"{amp_log[-1]:.4f} / {phs_log[-1]:.4f} / {comb_log[-1]:.4f}")

if __name__ == "__main__":
    main()
