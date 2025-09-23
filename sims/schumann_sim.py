"""
sims/schumann_sim.py

Small utility to:
- generate a synthetic Schumann-like pulse from a time series by smoothing/downsampling,
- optionally create an overlay PNG (requires matplotlib) to place in docs/assets/dashboard/.

Usage:
python -m sims.schumann_sim --input logs/timeseries.csv --out logs/schumann/pulse.npy --overlay docs/assets/dashboard/schumann_overlay.png
"""

import numpy as np
import os
import argparse

def load_timeseries(path):
    if path.endswith('.npy'):
        return np.load(path)
    else:
        return np.loadtxt(path, delimiter=',', usecols=[0])  # assume first column

def generate_pulse(series: np.ndarray, downsample: int = 10, smooth_win: int = 31):
    # downsample
    if downsample > 1:
        series = series.reshape(-1)[:len(series)//downsample*downsample]
        series = series.reshape(-1, downsample).mean(axis=1)
    # simple smoothing
    kernel = np.ones(smooth_win)/smooth_win
    pulse = np.convolve(series, kernel, mode='same')
    # normalize
    pulse = (pulse - np.mean(pulse)) / (np.std(pulse) + 1e-12)
    return pulse

def save_numpy(arr, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    np.save(path, arr)

def make_overlay_image(pulse, outpath):
    try:
        import matplotlib.pyplot as plt
    except Exception:
        print("matplotlib not available — skipping overlay image")
        return
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    t = np.arange(len(pulse))
    plt.figure(figsize=(6,2))
    plt.plot(t, pulse, linewidth=1.5)
    plt.fill_between(t, pulse, alpha=0.12)
    plt.title("Schumann Pulse (Atlas canonical)")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)
    plt.close()
    print(f"Saved overlay image {outpath}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--out', required=True, help="path to .npy output pulse")
    parser.add_argument('--overlay', required=False, help="optional png overlay path")
    parser.add_argument('--downsample', type=int, default=10)
    parser.add_argument('--smooth', type=int, default=31)
    args = parser.parse_args()

    series = load_timeseries(args.input)
    pulse = generate_pulse(series, downsample=args.downsample, smooth_win=args.smooth)
    save_numpy(pulse, args.out)
    print(f"Saved pulse to {args.out}")
    if args.overlay:
        make_overlay_image(pulse, args.overlay)
