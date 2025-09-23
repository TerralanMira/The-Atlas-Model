#!/usr/bin/env python3
"""
Schumann Coupling: HRV/EEG <-> Earth Hum

What it does
------------
- Loads HRV CSV (RR-intervals or time series), EEG CSV (t_s + channel), and Schumann CSV.
- Builds continuous HRV signal, aligns all streams on a common timeline.
- Bandpasses:
   - HRV in LF (default 0.04–0.15 Hz)
   - EEG in alpha (default 8–12 Hz)
   - Schumann fundamental/harmonics around provided center frequencies (default ~7.83 Hz)
- Extracts instantaneous phase (Hilbert) and computes PLV (0..1) for:
   - HRV <-> Schumann
   - EEG <-> Schumann
   - HRV <-> EEG (reference)
- Saves JSON summary + diagnostic plots (signals, spectra, phase histograms)

CSV formats
-----------
HRV:
  - Option A: rr_ms[,t_s]   (RR intervals in milliseconds, optional cumulative time seconds)
  - Option B: t_s,<hrv_col> (time series of a precomputed HRV/tachogram signal)

EEG:
  - t_s,<eeg_col>           (regularly sampled preferred; if not, resampled)

Schumann:
  - t_s,f0_hz[,amp]         (time stamps + fundamental frequency; amp optional)
    OR t_s,f0_hz,f1_hz,f2_hz,... if multiple bands are provided; script uses f0_hz.

Dependencies
------------
pip install numpy scipy pandas matplotlib
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, hilbert, welch

# ----------------------- Filters & helpers -----------------------

def butter_bandpass(low, high, fs, order=4):
    nyq = 0.5 * fs
    low_n = max(1e-6, low/nyq)
    high_n = min(0.999999, high/nyq)
    b, a = butter(order, [low_n, high_n], btype="band")
    return b, a

def bandpass(x, fs, low, high, order=4):
    b, a = butter_bandpass(low, high, fs, order)
    return filtfilt(b, a, x)

def power_spectrum(x, fs):
    f, Pxx = welch(x, fs=fs, nperseg=min(len(x), 4096))
    return f, Pxx

def plv_from_signals(x, y):
    """Phase-locking value between two real signals via Hilbert phases."""
    phase_x = np.angle(hilbert(x))
    phase_y = np.angle(hilbert(y))
    dphi = np.unwrap(phase_x - phase_y)
    val = np.abs(np.mean(np.exp(1j * dphi)))
    return float(np.clip(val, 0.0, 1.0)), dphi

def resample_linear(t_src, x_src, t_tgt):
    return np.interp(t_tgt, t_src, x_src)

def unify_timeline(t_arrs, fs):
    """Build a common time vector covering the overlap across arrays at target fs."""
    starts = [t[0] for t in t_arrs]
    ends   = [t[-1] for t in t_arrs]
    t0 = max(starts)
    t1 = min(ends)
    if t1 <= t0:
        raise ValueError("No temporal overlap across streams.")
    N = int(np.floor((t1 - t0) * fs))
    t = np.arange(N) / fs + t0
    return t

# ----------------------- Data loading -----------------------

def load_hrv(hrv_csv, fs, hrv_col=None):
    """
    Return (t, hrv_signal) uniformly sampled at fs.
    Supports:
      - rr_ms (and optional t_s): builds tachogram then centers.
      - t_s + hrv_col: resamples to fs.
    """
    df = pd.read_csv(hrv_csv)
    cols_l = {c.lower(): c for c in df.columns}

    if "rr_ms" in cols_l:
        rr = df[cols_l["rr_ms"]].to_numpy().astype(float) / 1000.0  # s
        if "t_s" in cols_l:
            t_beats = df[cols_l["t_s"]].to_numpy().astype(float)
        else:
            t_beats = np.cumsum(rr)
        t_end = t_beats[-1]
        N = int(np.floor(t_end * fs))
        t = np.arange(N) / fs
        # Step-hold RR across interval
        hrv_sig = np.interp(t, t_beats, rr, left=rr[0], right=rr[-1])
        hrv_sig = hrv_sig - np.mean(hrv_sig)
        return t, hrv_sig

    # time series path
    if "t_s" not in cols_l:
        raise ValueError("HRV CSV must contain 'rr_ms' or a time column 't_s'.")
    t_raw = df[cols_l["t_s"]].to_numpy().astype(float)
    if hrv_col is None:
        guesses = [c for c in df.columns if c.lower() in ("hrv","tachogram","rr_s","rr_signal","value")]
        if not guesses:
            raise ValueError("Provide --hrv-col to select HRV signal column.")
        hrv_col = guesses[0]
    x_raw = df[hrv_col].to_numpy().astype(float)
    # resample to uniform fs
    t = np.arange(int(np.floor((t_raw[-1] - t_raw[0]) * fs))) / fs + t_raw[0]
    x = np.interp(t, t_raw, x_raw)
    x = x - np.mean(x)
    return t, x

def load_eeg(eeg_csv, fs, eeg_col=None):
    df = pd.read_csv(eeg_csv)
    cols_l = {c.lower(): c for c in df.columns}
    if "t_s" not in cols_l:
        raise ValueError("EEG CSV must have 't_s' in seconds.")
    if eeg_col is None:
        if "eeg" in cols_l:
            eeg_col = cols_l["eeg"]
        else:
            # pick first numeric non-time column
            numeric = [c for c in df.select_dtypes(include=[np.number]).columns if c.lower() != "t_s"]
            if not numeric:
                raise ValueError("EEG CSV needs at least one numeric channel.")
            eeg_col = numeric[0]
    t_raw = df[cols_l["t_s"]].to_numpy().astype(float)
    x_raw = df[eeg_col].to_numpy().astype(float)
    t = np.arange(int(np.floor((t_raw[-1] - t_raw[0]) * fs))) / fs + t_raw[0]
    x = np.interp(t, t_raw, x_raw)
    x = x - np.mean(x)
    return t, x

def load_schumann(sch_csv, fs, col_f0="f0_hz"):
    """
    Schumann CSV expected columns:
      - t_s
      - f0_hz (center frequency of fundamental; can vary over time)
      - optional amp or other columns (ignored here)
    We synthesize a narrowband sinusoid at instantaneous f0, then band-limit later.
    """
    df = pd.read_csv(sch_csv)
    cols_l = {c.lower(): c for c in df.columns}
    if "t_s" not in cols_l:
        raise ValueError("Schumann CSV must contain 't_s'.")
    if col_f0.lower() not in cols_l:
        # try a forgiving guess
        guesses = [c for c in df.columns if "f0" in c.lower() and "hz" in c.lower()]
        if not guesses:
            raise ValueError("Schumann CSV must include fundamental frequency column like 'f0_hz'.")
        col_f0 = guesses[0]
    t_raw = df[cols_l["t_s"]].to_numpy().astype(float)
    f0 = df[col_f0].to_numpy().astype(float)

    # Resample f0 to uniform timeline, then integrate to phase for a sinusoid
    t = np.arange(int(np.floor((t_raw[-1] - t_raw[0]) * fs))) / fs + t_raw[0]
    f0_u = np.interp(t, t_raw, f0)
    # instantaneous phase from frequency: phi(t) = 2pi * integral f(t) dt
    dt = 1.0 / fs
    phi = 2*np.pi * np.cumsum(f0_u) * dt
    sch = np.sin(phi)
    sch = sch - np.mean(sch)
    return t, sch, f0_u

# ----------------------- Main analysis -----------------------

def main():
    ap = argparse.ArgumentParser(description="Schumann coupling with HRV/EEG (real data).")
    ap.add_argument("--hrv-csv", required=True, help="HRV CSV (rr_ms OR t_s+hrv_col).")
    ap.add_argument("--eeg-csv", required=True, help="EEG CSV (t_s + channel).")
    ap.add_argument("--sch-csv", required=True, help="Schumann CSV (t_s + f0_hz).")
    ap.add_argument("--fs", type=int, default=256, help="Target sampling rate (Hz).")
    ap.add_argument("--hrv-col", type=str, default=None, help="HRV column if not rr_ms.")
    ap.add_argument("--eeg-col", type=str, default=None, help="EEG channel column.")
    ap.add_argument("--hrv-band", nargs=2, type=float, default=[0.04, 0.15], help="HRV LF band (Hz).")
    ap.add_argument("--eeg-band", nargs=2, type=float, default=[8.0, 12.0], help="EEG band (Hz), default alpha.")
    ap.add_argument("--sch-band", nargs=2, type=float, default=[6.5, 9.0], help="Schumann band around f0 (Hz).")
    ap.add_argument("--outdir", type=str, default="outputs/health_schumann", help="Output directory.")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Load streams
    t_hrv, hrv_sig = load_hrv(args.hrv_csv, args.fs, hrv_col=args.hrv_col)
    t_eeg, eeg_sig = load_eeg(args.eeg_csv, args.fs, eeg_col=args.eeg_col)
    t_sch, sch_raw, f0_u = load_schumann(args.sch_csv, args.fs)

    # Common timeline
    t_common = unify_timeline([t_hrv, t_eeg, t_sch], args.fs)
    hrv_u = resample_linear(t_hrv, hrv_sig, t_common)
    eeg_u = resample_linear(t_eeg, eeg_sig, t_common)
    sch_u = resample_linear(t_sch, sch_raw, t_common)

    fs = args.fs

    # Bandpass
    hrv_bp = bandpass(hrv_u, fs, args.hrv_band[0], args.hrv_band[1])
    eeg_bp = bandpass(eeg_u, fs, args.eeg_band[0], args.eeg_band[1])
    sch_bp = bandpass(sch_u, fs, args.sch_band[0], args.sch_band[1])

    # PLVs
    plv_hrv_sch, dphi_hs = plv_from_signals(hrv_bp, sch_bp)
    plv_eeg_sch, dphi_es = plv_from_signals(eeg_bp, sch_bp)
    plv_hrv_eeg, dphi_he = plv_from_signals(hrv_bp, eeg_bp)

    # Spectra
    f_h, P_h = power_spectrum(hrv_bp, fs)
    f_e, P_e = power_spectrum(eeg_bp, fs)
    f_s, P_s = power_spectrum(sch_bp, fs)

    # Summary JSON
    summary = {
        "fs": fs,
        "duration_s": float(t_common[-1] - t_common[0]),
        "bands": {
            "hrv_hz": args.hrv_band,
            "eeg_hz": args.eeg_band,
            "sch_hz": args.sch_band
        },
        "plv": {
            "hrv_schumann": plv_hrv_sch,
            "eeg_schumann": plv_eeg_sch,
            "hrv_eeg": plv_hrv_eeg
        },
        "schumann_f0_mean_hz": float(np.mean(f0_u)),
        "schumann_f0_std_hz": float(np.std(f0_u))
    }
    with open(outdir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"[PLV] HRV↔Schumann: {plv_hrv_sch:.3f} | EEG↔Schumann: {plv_eeg_sch:.3f} | HRV↔EEG: {plv_hrv_eeg:.3f}")
    print(f"Saved summary -> {outdir/'summary.json'}")

    # ----------- Plots -----------
    # 1) Bandpassed preview
    import matplotlib as mpl
    mpl.rcParams.update({"figure.figsize": (12, 10)})

    n_prev = min(len(t_common), fs * 30)  # first 30 s
    fig, axes = plt.subplots(4, 1, sharex=True)
    axes[0].plot(t_common[:n_prev], hrv_bp[:n_prev])
    axes[0].set_title("HRV (bandpassed)")
    axes[1].plot(t_common[:n_prev], eeg_bp[:n_prev])
    axes[1].set_title("EEG (bandpassed)")
    axes[2].plot(t_common[:n_prev], sch_bp[:n_prev])
    axes[2].set_title("Schumann Proxy (bandpassed)")
    axes[3].plot(t_common[:n_prev], f0_u[:n_prev])
    axes[3].set_title("Schumann f0(t) [Hz]")
    axes[3].set_xlabel("Time (s)")
    plt.tight_layout()
    fig.savefig(outdir / "bandpassed_preview.png", dpi=160)
    plt.close(fig)

    # 2) Spectra
    fig2, ax2 = plt.subplots(1, 1)
    ax2.semilogy(f_h, P_h + 1e-12, label="HRV PSD")
    ax2.semilogy(f_e, P_e + 1e-12, label="EEG PSD")
    ax2.semilogy(f_s, P_s + 1e-12, label="Schumann PSD")
    ax2.set_xlim(0.01, max(40, args.eeg_band[1]*2))
    ax2.set_title("Power Spectral Density")
    ax2.set_xlabel("Hz")
    ax2.legend()
    fig2.tight_layout()
    fig2.savefig(outdir / "spectra.png", dpi=160)
    plt.close(fig2)

    # 3) Phase histograms
    def wrap_pi(x): return (x + np.pi) % (2*np.pi) - np.pi
    fig3, axes3 = plt.subplots(3, 1, figsize=(10, 10))
    axes3[0].hist(wrap_pi(dphi_hs), bins=72, density=True)
    axes3[0].set_title(f"Phase Diff: HRV↔Schumann (PLV={plv_hrv_sch:.3f})")
    axes3[1].hist(wrap_pi(dphi_es), bins=72, density=True)
    axes3[1].set_title(f"Phase Diff: EEG↔Schumann (PLV={plv_eeg_sch:.3f})")
    axes3[2].hist(wrap_pi(dphi_he), bins=72, density=True)
    axes3[2].set_title(f"Phase Diff: HRV↔EEG (PLV={plv_hrv_eeg:.3f})")
    for ax in axes3: ax.set_xlabel("Δphase (rad)"); ax.set_ylabel("Density")
    fig3.tight_layout()
    fig3.savefig(outdir / "phase_histograms.png", dpi=160)
    plt.close(fig3)

if __name__ == "__main__":
    main()
