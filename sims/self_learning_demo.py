#!/usr/bin/env python3
"""
Self-Learning Network — Demo Simulation

Runs the elemental self-learning network and produces:
- coherence_over_time.png      : Coherence trajectory across steps
- final_state_hist.png         : Distribution of node states at final step
- connections_heatmap.png      : Connectivity matrix visualization
- states_trajectory.csv        : Node states over time (steps x nodes)
- coherence_trajectory.csv     : Coherence metric per step

Usage:
  python sims/self_learning_demo.py --nodes 200 --steps 300 --learning-rate 0.08 --seed 42 --save-dir logs/self_learning

Notes:
- Visualizations use matplotlib only (no seaborn, no style overrides).
"""

import argparse
import os
import numpy as np
import matplotlib.pyplot as plt

# Import the model from algorithms
try:
    from algorithms.self_learning_networks import SelfLearningNetwork
except Exception as e:
    raise SystemExit(
        "Could not import SelfLearningNetwork from algorithms.self_learning_networks. "
        "Ensure the file exists and package paths are correct.\n"
        f"Import error: {e}"
    )

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def save_coherence_plot(coh_list, out_path):
    plt.figure()
    plt.plot(range(len(coh_list)), coh_list)
    plt.xlabel("Step")
    plt.ylabel("Coherence (1 - variance)")
    plt.title("Coherence Over Time")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def save_final_hist(states, out_path):
    plt.figure()
    plt.hist(states, bins=30)
    plt.xlabel("State value")
    plt.ylabel("Count")
    plt.title("Final Node State Distribution")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def save_connections_heatmap(conn, out_path):
    plt.figure()
    plt.imshow(conn, aspect="auto")
    plt.xlabel("To node")
    plt.ylabel("From node")
    plt.title("Connectivity Matrix (row-normalized)")
    plt.colorbar()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def run_demo(args):
    if args.seed is not None:
        np.random.seed(args.seed)

    ensure_dir(args.save_dir)

    net = SelfLearningNetwork(num_nodes=args.nodes, learning_rate=args.learning_rate)

    # Run and log trajectory
    trajectory = []
    coherence = []
    for step in range(args.steps):
        net.step()
        trajectory.append(net.states.copy())
        coherence.append(net.coherence_metric())

    trajectory = np.array(trajectory)  # shape: (steps, nodes)
    coherence = np.array(coherence)

    # Save CSV logs
    np.savetxt(os.path.join(args.save_dir, "states_trajectory.csv"), trajectory, delimiter=",")
    np.savetxt(os.path.join(args.save_dir, "coherence_trajectory.csv"), coherence, delimiter=",")

    # Save plots
    save_coherence_plot(coherence, os.path.join(args.save_dir, "coherence_over_time.png"))
    save_final_hist(trajectory[-1], os.path.join(args.save_dir, "final_state_hist.png"))
    save_connections_heatmap(net.connections, os.path.join(args.save_dir, "connections_heatmap.png"))

    # Console summary
    print(f"Saved logs and plots to: {args.save_dir}")
    print(f"Final coherence: {coherence[-1]:.4f}")
    print("Files:")
    for fname in ["states_trajectory.csv",
                  "coherence_trajectory.csv",
                  "coherence_over_time.png",
                  "final_state_hist.png",
                  "connections_heatmap.png"]:
        print(" -", os.path.join(args.save_dir, fname))

def parse_args():
    p = argparse.ArgumentParser(description="Run the elemental self-learning network demo.")
    p.add_argument("--nodes", type=int, default=150, help="Number of nodes in the network.")
    p.add_argument("--steps", type=int, default=250, help="Simulation steps to run.")
    p.add_argument("--learning-rate", type=float, default=0.06, help="Adaptation learning rate.")
    p.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility.")
    p.add_argument("--save-dir", type=str, default="logs/self_learning", help="Directory to save outputs.")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    run_demo(args)
