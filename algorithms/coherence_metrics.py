"""
The Atlas Model — Coherence Metrics
===================================

Hum → Code: measure, don't guess.

This module computes time-resolved coherence metrics for oscillator fields
(simulations or real recordings). It takes as input a phase history
T×N (time × nodes) in radians ([-pi, pi]) and optionally a driver
phase series, then emits:

• R(t): Kuramoto order parameter (0–1)
• psi(t): mean phase
• |gap|(t): wrapped distance between psi(t) and driver(t)  [optional]
• anchor_fraction(t): fraction of nodes locked within eps of psi
• global PLV: mean phase-locking value across nodes (over time window)
• trends (slopes) over sliding windows

It can be used as a library or via CLI.

Minimal deps: numpy (pandas optional for CSV convenience).

Examples
--------
# From a NumPy .npy file containing phases_hist of shape (T, N)
python algorithms/coherence_metrics.py --input logs/phases.npy --outdir artifacts/coherence

# From CSV with columns: t, node_0, node_1, ..., node_{N-1}
python algorithms/coherence_metrics.py --input logs/phases.csv --format csv --outdir artifacts/coherence

# With a driver phase series CSV (columns: t, driver_phase)
python algorithms/coherence_metrics.py --input logs/phases.npy --driver logs/driver.csv

Outputs
-------
outdir/
  metrics_timeseries.csv  # t, R, psi, gap_abs(optional), anchor_fraction
  summary.json            # key metrics + trend slopes + final values

Truth-only: this file *measures* coherence; it never asserts emergence.
(Use creation_protocols.evaluate_gates for “creation” claims.)
"""

from __future__ import annotations
import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np

# ----------------- angle utils ----------------- #

def wrap_angle(x: np.ndarray) -> np.ndarray:
    """Wrap angles to [-pi, pi] elementwise."""
    return (x + np.pi) % (2 * np.pi) - np.pi

def order_parameter(phases: np.ndarray) -> Tuple[float, float]:
    """
    Kuramoto order parameter for a 1D phase vector.
    Returns (R, psi) where R ∈ [0,1], psi ∈ [-pi, pi].
    """
    z = np.exp(1j * phases)
    mean = z.mean()
    R = np.abs(mean)
    psi = np.angle(mean)
    return float(R), float(psi)

# ----------------- metrics core ----------------- #

@dataclass
class MetricsConfig:
    anchor_eps: float = 0.35   # rad threshold for lock
    anchor_window: int = 1     # consecutive timepoints required (1 = instantaneous)
    trend_window: int = 400    # samples used for slope estimation
    compute_plv: bool = True   # compute global PLV over whole record

def compute_timeseries(
    phases_hist: np.ndarray,
    driver_phase: Optional[np.ndarray] = None,
    cfg: MetricsConfig = MetricsConfig()
) -> Dict[str, np.ndarray]:
    """
    Compute time-resolved metrics.
    phases_hist: (T, N) angles in radians in [-pi, pi]
    driver_phase: optional (T,) in radians
    Returns dict of arrays (length T): R, psi, anchor_fraction, (gap_abs optional)
    """
    T, N = phases_hist.shape
    R = np.zeros(T, dtype=float)
    psi = np.zeros(T, dtype=float)
    anchor_fraction = np.zeros(T, dtype=float)
    gap_abs = np.zeros(T, dtype=float) if driver_phase is not None else None

    # rolling lock memory if window > 1
    if cfg.anchor_window > 1:
        # circular diff to current psi computed below; we track last W states
        lock_buffer = np.zeros((cfg.anchor_window, N), dtype=bool)
        buf_i = 0

    for t in range(T):
        Rt, psit = order_parameter(phases_hist[t])
        R[t] = Rt
        psi[t] = psit

        diffs = wrap_angle(phases_hist[t] - psit)  # (N,)
        inst_lock = (np.abs(diffs) <= cfg.anchor_eps)

        if cfg.anchor_window == 1:
            anchor_fraction[t] = inst_lock.mean()
        else:
            lock_buffer[buf_i] = inst_lock
            buf_i = (buf_i + 1) % cfg.anchor_window
            # node is "locked" if locked for the entire window
            locked_all = lock_buffer.all(axis=0)
            anchor_fraction[t] = locked_all.mean()

        if driver_phase is not None:
            gap_abs[t] = abs(float(wrap_angle(np.array([psit - float(driver_phase[t])]))[0]))

    out = {"R": R, "psi": psi, "anchor_fraction": anchor_fraction}
    if gap_abs is not None:
        out["gap_abs"] = gap_abs
    return out

def poly_slope(y: np.ndarray, w: int) -> Optional[float]:
    """Least-squares slope over the last w samples. Returns None if insufficient length."""
    if w < 2 or len(y) < w:
        return None
    x = np.arange(w, dtype=float)
    m, _ = np.polyfit(x, y[-w:], 1)
    return float(m)

def compute_plv_global(phases_hist: np.ndarray) -> float:
    """
    Global PLV across nodes, aggregated over time.
    For each node i, PLV_i = |mean_t exp(j*theta_i(t))|.
    We report mean(PLV_i) over nodes as a stable scalar [0,1].
    """
    T, N = phases_hist.shape
    plv_nodes = np.abs(np.exp(1j * phases_hist).mean(axis=0))  # (N,)
    return float(plv_nodes.mean())

def summarize_metrics(ts: Dict[str, np.ndarray], cfg: MetricsConfig) -> Dict:
    """
    Produce summary dict with slopes, means, finals, and PLV (if requested).
    """
    R = ts["R"]
    psi = ts["psi"]
    anchor = ts["anchor_fraction"]
    gap = ts.get("gap_abs", None)

    summary = {
        "final": {
            "R": float(R[-1]) if len(R) else None,
            "anchor_fraction": float(anchor[-1]) if len(anchor) else None,
            "gap_abs": float(gap[-1]) if (gap is not None and len(gap)) else None,
        },
        "mean": {
            "R": float(R.mean()) if len(R) else None,
            "anchor_fraction": float(anchor.mean()) if len(anchor) else None,
            "gap_abs": float(gap.mean()) if (gap is not None and len(gap)) else None,
        },
        "slope": {
            "R": poly_slope(R, cfg.trend_window),
            "gap_abs": poly_slope(gap, cfg.trend_window) if gap is not None else None,
            "anchor_fraction": poly_slope(anchor, cfg.trend_window),
        },
        "config": {
            "anchor_eps": cfg.anchor_eps,
            "anchor_window": cfg.anchor_window,
            "trend_window": cfg.trend_window,
        }
    }
    return summary

# ----------------- I/O helpers ----------------- #

def load_phases(path: Path, fmt: Optional[str]) -> np.ndarray:
    """
    Load phases history. Supported:
      - .npy  : NP array (T, N)
      - .csv  : rows = time, columns = node_0..node_{N-1} (header allowed)
    """
    if fmt is None:
        fmt = path.suffix.lstrip(".").lower()
    if fmt == "npy":
        arr = np.load(path)
        if arr.ndim != 2:
            raise ValueError("Expected phases npy of shape (T, N)")
        return wrap_angle(arr.astype(float))
    elif fmt == "csv":
        # optional pandas
        try:
            import pandas as pd  # type: ignore
            df = pd.read_csv(path)
            # drop 't' if present
            cols = [c for c in df.columns if c.lower() != "t"]
            arr = df[cols].to_numpy(dtype=float)
        except Exception:
            # manual CSV parse
            rows = []
            with path.open() as f:
                header = f.readline()
                # detect if header contains non-numeric labels
                try:
                    float(header.split(",")[0])
                    # first line was actually data; include it
                    rows.append([float(x) for x in header.strip().split(",")[1:]])
                except Exception:
                    pass  # header ignored
                for line in f:
                    parts = line.strip().split(",")
                    if not parts:
                        continue
                    # if first column is 't', skip it
                    if parts[0].replace(".", "", 1).lstrip("-").isdigit():
                        parts = parts[1:]
                    rows.append([float(x) for x in parts])
            arr = np.array(rows, dtype=float)
        return wrap_angle(arr)
    else:
        raise ValueError(f"Unsupported format: {fmt}")

def load_driver(path: Optional[Path]) -> Optional[np.ndarray]:
    """Load driver phase series CSV with columns: t, driver_phase (radians)."""
    if path is None:
        return None
    try:
        import pandas as pd  # type: ignore
        df = pd.read_csv(path)
        col = "driver_phase" if "driver_phase" in df.columns else df.columns[-1]
        return wrap_angle(df[col].to_numpy(dtype=float))
    except Exception:
        # minimal parser
        vals = []
        with path.open() as f:
            header = f.readline()  # discard
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 1:
                    vals.append(float(parts[0]))
                else:
                    vals.append(float(parts[-1]))
        return wrap_angle(np.array(vals, dtype=float))

def write_timeseries_csv(out_csv: Path, t: np.ndarray, ts: Dict[str, np.ndarray]) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    # prefer pandas if available for nice headers
    try:
        import pandas as pd  # type: ignore
        df = {"t": t}
        for k, v in ts.items():
            df[k] = v
        pd.DataFrame(df).to_csv(out_csv, index=False)
    except Exception:
        # fallback
        keys = list(ts.keys())
        with out_csv.open("w") as f:
            f.write(",".join(["t"] + keys) + "\n")
            for i in range(len(t)):
                row = [f"{t[i]:.0f}"] + [f"{ts[k][i]:.9f}" for k in keys]
                f.write(",".join(row) + "\n")

def write_summary_json(out_json: Path, summary: Dict) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, indent=2))

# ----------------- CLI ----------------- #

def main(argv=None):
    ap = argparse.ArgumentParser(description="Compute coherence metrics from phase histories.")
    ap.add_argument("--input", required=True, help="Path to phases (.npy or .csv)")
    ap.add_argument("--format", choices=["npy", "csv"], default=None, help="Force input format if needed")
    ap.add_argument("--driver", default=None, help="Optional CSV with columns: t, driver_phase (radians)")
    ap.add_argument("--anchor-eps", type=float, default=0.35, help="Lock threshold (rad)")
    ap.add_argument("--anchor-window", type=int, default=1, help="Consecutive timepoints required for lock")
    ap.add_argument("--trend-window", type=int, default=400, help="Samples used for trend slope")
    ap.add_argument("--outdir", default="artifacts/coherence", help="Output directory")
    args = ap.parse_args(argv)

    phases_path = Path(args.input)
    driver_path = Path(args.driver) if args.driver else None
    outdir = Path(args.outdir)

    cfg = MetricsConfig(
        anchor_eps=args.anchor_eps,
        anchor_window=args.anchor_window,
        trend_window=args.trend_window,
    )

    phases_hist = load_phases(phases_path, args.format)
    driver_phase = load_driver(driver_path)

    T = phases_hist.shape[0]
    t = np.arange(T, dtype=int)

    ts = compute_timeseries(phases_hist, driver_phase=driver_phase, cfg=cfg)

    # Optional PLV (global)
    try:
        plv = compute_plv_global(phases_hist)
    except Exception:
        plv = None

    summary = summarize_metrics(ts, cfg)
    summary["global_plv"] = plv

    outdir.mkdir(parents=True, exist_ok=True)
    write_timeseries_csv(outdir / "metrics_timeseries.csv", t, ts)
    write_summary_json(outdir / "summary.json", summary)

    # Concise console echo
    print("Hum: measured coherence — no claims, only metrics.")
    print(json.dumps({
        "final_R": summary["final"]["R"],
        "final_anchor_fraction": summary["final"]["anchor_fraction"],
        "final_gap_abs": summary["final"]["gap_abs"],
        "slope_R": summary["slope"]["R"],
        "slope_gap_abs": summary["slope"]["gap_abs"],
        "slope_anchor_fraction": summary["slope"]["anchor_fraction"],
        "global_plv": summary["global_plv"],
        "outdir": str(outdir)
    }, indent=2))

if __name__ == "__main__":
    main()
