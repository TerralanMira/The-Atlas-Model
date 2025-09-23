#!/usr/bin/env python3
"""
Schumann Coupling (HRV/EEG ↔ Earth Hum)

Purpose
-------
Quantify phase-locking (PLV) between human rhythms and the Schumann fundamental.
- Ingest HRV (RR or HRV series), EEG (any channel), and Schumann f0(t)
- Align to a common timeline, band-limit each stream
- Compute PLV for HRV↔Schumann, EEG↔Schumann, and HRV↔EEG
- Save plots and a JSON summary

CSV formats
-----------
HRV: rr_ms[,t_s]  OR  t_s,<hrv_col>
EEG: t_s,<eeg_col>
SCH: t_s,f0_hz    (fundamental frequency over time)
"""

import argparse, json
from pathlib import Path
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, hilbert, welch

def butter_bandpass(low, high, fs, order=4):
    nyq = 0.5 * fs
    low_n = max(1e-6, low/nyq); high_n = min(0.999999, high/nyq)
    b, a = butter(order, [low_n, high_n], btype="band"); return b, a

def bandpass(x, fs, low, high, order=4):
    b, a = butter_bandpass(low, high, fs, order); return filtfilt(b, a, x)

def power_spectrum(x, fs):
    f, Pxx = welch(x, fs=fs, nperseg=min(len(x), 4096)); return f, Pxx

def plv_from_signals(x, y):
    phase_x = np.angle(hilbert(x)); phase_y = np.angle(hilbert(y))
    dphi = np.unwrap(phase_x - phase_y)
    val = np.abs(np.mean(np.exp(1j * dphi))); return float(np.clip(val, 0.0, 1.0)), dphi

def resample_linear(t_src, x_src, t_tgt): return np.interp(t_tgt, t_src, x_src)

def unify_timeline(t_arrs, fs):
    t0 = max(t[0] for t in t_arrs); t1 = min(t[-1] for t in t_arrs)
    if t1 <= t0: raise ValueError("No temporal overlap across streams.")
    N = int(np.floor((t1 - t0) * fs)); return np.arange(N) / fs + t0

def load_hrv(hrv_csv, fs, hrv_col=None):
    df = pd.read_csv(hrv_csv); cols = {c.lower(): c for c in df.columns}
    if "rr_ms" in cols:
        rr = df[cols["rr_ms"]].to_numpy().astype(float) / 1000.0
        t_beats = df[cols["t_s"]].to_numpy().astype(float) if "t_s" in cols else np.cumsum(rr)
        t_end = t_beats[-1]; N = int(np.floor(t_end * fs)); t = np.arange(N) / fs
        sig = np.interp(t, t_beats, rr, left=rr[0], right=rr[-1]); return t, sig - np.mean(sig)
    if "t_s" not in cols: raise ValueError("HRV needs 'rr_ms' or 't_s'.")
    t_raw = df[cols["t_s"]].to_numpy().astype(float)
    if hrv_col is None:
        guess = [c for c in df.columns if c.lower() in ("hrv","tachogram","rr_s","rr_signal","value")]
        if not guess: raise ValueError("Provide --hrv-col for HRV series.")
        hrv_col = guess[0]
    x_raw = df[hrv_col].to_numpy().astype(float)
    t = np.arange(int(np.floor((t_raw[-1] - t_raw[0]) * fs))) / fs + t_raw[0]
    x = np.interp(t, t_raw, x_raw); return t, x - np.mean(x)

def load_eeg(eeg_csv, fs, eeg_col=None):
    df = pd.read_csv(eeg_csv); cols = {c.lower(): c for c in df.columns}
    if "t_s" not in cols: raise ValueError("EEG needs 't_s'.")
    if eeg_col is None:
        if "eeg" in cols: eeg_col = cols["eeg"]
        else:
            numeric = [c for c in df.select_dtypes(include=[np.number]).columns if c.lower() != "t_s"]
            if not numeric: raise ValueError("EEG needs a numeric channel.")
            eeg_col = numeric[0]
    t_raw = df[cols["t_s"]].to_numpy().astype(float); x_raw = df[eeg_col].to_numpy().astype(float)
    t = np.arange(int(np.floor((t_raw[-1] - t_raw[0]) * fs))) / fs + t_raw[0]
    x = np.interp(t, t_raw, x_raw); return t, x - np.mean(x)

def load_schumann(sch_csv, fs, col_f0="f0_hz"):
    df = pd.read_csv(sch_csv); cols = {c.lower(): c for c in df.columns}
    if "t_s" not in cols: raise ValueError("Schumann needs 't_s'.")
    if col_f0.lower() not in cols:
        candidates = [c for c in df.columns if "f0" in c.lower() and "hz" in c.lower()]
        if not candidates: raise ValueError("Missing fundamental frequency column like 'f0_hz'.")
        col_f0 = candidates[0]
    t_raw = df[cols["t_s"]].to_numpy().astype(float); f0 = df[col_f0].to_numpy().astype(float)
    t = np.arange(int(np.floor((t_raw[-1] - t_raw[0]) * fs))) / fs + t_raw[0]
    f0_u = np.interp(t, t_raw, f0); dt = 1.0 / fs
    phi = 2*np.pi * np.cumsum(f0_u) * dt
    sch = np.sin(phi); return t, sch - np.mean(sch), f0_u

def main():
    ap = argparse.ArgumentParser(description="Schumann coupling with HRV/EEG (real data).")
    ap.add_argument("--hrv-csv", required=True)
    ap.add_argument("--eeg-csv", required=True)
    ap.add_argument("--sch-csv", required=True)
    ap.add_argument("--fs", type=int, default=256)
    ap.add_argument("--hrv-col", type=str, default=None)
    ap.add_argument("--eeg-col", type=str, default=None)
    ap.add_argument("--hrv-band", nargs=2, type=float, default=[0.04, 0.15])
    ap.add_argument("--eeg-band", nargs=2, type=float, default=[8.0, 12.0])
    ap.add_argument("--sch-band", nargs=2, type=float, default=[6.5, 9.0])
    ap.add_argument("--outdir", type=str, default="outputs/health_schumann")
    args = ap.parse_args()

    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)

    t_hrv, x_hrv = load_hrv(args.hrv_csv, args.fs, hrv_col=args.hrv_col)
    t_eeg, x_eeg = load_eeg(args.eeg_csv, args.fs, eeg_col=args.eeg_col)
    t_sch, x_sch, f0_u = load_schumann(args.sch_csv, args.fs)

    # Common timeline
    def unify(t_arrs, fs):
        t0 = max(t[0] for t in t_arrs); t1 = min(t[-1] for t in t_arrs)
        if t1 <= t0: raise ValueError("No overlap across streams.")
        N = int(np.floor((t1 - t0) * fs)); return np.arange(N) / fs + t0
    t = unify([t_hrv, t_eeg, t_sch], args.fs)

    def interp(t_src, x_src): return np.interp(t, t_src, x_src)
    hrv_u, eeg_u, sch_u = interp(t_hrv, x_hrv), interp(t_eeg, x_eeg), interp(t_sch, x_sch)
    fs = args.fs

    # Bandpass
    hrv_bp = bandpass(hrv_u, fs, args.hrv_band[0], args.hrv_band[1])
    eeg_bp = bandpass(eeg_u, fs, args.eeg_band[0], args.eeg_band[1])
    sch_bp = bandpass(sch_u, fs, args.sch_band[0], args.sch_band[1])

    # PLV
    plv_hs, dphi_hs = plv_from_signals(hrv_bp, sch_bp)
    plv_es, dphi_es = plv_from_signals(eeg_bp, sch_bp)
    plv_he, dphi_he = plv_from_signals(hrv_bp, eeg_bp)

    # Spectra
    f_h, P_h = power_spectrum(hrv_bp, fs)
    f_e, P_e = power_spectrum(eeg_bp, fs)
    f_s, P_s = power_spectrum(sch_bp, fs)

    summary = {
        "fs": fs,
        "duration_s": float(t[-1] - t[0]),
        "bands": {"hrv_hz": args.hrv_band, "eeg_hz": args.eeg_band, "sch_hz": args.sch_band},
        "plv": {"hrv_schumann": plv_hs, "eeg_schumann": plv_es, "hrv_eeg": plv_he},
        "schumann_f0_mean_hz": float(np.mean(f0_u)),
        "schumann_f0_std_hz": float(np.std(f0_u))
    }
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(f"[PLV] HRV↔Schumann={plv_hs:.3f} | EEG↔Schumann={plv_es:.3f} | HRV↔EEG={plv_he:.3f}")
    print(f"Saved -> {outdir/'summary.json'}")

    # Plots
    import matplotlib as mpl; mpl.rcParams.update({"figure.figsize": (12, 10)})
    n_prev = min(len(t), fs*30)

    fig, ax = plt.subplots(4, 1, sharex=True)
    ax[0].plot(t[:n_prev], hrv_bp[:n_prev]); ax[0].set_title("HRV (bandpassed)")
    ax[1].plot(t[:n_prev], eeg_bp[:n_prev]); ax[1].set_title("EEG (bandpassed)")
    ax[2].plot(t[:n_prev], sch_bp[:n_prev]); ax[2].set_title("Schumann Proxy (bandpassed)")
    ax[3].plot(t[:n_prev], f0_u[:n_prev]);  ax[3].set_title("Schumann f0(t) [Hz]"); ax[3].set_xlabel("Time (s)")
    fig.tight_layout(); fig.savefig(outdir / "bandpassed_preview.png", dpi=160); plt.close(fig)

    fig2, ax2 = plt.subplots(1,1)
    ax2.semilogy(f_h, P_h + 1e-12, label="HRV PSD")
    ax2.semilogy(f_e, P_e + 1e-12, label="EEG PSD")
    ax2.semilogy(f_s, P_s + 1e-12, label="Schumann PSD")
    ax2.set_xlim(0.01, max(40, args.eeg_band[1]*2))
    ax2.set_title("Power Spectral Density"); ax2.set_xlabel("Hz"); ax2.legend()
    fig2.tight_layout(); fig2.savefig(outdir / "spectra.png", dpi=160); plt.close(fig2)

    wrap = lambda x: (x + np.pi) % (2*np.pi) - np.pi
    fig3, ax3 = plt.subplots(3,1, figsize=(10,10))
    ax3[0].hist(wrap(dphi_hs), bins=72, density=True); ax3[0].set_title(f"ΔPhase HRV↔Schumann (PLV={plv_hs:.3f})")
    ax3[1].hist(wrap(dphi_es), bins=72, density=True); ax3[1].set_title(f"ΔPhase EEG↔Schumann (PLV={plv_es:.3f})")
    ax3[2].hist(wrap(dphi_he), bins=72, density=True); ax3[2].set_title(f"ΔPhase HRV↔EEG (PLV={plv_he:.3f})")
    for a in ax3: a.set_xlabel("rad"); a.set_ylabel("Density")
    fig3.tight_layout(); fig3.savefig(outdir / "phase_histograms.png", dpi=160); plt.close(fig3)

if __name__ == "__main__":
    main()
