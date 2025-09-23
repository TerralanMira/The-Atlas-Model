#!/usr/bin/env python3
"""
Heart–Brain Coherence

Purpose
-------
Compute a testable phase-locking coherence (PLV) between HRV and EEG using real CSV inputs.
- Builds a continuous HRV signal (from RR intervals or HRV time series)
- Band-passes HRV (LF 0.04–0.15 Hz) and EEG (default alpha 8–12 Hz)
- Extracts instantaneous phase (Hilbert) and computes PLV (0..1)
- Saves plots and a JSON summary

CSV formats
-----------
HRV:
  A) rr_ms[,t_s]            # RR intervals in ms, optional cumulative time (s)
  B) t_s,<hrv_col>          # irregular/regular HRV series with timestamps

EEG:
  t_s,<eeg_col>             # regularly sampled preferred; if not, resampled

Usage
-----
python simulations/health/heart_brain_coherence.py \
  --hrv-csv data/hrv_rr.csv \
  --eeg-csv data/eeg_alpha.csv \
  --fs 256 \
  --outdir outputs/health_hbc
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, hilbert, welch

def butter_bandpass(low, high, fs, order=4):
    nyq = 0.5 * fs
    b, a = butter(order, [low/nyq, high/nyq], btype="band")
    return b, a

def bandpass(x, fs, low, high, order=4):
    b, a = butter_bandpass(low, high, fs, order)
    return filtfilt(b, a, x)

def plv(signal1, signal2):
    phase1 = np.angle(hilbert(signal1))
    phase2 = np.angle(hilbert(signal2))
    dphi = np.unwrap(phase1 - phase2)
    val = np.abs(np.mean(np.exp(1j * dphi)))
    return float(np.clip(val, 0.0, 1.0)), dphi

def power_spectrum(x, fs):
    f, Pxx = welch(x, fs=fs, nperseg=min(len(x), 4096))
    return f, Pxx

def load_hrv_as_signal(hrv_path, fs, hrv_col=None):
    df = pd.read_csv(hrv_path)
    cols = {c.lower(): c for c in df.columns}

    if "rr_ms" in cols:
        rr = df[cols["rr_ms"]].to_numpy().astype(float) / 1000.0
        if "t_s" in cols:
            t_beats = df[cols["t_s"]].to_numpy().astype(float)
        else:
            t_beats = np.cumsum(rr)
        t_end = t_beats[-1]
        N = int(np.floor(t_end * fs))
        t = np.arange(N) / fs
        hrv_sig = np.interp(t, t_beats, rr, left=rr[0], right=rr[-1])
        hrv_sig = hrv_sig - np.mean(hrv_sig)
        return t, hrv_sig

    if "t_s" not in cols:
        raise ValueError("HRV CSV must contain 'rr_ms' or 't_s'.")
    t_raw = df[cols["t_s"]].to_numpy().astype(float)

    if hrv_col is None:
        guess = [c for c in df.columns if c.lower() in ("hrv","tachogram","rr_s","rr_signal","value")]
        if not guess: raise ValueError("Provide --hrv-col for HRV series.")
        hrv_col = guess[0]
    x_raw = df[hrv_col].to_numpy().astype(float)

    duration = t_raw[-1] - t_raw[0]
    N = int(np.floor(duration * fs))
    t = np.arange(N) / fs + t_raw[0]
    x = np.interp(t, t_raw, x_raw)
    x = x - np.mean(x)
    return t, x

def load_eeg(eeg_path, fs, eeg_col=None):
    df = pd.read_csv(eeg_path)
    cols = {c.lower(): c for c in df.columns}
    if "t_s" not in cols:
        raise ValueError("EEG CSV must have 't_s' (seconds).")

    if eeg_col is None:
        if "eeg" in cols: eeg_col = cols["eeg"]
        else:
            numeric = [c for c in df.select_dtypes(include=[np.number]).columns if c.lower() != "t_s"]
            if not numeric: raise ValueError("EEG CSV needs a numeric channel.")
            eeg_col = numeric[0]

    t_raw = df[cols["t_s"]].to_numpy().astype(float)
    x_raw = df[eeg_col].to_numpy().astype(float)

    dt = np.median(np.diff(t_raw))
    fs_raw = 1.0/dt if dt > 0 else fs
    if abs(fs_raw - fs)/fs > 0.01:
        duration = t_raw[-1] - t_raw[0]
        N = int(np.floor(duration * fs))
        t = np.arange(N) / fs + t_raw[0]
        x = np.interp(t, t_raw, x_raw)
    else:
        t, x = t_raw, x_raw
    x = x - np.mean(x)
    return t, x

def align_lengths(t1, x1, t2, x2):
    t0 = max(t1[0], t2[0])
    t1_end = min(t1[-1], t2[-1])
    if t1_end <= t0: raise ValueError("No time overlap between HRV and EEG.")
    fs1 = 1.0/np.median(np.diff(t1))
    fs2 = 1.0/np.median(np.diff(t2))
    fs = int(round(min(fs1, fs2)))
    N = int(np.floor((t1_end - t0) * fs))
    t = np.arange(N) / fs + t0
    x1i = np.interp(t, t1, x1)
    x2i = np.interp(t, t2, x2)
    return fs, t, x1i, x2i

def main():
    ap = argparse.ArgumentParser(description="Heart–Brain coherence with real CSV data.")
    ap.add_argument("--hrv-csv", required=True)
    ap.add_argument("--eeg-csv", required=True)
    ap.add_argument("--fs", type=int, default=256)
    ap.add_argument("--hrv-col", type=str, default=None)
    ap.add_argument("--eeg-col", type=str, default=None)
    ap.add_argument("--hrv-band", nargs=2, type=float, default=[0.04, 0.15])
    ap.add_argument("--eeg-band", nargs=2, type=float, default=[8.0, 12.0])
    ap.add_argument("--outdir", type=str, default="outputs/health_hbc")
    args = ap.parse_args()

    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)

    t_hrv, hrv_sig = load_hrv_as_signal(args.hrv_csv, args.fs, hrv_col=args.hrv_col)
    t_eeg, eeg_sig = load_eeg(args.eeg_csv, args.fs, eeg_col=args.eeg_col)

    fs, t, hrv_u, eeg_u = align_lengths(t_hrv, hrv_sig, t_eeg, eeg_sig)

    hrv_bp = bandpass(hrv_u, fs, args.hrv_band[0], args.hrv_band[1])
    eeg_bp = bandpass(eeg_u, fs, args.eeg_band[0], args.eeg_band[1])

    coh, dphi = plv(hrv_bp, eeg_bp)

    f_hrv, P_hrv = power_spectrum(hrv_bp, fs)
    f_eeg, P_eeg = power_spectrum(eeg_bp, fs)

    summary = {
        "fs": fs,
        "duration_s": float(t[-1] - t[0]),
        "hrv_band_hz": args.hrv_band,
        "eeg_band_hz": args.eeg_band,
        "coherence_plv": coh
    }
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"[Heart–Brain Coherence] PLV={coh:.3f} | HRV {args.hrv_band} Hz | EEG {args.eeg_band} Hz")

    # Plots
    import matplotlib as mpl
    mpl.rcParams.update({"figure.figsize": (12, 8)})
    n_prev = min(len(t), fs*30)

    fig, axes = plt.subplots(3, 1)
    axes[0].plot(t[:n_prev], hrv_bp[:n_prev], label="HRV (bp)")
    axes[0].plot(t[:n_prev], eeg_bp[:n_prev], label="EEG (bp)")
    axes[0].set_title("Bandpassed Signals (preview)"); axes[0].legend()

    axes[1].semilogy(f_hrv, P_hrv + 1e-12, label="HRV PSD")
    axes[1].semilogy(f_eeg, P_eeg + 1e-12, label="EEG PSD")
    axes[1].set_xlim(0.01, max(40, args.eeg_band[1]*2))
    axes[1].set_title("Power Spectral Density"); axes[1].legend()

    dphi_wrapped = (dphi + np.pi) % (2*np.pi) - np.pi
    axes[2].hist(dphi_wrapped, bins=60, density=True)
    axes[2].set_title(f"Phase Difference (PLV={coh:.3f})"); axes[2].set_xlabel("rad")

    plt.tight_layout()
    plt.savefig(outdir / "coherence_report.png", dpi=160); plt.close()

if __name__ == "__main__":
    main()
