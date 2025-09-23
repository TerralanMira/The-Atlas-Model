#!/usr/bin/env python3
"""
Group Coherence (Kuramoto order parameter R)

Purpose
-------
Estimate collective synchrony across participants (HRV and/or EEG) against a shared band.
- Accepts a list of CSV files per participant and stream type.
- For each participant: load, resample to common fs, bandpass, extract analytic phase.
- Compute Kuramoto order parameter R(t) and summary stats.
- Optionally compute individual PLV to a reference (e.g., Schumann proxy) if provided.

Supported CSV formats
---------------------
HRV:
  A) rr_ms[,t_s]
  B) t_s,<hrv_col>

EEG:
  t_s,<eeg_col>

Optional reference (e.g., Schumann):
  t_s,<ref_col>    (a narrowband proxy; if frequencies vary over time, pre-synthesize)

Usage
-----
python simulations/health/group_coherence.py \
  --files data/group/*.csv \
  --stream hrv \
  --fs 256 \
  --band 0.04 0.15 \
  --outdir outputs/group_hrv

python simulations/health/group_coherence.py \
  --files data/group_eeg/*.csv \
  --stream eeg \
  --fs 256 \
  --band 8 12 \
  --outdir outputs/group_eeg \
  --reference-csv data/schumann_proxy.csv --reference-col proxy

Dependencies
------------
numpy scipy pandas matplotlib
"""

import argparse
import glob
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, hilbert, welch

# ----------------------- DSP helpers -----------------------

def butter_bandpass(low, high, fs, order=4):
    nyq = 0.5 * fs
    low_n = max(1e-6, low / nyq)
    high_n = min(0.999999, high / nyq)
    b, a = butter(order, [low_n, high_n], btype="band")
    return b, a

def bandpass(x, fs, low, high, order=4):
    b, a = butter_bandpass(low, high, fs, order)
    return filtfilt(b, a, x)

def analytic_phase(x):
    return np.angle(hilbert(x))

def power_spectrum(x, fs):
    f, Pxx = welch(x, fs=fs, nperseg=min(len(x), 4096))
    return f, Pxx

# ----------------------- loading & resampling -----------------------

def resample_linear(t_src, x_src, t_tgt):
    return np.interp(t_tgt, t_src, x_src)

def unify_time_interval(t_list, fs):
    t0 = max(t[0] for t in t_list)
    t1 = min(t[-1] for t in t_list)
    if t1 <= t0:
        raise ValueError("No temporal overlap across participants.")
    N = int(np.floor((t1 - t0) * fs))
    t = np.arange(N) / fs + t0
    return t

def load_hrv_csv(path, fs, hrv_col=None):
    df = pd.read_csv(path)
    cols = {c.lower(): c for c in df.columns}

    # RR form
    if "rr_ms" in cols:
        rr = df[cols["rr_ms"]].to_numpy().astype(float) / 1000.0
        if "t_s" in cols:
            t_beats = df[cols["t_s"]].to_numpy().astype(float)
        else:
            t_beats = np.cumsum(rr)
        t_end = t_beats[-1]
        N = int(np.floor(t_end * fs))
        t = np.arange(N) / fs
        sig = np.interp(t, t_beats, rr, left=rr[0], right=rr[-1])
        return t, sig - np.mean(sig)

    # time-series form
    if "t_s" not in cols:
        raise ValueError(f"{path}: HRV CSV must contain 'rr_ms' or 't_s'.")
    t_raw = df[cols["t_s"]].to_numpy().astype(float)
    if hrv_col is None:
        guesses = [c for c in df.columns if c.lower() in ("hrv", "tachogram", "rr_s", "rr_signal", "value")]
        if not guesses:
            raise ValueError(f"{path}: Provide --hrv-col for HRV series.")
        hrv_col = guesses[0]
    x_raw = df[hrv_col].to_numpy().astype(float)
    t = np.arange(int(np.floor((t_raw[-1] - t_raw[0]) * fs))) / fs + t_raw[0]
    x = np.interp(t, t_raw, x_raw)
    return t, x - np.mean(x)

def load_eeg_csv(path, fs, eeg_col=None):
    df = pd.read_csv(path)
    cols = {c.lower(): c for c in df.columns}
    if "t_s" not in cols:
        raise ValueError(f"{path}: EEG CSV must contain 't_s'.")

    if eeg_col is None:
        if "eeg" in cols:
            eeg_col = cols["eeg"]
        else:
            numeric = [c for c in df.select_dtypes(include=[np.number]).columns if c.lower() != "t_s"]
            if not numeric:
                raise ValueError(f"{path}: EEG CSV needs a numeric channel.")
            eeg_col = numeric[0]

    t_raw = df[cols["t_s"]].to_numpy().astype(float)
    x_raw = df[eeg_col].to_numpy().astype(float)
    t = np.arange(int(np.floor((t_raw[-1] - t_raw[0]) * fs))) / fs + t_raw[0]
    x = np.interp(t, t_raw, x_raw)
    return t, x - np.mean(x)

def load_reference_csv(path, fs, col=None):
    df = pd.read_csv(path)
    cols = {c.lower(): c for c in df.columns}
    if "t_s" not in cols:
        raise ValueError("Reference CSV must contain 't_s'.")

    if col is None:
        numeric = [c for c in df.select_dtypes(include=[np.number]).columns if c.lower() != "t_s"]
        if not numeric:
            raise ValueError("Reference CSV needs a numeric column for the proxy.")
        col = numeric[0]

    t_raw = df[cols["t_s"]].to_numpy().astype(float)
    x_raw = df[col].to_numpy().astype(float)
    t = np.arange(int(np.floor((t_raw[-1] - t_raw[0]) * fs))) / fs + t_raw[0]
    x = np.interp(t, t_raw, x_raw)
    return t, x - np.mean(x)

# ----------------------- group coherence -----------------------

def kuramoto_R(phases):
    """
    phases: array shape [n_series, T]
    returns: R_t (T,), mean_R, std_R
    """
    z = np.exp(1j * phases)             # [n, T]
    order_vec = np.mean(z, axis=0)      # [T]
    R_t = np.abs(order_vec)             # [0..1]
    return R_t, float(np.mean(R_t)), float(np.std(R_t))

def plv_to_reference(phases, ref_phase):
    """
    phases: [n_series, T]
    ref_phase: [T]
    returns per-series PLV to reference
    """
    plvs = []
    for k in range(phases.shape[0]):
        dphi = np.unwrap(phases[k] - ref_phase)
        plv = np.abs(np.mean(np.exp(1j * dphi)))
        plvs.append(float(plv))
    return plvs

# ----------------------- main -----------------------

def main():
    ap = argparse.ArgumentParser(description="Group coherence (Kuramoto R) for HRV/EEG.")
    ap.add_argument("--files", nargs="+", required=True,
                    help="List/glob of CSVs (participants). Use shell quotes for globs.")
    ap.add_argument("--stream", choices=["hrv", "eeg"], required=True,
                    help="Stream type for all files.")
    ap.add_argument("--fs", type=int, default=256, help="Target Hz for uniform processing.")
    ap.add_argument("--band", nargs=2, type=float, required=True,
                    help="Bandpass range, e.g., 0.04 0.15 (HRV) or 8 12 (EEG).")
    ap.add_argument("--hrv-col", type=str, default=None, help="HRV column name (if time series).")
    ap.add_argument("--eeg-col", type=str, default=None, help="EEG column name.")
    ap.add_argument("--reference-csv", type=str, default=None,
                    help="Optional reference CSV to compute per-series PLV.")
    ap.add_argument("--reference-col", type=str, default=None,
                    help="Column name in reference CSV (optional).")
    ap.add_argument("--outdir", type=str, default="outputs/group")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Expand globs
    file_list = []
    for f in args.files:
        file_list += glob.glob(f)
    file_list = sorted(set(file_list))
    if not file_list:
        raise ValueError("No files matched --files.")

    # Load all series
    fs = args.fs
    low, high = args.band

    t_series = []
    x_series = []
    for path in file_list:
        if args.stream == "hrv":
            t, x = load_hrv_csv(path, fs, hrv_col=args.hrv_col)
        else:
            t, x = load_eeg_csv(path, fs, eeg_col=args.eeg_col)
        t_series.append(t); x_series.append(x)

    # Common time window
    t = unify_time_interval(t_series, fs)

    # Interp, bandpass, phases
    X_bp = []
    for (ti, xi) in zip(t_series, x_series):
        xi_u = resample_linear(ti, xi, t)
        xi_bp = bandpass(xi_u, fs, low, high)
        X_bp.append(xi_bp)
    X_bp = np.vstack(X_bp)             # [n_series, T]
    phases = np.angle(hilbert(X_bp, axis=1))

    # Group synchrony
    R_t, R_mean, R_std = kuramoto_R(phases)

    # Optional reference PLVs
    ref_info = None
    if args.reference_csv:
        tr, xr = load_reference_csv(args.reference_csv, fs, col=args.reference_col)
        xr_u = resample_linear(tr, xr, t)
        xr_bp = bandpass(xr_u, fs, low, high)
        ref_phase = analytic_phase(xr_bp)
        per_series_plv = plv_to_reference(phases, ref_phase)
        ref_info = {
            "reference_csv": args.reference_csv,
            "plv_to_reference": per_series_plv,
            "plv_mean": float(np.mean(per_series_plv)),
            "plv_std": float(np.std(per_series_plv))
        }

    # Spectral snapshot of group mean
    f_mean, P_mean = power_spectrum(np.mean(X_bp, axis=0), fs)

    # Save summary
    summary = {
        "n_series": int(X_bp.shape[0]),
        "fs": fs,
        "band_hz": [low, high],
        "duration_s": float(t[-1] - t[0]),
        "R_mean": R_mean,
        "R_std": R_std,
        "files": file_list,
    }
    if ref_info:
        summary["reference"] = ref_info

    (outdir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"[Group] N={X_bp.shape[0]} | R_mean={R_mean:.3f} ± {R_std:.3f}")

    # Plots
    import matplotlib as mpl
    mpl.rcParams.update({"figure.figsize": (12, 10)})

    # 1) R(t)
    fig1, ax1 = plt.subplots(1, 1)
    ax1.plot(t, R_t)
    ax1.set_ylim(0, 1)
    ax1.set_title(f"Kuramoto Order Parameter R(t) — band {low}-{high} Hz")
    ax1.set_xlabel("Time (s)"); ax1.set_ylabel("R")
    fig1.tight_layout(); fig1.savefig(outdir / "R_time.png", dpi=160); plt.close(fig1)

    # 2) Phase stacks (preview first 20 s)
    n_prev = min(len(t), fs * 20)
    fig2, ax2 = plt.subplots(1, 1)
    for k in range(min(8, X_bp.shape[0])):  # show up to 8 series
        ax2.plot(t[:n_prev], X_bp[k, :n_prev], alpha=0.7)
    ax2.set_title("Bandpassed signals (preview)")
    ax2.set_xlabel("Time (s)")
    fig2.tight_layout(); fig2.savefig(outdir / "bandpassed_preview.png", dpi=160); plt.close(fig2)

    # 3) PSD of group mean
    fig3, ax3 = plt.subplots(1, 1)
    ax3.semilogy(f_mean, P_mean + 1e-12)
    ax3.set_title("PSD of group-mean signal")
    ax3.set_xlabel("Hz")
    fig3.tight_layout(); fig3.savefig(outdir / "group_mean_psd.png", dpi=160); plt.close(fig3)

if __name__ == "__main__":
    main()
