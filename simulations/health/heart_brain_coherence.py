#!/usr/bin/env python3
"""
Heart–Brain Coherence (real data, no pseudo)

What it does
------------
- Loads HRV (RR-intervals) CSV and EEG CSV.
- Builds continuous HRV signal from RR-intervals (tachogram -> resampled).
- Bandpasses: HRV in LF (0.04–0.15 Hz), EEG in alpha (8–12 Hz) by default.
- Extracts instantaneous phase via Hilbert transform.
- Computes Phase-Locking Value (PLV) as a 0–1 coherence index.
- Saves:
  - console summary
  - plots (signals + spectra + phase difference)
  - JSON with metrics

Expected CSV formats
--------------------
HRV CSV: (pick one of these)
  A) rr_ms:        a column with RR intervals in milliseconds (one row per beat)
     Optional: t_s a column of cumulative time in seconds for each RR (otherwise inferred)
  B) t_s, hrv:     a regularly or irregularly sampled “hrv” signal with timestamps in seconds

EEG CSV:
  - t_s:           timestamps in seconds (regularly sampled)
  - eeg:           EEG amplitude (single channel) OR specify --eeg-col for a different column

Examples
--------
python simulations/health/heart_brain_coherence.py \
  --hrv-csv data/hrv_rr.csv \
  --eeg-csv data/eeg_alpha.csv \
  --fs 256 \
  --outdir outputs/health_hbc

python simulations/health/heart_brain_coherence.py \
  --hrv-csv data/hrv_signal.csv --hrv-col hrv \
  --eeg-csv data/eeg.csv --eeg-col Cz --fs 512 --eeg-band 8 12

Dependencies
------------
pip install numpy scipy pandas matplotlib

Notes
-----
- PLV is computed between HRV(LF) phase and EEG(alpha) phase (cross-frequency coupling).
- If your EEG is multi-channel, pick a column with --eeg-col.
"""

import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, hilbert, welch, resample

def butter_bandpass(low, high, fs, order=4):
    nyq = 0.5 * fs
    b, a = butter(order, [low/nyq, high/nyq], btype="band")
    return b, a

def bandpass(x, fs, low, high, order=4):
    b, a = butter_bandpass(low, high, fs, order)
    return filtfilt(b, a, x)

def plv(signal1, signal2):
    """Phase-Locking Value between two analytic-phase signals."""
    phase1 = np.angle(hilbert(signal1))
    phase2 = np.angle(hilbert(signal2))
    dphi = np.unwrap(phase1 - phase2)
    val = np.abs(np.mean(np.exp(1j * dphi)))
    return float(np.clip(val, 0.0, 1.0)), dphi

def load_hrv_as_signal(hrv_path, fs, hrv_col=None):
    """
    Returns: t (seconds), hrv_signal (float array, length N at fs)
    Supports:
      - rr_ms (with optional t_s)
      - or a column hrv (with t_s)
    """
    df = pd.read_csv(hrv_path)
    cols = set(c.lower() for c in df.columns)

    if "rr_ms" in cols:
        # Build tachogram from RR-intervals
        rr = df[[c for c in df.columns if c.lower() == "rr_ms"][0]].to_numpy().astype(float) / 1000.0  # seconds
        if "t_s" in cols:
            t_beats = df[[c for c in df.columns if c.lower() == "t_s"][0]].to_numpy().astype(float)
        else:
            # cumulative time across beats
            t_beats = np.cumsum(rr)
        # Tachogram: assign RR values at beat times, then resample to uniform grid
        t_end = t_beats[-1]
        N = int(np.floor(t_end * fs))
        t = np.arange(N) / fs
        # Step-hold RR across intervals
        hrv_sig = np.interp(t, t_beats, rr, left=rr[0], right=rr[-1])
        # Detrend (optional): center
        hrv_sig = hrv_sig - np.mean(hrv_sig)
        return t, hrv_sig

    # Otherwise expect a time series with t_s and a value column
    t_col = [c for c in df.columns if c.lower() == "t_s"]
    if not t_col:
        raise ValueError("HRV CSV must contain either 'rr_ms' or time column 't_s'.")
    t_raw = df[t_col[0]].to_numpy().astype(float)

    if hrv_col is None:
        guess = [c for c in df.columns if c.lower() in ("hrv", "tachogram", "rr_s", "rr_signal")]
        if not guess:
            raise ValueError("Provide --hrv-col to select which HRV signal column to use.")
        hrv_col = guess[0]
    x_raw = df[hrv_col].to_numpy().astype(float)

    # Resample to uniform fs (handles irregular sampling)
    duration = t_raw[-1] - t_raw[0]
    N = int(np.floor(duration * fs))
    t = np.arange(N) / fs + t_raw[0]
    x = np.interp(t, t_raw, x_raw)
    x = x - np.mean(x)
    return t, x

def load_eeg(eeg_path, fs, eeg_col=None):
    """
    Returns: t (seconds), eeg (float array, length N at fs)
    Requires t_s column and an EEG column (default 'eeg' or provided via --eeg-col).
    If EEG is not at target fs, resample.
    """
    df = pd.read_csv(eeg_path)
    if "t_s" not in [c.lower() for c in df.columns]:
        # try to find case-insensitive match
        cand = [c for c in df.columns if c.lower() == "t_s"]
        if cand:
            df = df.rename(columns={cand[0]: "t_s"})
        else:
            raise ValueError("EEG CSV must have a 't_s' column (seconds).")

    if eeg_col is None:
        # pick 'eeg' if present, else first non-time numeric column
        if "eeg" in [c.lower() for c in df.columns]:
            eeg_col = [c for c in df.columns if c.lower() == "eeg"][0]
        else:
            numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c.lower() != "t_s"]
            if not numeric_cols:
                raise ValueError("EEG CSV must contain at least one numeric channel.")
            eeg_col = numeric_cols[0]

    t_raw = df["t_s"].to_numpy().astype(float)
    x_raw = df[eeg_col].to_numpy().astype(float)

    # infer raw fs and resample to target fs if needed
    if len(t_raw) < 2:
        raise ValueError("EEG CSV has too few samples.")
    dt = np.median(np.diff(t_raw))
    fs_raw = 1.0 / dt if dt > 0 else fs
    if abs(fs_raw - fs) / fs > 0.01:  # resample if >1% mismatch
        duration = t_raw[-1] - t_raw[0]
        N = int(np.floor(duration * fs))
        t = np.arange(N) / fs + t_raw[0]
        x = np.interp(t, t_raw, x_raw)
    else:
        t, x = t_raw, x_raw
    x = x - np.mean(x)
    return t, x

def power_spectrum(x, fs):
    f, Pxx = welch(x, fs=fs, nperseg=min(len(x), 4096))
    return f, Pxx

def align_lengths(t1, x1, t2, x2):
    t0 = max(t1[0], t2[0])
    t1_end = min(t1[-1], t2[-1])
    if t1_end <= t0:
        raise ValueError("No overlap between HRV and EEG time ranges.")
    fs1 = 1.0 / np.median(np.diff(t1))
    fs2 = 1.0 / np.median(np.diff(t2))
    fs = int(round(min(fs1, fs2)))
    N = int(np.floor((t1_end - t0) * fs))
    t = np.arange(N) / fs + t0
    x1i = np.interp(t, t1, x1)
    x2i = np.interp(t, t2, x2)
    return fs, t, x1i, x2i

def main():
    ap = argparse.ArgumentParser(description="Heart–Brain Coherence on real CSV data.")
    ap.add_argument("--hrv-csv", required=True, help="Path to HRV CSV (rr_ms or t_s+hrv).")
    ap.add_argument("--eeg-csv", required=True, help="Path to EEG CSV (t_s + eeg column).")
    ap.add_argument("--fs", type=int, default=256, help="Target sampling rate (Hz).")
    ap.add_argument("--hrv-col", type=str, default=None, help="Name of HRV signal column if not using rr_ms.")
    ap.add_argument("--eeg-col", type=str, default=None, help="Name of EEG channel column (default auto).")
    ap.add_argument("--hrv-band", nargs=2, type=float, default=[0.04, 0.15], help="HRV bandpass (Hz).")
    ap.add_argument("--eeg-band", nargs=2, type=float, default=[8.0, 12.0], help="EEG bandpass (Hz).")
    ap.add_argument("--outdir", type=str, default="outputs/health_hbc", help="Output directory.")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Load streams
    t_hrv, hrv_sig = load_hrv_as_signal(args.hrv_csv, args.fs, hrv_col=args.hrv_col)
    t_eeg, eeg_sig = load_eeg(args.eeg_csv, args.fs, eeg_col=args.eeg_col)

    # Align lengths and unify sampling rate
    fs, t, hrv_u, eeg_u = align_lengths(t_hrv, hrv_sig, t_eeg, eeg_sig)

    # Bandpass both streams
    hrv_bp = bandpass(hrv_u, fs, args.hrv_band[0], args.hrv_band[1])
    eeg_bp = bandpass(eeg_u, fs, args.eeg_band[0], args.eeg_band[1])

    # Compute PLV
    coherence, dphi = plv(hrv_bp, eeg_bp)

    # Spectra (for plots)
    f_hrv, P_hrv = power_spectrum(hrv_bp, fs)
    f_eeg, P_eeg = power_spectrum(eeg_bp, fs)

    # Save JSON summary
    summary = {
        "fs": fs,
        "duration_s": float(t[-1] - t[0]),
        "hrv_band_hz": args.hrv_band,
        "eeg_band_hz": args.eeg_band,
        "coherence_plv": coherence
    }
    with open(outdir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    # Print console result
    print(f"[Heart–Brain Coherence] PLV={coherence:.3f} | HRV band {args.hrv_band} Hz | EEG band {args.eeg_band} Hz")
    print(f"Saved summary -> {outdir/'summary.json'}")

    # Plots
    plt.figure(figsize=(12, 8))

    # Time series (short window preview to keep plot readable)
    n_preview = min(len(t), fs * 30)  # preview first 30s
    ax1 = plt.subplot(3, 1, 1)
    ax1.plot(t[:n_preview], hrv_bp[:n_preview], label="HRV (bandpassed)")
    ax1.plot(t[:n_preview], eeg_bp[:n_preview], label="EEG (bandpassed)")
    ax1.set_title("Bandpassed Signals (preview)")
    ax1.set_xlabel("Time (s)")
    ax1.legend(loc="upper right")

    # Spectra
    ax2 = plt.subplot(3, 1, 2)
    ax2.semilogy(f_hrv, P_hrv + 1e-12, label="HRV PSD")
    ax2.semilogy(f_eeg, P_eeg + 1e-12, label="EEG PSD")
    ax2.set_xlim(0.01, max(40, args.eeg_band[1] * 2))
    ax2.set_title("Power Spectral Density")
    ax2.set_xlabel("Frequency (Hz)")
    ax2.legend(loc="upper right")

    # Phase difference histogram
    ax3 = plt.subplot(3, 1, 3)
    # Wrap phase difference to [-pi, pi]
    dphi_wrapped = (dphi + np.pi) % (2 * np.pi) - np.pi
    ax3.hist(dphi_wrapped, bins=60, density=True)
    ax3.set_title(f"Phase Difference Distribution (PLV={coherence:.3f})")
    ax3.set_xlabel("Phase diff (rad)")
    ax3.set_ylabel("Density")

    plt.tight_layout()
    plot_path = outdir / "coherence_report.png"
    plt.savefig(plot_path, dpi=160)
    plt.close()
    print(f"Saved plot -> {plot_path}")

if __name__ == "__main__":
    main()
	data/hrv_rr.csv
rr_ms
820
790
805
795
810
...
data/eeg_alpha.csv
t_s,eeg
0.000,0.0021
0.004,-0.0017
0.008,0.0030
...
