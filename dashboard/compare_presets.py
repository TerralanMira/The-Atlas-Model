"""
Compare two presets side-by-side using multilayer resonance.
Outputs simple PNGs for quick diffing (no web server).

Usage:
    python dashboard/compare_presets.py --a multilayer_demo --b memory_demo
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

def global_R(phase_TN):
    T = phase_TN.shape[0]
    R = np.zeros(T)
    for t in range(T):
        R[t] = np.abs(np.mean(np.exp(1j * phase_TN[t])))
    return R

def run(preset):
    result = simulate(preset)
    TH = result["community_layer_phases"]
    R = global_R(TH)
    return {
        "R": R,
        "r_hist": result.get("r_history"),
        "env_phase": result.get("env_phase"),
        "summary": result["summary"],
        "name": preset.get("name", "preset")
    }

def plot_compare(A, B, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)

    # Global R
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(A["R"], label=f"{A['name']} R(t)")
    ax.plot(B["R"], label=f"{B['name']} R(t)")
    ax.set_xlabel("Time")
    ax.set_ylabel("Global Resonance R(t)")
    ax.set_title("Global Resonance — A/B")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(outdir / "compare_R.png", dpi=160)
    plt.close(fig)

    # Resource mean ± std if available
    if A["r_hist"] is not None and B["r_hist"] is not None:
        for label, data in [("A", A), ("B", B)]:
            mean_r = np.mean(data["r_hist"], axis=1)
            std_r = np.std(data["r_hist"], axis=1)
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.plot(mean_r)
            ax.fill_between(np.arange(len(mean_r)), mean_r - std_r, mean_r + std_r, alpha=0.15)
            ax.set_xlabel("Time")
            ax.set_ylabel("r(t)")
            ax.set_title(f"Resource Health — {data['name']}")
            fig.tight_layout()
            fig.savefig(outdir / f"resource_{label}.png", dpi=160)
            plt.close(fig)

    # Env phase if available
    if A["env_phase"] is not None or B["env_phase"] is not None:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        if A["env_phase"] is not None:
            ax.plot(A["env_phase"], label=f"{A['name']} φ_env")
        if B["env_phase"] is not None:
            ax.plot(B["env_phase"], label=f"{B['name']} φ_env")
        ax.set_xlabel("Time")
        ax.set_ylabel("φ_env(t) [rad]")
        ax.set_title("Environment Phase — A/B")
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(outdir / "compare_env_phase.png", dpi=160)
        plt.close(fig)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", type=str, default="multilayer_demo")
    ap.add_argument("--b", type=str, default="memory_demo")
    ap.add_argument("--presets_path", type=str, default=str(Path(__file__).with_name("../sims/presets.json")))
    ap.add_argument("--outdir", type=str, default=str(Path(__file__).with_name("out_compare")))
    args = ap.parse_args()

    pres_path = Path(args.presets_path).resolve()
    presets = json.loads(Path(pres_path).read_text())

    if args.a not in presets or args.b not in presets:
        raise KeyError(f"Missing preset: {args.a if args.a not in presets else args.b}")

    A = run({**presets[args.a], "name": args.a})
    B = run({**presets[args.b], "name": args.b})

    outdir = Path(args.outdir).resolve()
    plot_compare(A, B, outdir)

    print("Saved A/B comparison to:", outdir)

if __name__ == "__main__":
    main()
