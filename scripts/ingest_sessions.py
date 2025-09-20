#!/usr/bin/env python3
"""
scripts/ingest_sessions.py

Ingest sim CSV logs and propose learning signals:
- rolling means of R_total, cross_sync, drift, ready
- deltas comparing presets
- suggested parameter tweaks for next runs

Usage:
  python scripts/ingest_sessions.py logs/circle.csv logs/grid.csv --out sessions/suggestions.json
"""
from __future__ import annotations
import argparse, json, csv
from pathlib import Path
from typing import Dict, List
import numpy as np


def load_csv(path: Path) -> Dict[str, np.ndarray]:
    cols: Dict[str, List[float]] = {}
    with path.open() as f:
        r = csv.DictReader(f)
        for row in r:
            for k, v in row.items():
                try:
                    cols.setdefault(k, []).append(float(v))
                except ValueError:
                    pass
    return {k: np.array(v, dtype=float) for k, v in cols.items()}


def summarize(metrics: Dict[str, np.ndarray]) -> Dict[str, float]:
    out = {}
    for k, v in metrics.items():
        if v.size == 0:
            continue
        out[f"{k}_mean"] = float(np.mean(v))
        out[f"{k}_std"]  = float(np.std(v))
        out[f"{k}_last"] = float(v[-1])
    return out


def suggest_weights(a: Dict[str, float], b: Dict[str, float]) -> Dict[str, float]:
    """
    Heuristic suggestions:
      Prefer higher R_total & cross_sync with lower drift.
      If 'ready' was high but R_total low, suggest reducing coupling to avoid over-lock.
    """
    def get(d, key, default=0.0): return d.get(key, default)

    a_good = (get(a,"R_total_mean") > get(b,"R_total_mean")) and \
             (get(a,"cross_sync_mean") >= get(b,"cross_sync_mean")) and \
             (get(a,"drift_mean") <= get(b,"drift_mean"))

    # If readiness was high but coherence under-delivered, reduce tightness
    a_overlock = (get(a,"ready_mean") > 0.7 and get(a,"R_total_mean") < get(b,"R_total_mean"))

    if a_good and not a_overlock:
        return {
            "suggest_pi_delta": +0.05,
            "suggest_intraK_delta": +0.02,
            "note": "Run A exhibits stronger coherence with smoother drift. Try slightly higher π and intra_K."
        }
    else:
        return {
            "suggest_pi_delta": -0.05 if a_overlock else -0.02,
            "suggest_intraK_delta": -0.02,
            "note": "Signs of over-lock or weaker cross-sync. Try slightly lower π and intra_K to reintroduce flexibility."
        }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", nargs="+", help="CSV logs")
    ap.add_argument("--out", type=str, default="sessions/suggestions.json")
    args = ap.parse_args()

    paths = [Path(p) for p in args.csv]
    summaries = [summarize(load_csv(p)) for p in paths]

    result = {"runs": summaries}
    if len(summaries) >= 2:
        result["suggestions"] = suggest_weights(summaries[0], summaries[1])

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
