#!/usr/bin/env python3
"""
ingest_sessions.py

Ingest one or more CSV logs from sims (e.g., multi_scale_kuramoto.py) and
summarize resonance signals + propose small, reversible parameter deltas (Δ).

Inputs:  CSVs with headers like:
  step,t,R_total,R_mean,cross_sync,drift,C,Delta,Phi,ready,choice_score,offer_two_paths,consent_to_log

Output:  JSON (to --out) with per-run metrics + Return-Spiral suggestions.

Usage:
  python scripts/ingest_sessions.py logs/circle.csv logs/grid.csv --out sessions/suggestions.json
"""

from __future__ import annotations
import argparse, csv, json, math, os
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Optional

# -----------------------------
# Config
# -----------------------------

# Small, reversible nudges
DK_SMALL  = 0.05
DPI_SMALL = 0.05

# Thresholds (can be tuned later)
DELTA_LOW          = 0.30    # diversity too low => over-lock risk
R_LOW              = 0.50    # global coherence too low => under-coupled
R_HIGH             = 0.80    # very high coherence
DRIFT_VERY_LOW     = 0.02    # clamp risk
PHI_LOW            = 0.40    # flow not smooth
CROSS_SYNC_LOW     = 0.45
CROSS_SYNC_HIGH    = 0.75


# -----------------------------
# Data structures
# -----------------------------

@dataclass
class Metrics:
    mean_R: float = math.nan
    last_R: float = math.nan
    mean_cross: float = math.nan
    last_cross: float = math.nan
    mean_drift: float = math.nan
    last_drift: float = math.nan
    mean_C: float = math.nan
    last_C: float = math.nan
    mean_Delta: float = math.nan
    last_Delta: float = math.nan
    mean_Phi: float = math.nan
    last_Phi: float = math.nan
    mean_ready: float = math.nan
    last_ready: float = math.nan
    mean_choice: float = math.nan
    last_choice: float = math.nan


@dataclass
class Suggestions:
    # Suggested parameter nudges for next run
    dK: float = 0.0
    dPi: float = 0.0
    notes: List[str] = None

    def to_dict(self) -> Dict:
        return {"dK": self.dK, "dPi": self.dPi, "notes": self.notes or []}


@dataclass
class RunSummary:
    file: str
    rows: int
    metrics: Metrics
    suggestions: Suggestions


# -----------------------------
# Helpers
# -----------------------------

def _f(v: Optional[str]) -> Optional[float]:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except Exception:
        return None

def _mean(values: List[float]) -> float:
    vals = [v for v in values if v is not None and not math.isnan(v)]
    return float(sum(vals) / len(vals)) if vals else math.nan

def _last(values: List[float]) -> float:
    for v in reversed(values):
        if v is not None and not math.isnan(v):
            return float(v)
    return math.nan

def _col(rows: List[Dict[str, str]], key: str) -> List[Optional[float]]:
    return [_f(r.get(key)) for r in rows]

def _exists_any(rows: List[Dict[str, str]], key: str) -> bool:
    return any(r.get(key) not in (None, "") for r in rows)

def load_csv(path: str) -> List[Dict[str, str]]:
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)

def summarize_rows(rows: List[Dict[str, str]]) -> Metrics:
    R      = _col(rows, "R_total") or _col(rows, "R")  # fallback if older header
    cross  = _col(rows, "cross_sync")
    drift  = _col(rows, "drift")
    C      = _col(rows, "C")
    Delta  = _col(rows, "Delta")
    Phi    = _col(rows, "Phi")
    ready  = _col(rows, "ready")
    choice = _col(rows, "choice_score")

    return Metrics(
        mean_R=_mean(R),               last_R=_last(R),
        mean_cross=_mean(cross),       last_cross=_last(cross),
        mean_drift=_mean(drift),       last_drift=_last(drift),
        mean_C=_mean(C),               last_C=_last(C),
        mean_Delta=_mean(Delta),       last_Delta=_last(Delta),
        mean_Phi=_mean(Phi),           last_Phi=_last(Phi),
        mean_ready=_mean(ready),       last_ready=_last(ready),
        mean_choice=_mean(choice),     last_choice=_last(choice),
    )

def propose(metrics: Metrics) -> Suggestions:
    notes: List[str] = []
    dK = 0.0
    dPi = 0.0

    # 1) Over-lock risk: diversity too low or drift nearly zero while R is high
    if (not math.isnan(metrics.last_Delta) and metrics.last_Delta < DELTA_LOW) or \
       (not math.isnan(metrics.last_drift) and metrics.last_drift < DRIFT_VERY_LOW and \
        not math.isnan(metrics.last_R) and metrics.last_R >= R_HIGH):
        notes.append("Over-lock risk: diversity low or drift clamped.")
        dK -= DK_SMALL
        dPi += DPI_SMALL

    # 2) Under-coupled: coherence low but diversity high
    if (not math.isnan(metrics.mean_R) and metrics.mean_R < R_LOW) and \
       (not math.isnan(metrics.mean_Delta) and metrics.mean_Delta >= 0.6):
        notes.append("Under-coupled: raise coupling to help alignment.")
        dK += DK_SMALL

    # 3) Flow roughness
    if not math.isnan(metrics.mean_Phi) and metrics.mean_Phi < PHI_LOW:
        notes.append("Flow not smooth: reduce noise / destabilizer or slightly increase π.")
        dPi += 0.02  # very gentle

    # 4) Bridges weak: cross_sync low
    if not math.isnan(metrics.mean_cross) and metrics.mean_cross < CROSS_SYNC_LOW:
        notes.append("Bridges weak: adjust geometry or slightly increase K.")
        dK += 0.02

    # 5) Bridges too tight
    if not math.isnan(metrics.mean_cross) and metrics.mean_cross > CROSS_SYNC_HIGH and \
       not math.isnan(metrics.mean_Delta) and metrics.mean_Delta < 0.4:
        notes.append("Bridges too tight: widen options; reduce K or increase π.")
        dK -= 0.02
        dPi += 0.02

    # bound small deltas
    dK  = float(max(-0.15, min(0.15, dK)))
    dPi = float(max(-0.15, min(0.15, dPi)))

    # Nudge preference: prefer very small steps if both nonzero
    if abs(dK) > 0 and abs(dPi) > 0:
        dK  = round(dK, 2)
        dPi = round(dPi, 2)

    return Suggestions(dK=dK, dPi=dPi, notes=notes)


# -----------------------------
# Aggregate proposal
# -----------------------------

def aggregate_suggestions(run_summaries: List[RunSummary]) -> Suggestions:
    """Combine suggestions gently across runs (mean dK/dPi, union notes)."""
    if not run_summaries:
        return Suggestions(dK=0.0, dPi=0.0, notes=["No runs provided."])
    dK_vals  = [r.suggestions.dK for r in run_summaries]
    dPi_vals = [r.suggestions.dPi for r in run_summaries]
    dK_mean  = float(sum(dK_vals) / len(dK_vals))
    dPi_mean = float(sum(dPi_vals) / len(dPi_vals))
    notes: List[str] = []
    for r in run_summaries:
        for n in (r.suggestions.notes or []):
            if n not in notes:
                notes.append(n)
    # keep within gentle bounds
    dK_mean  = max(-0.10, min(0.10, dK_mean))
    dPi_mean = max(-0.10, min(0.10, dPi_mean))
    return Suggestions(dK=dK_mean, dPi=dPi_mean, notes=notes)


# -----------------------------
# Main
# -----------------------------

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Ingest sim logs and propose small Return-Spiral deltas.")
    ap.add_argument("csv_paths", nargs="+", help="Paths to CSV logs")
    ap.add_argument("--out", type=str, default="sessions/suggestions.json", help="Output JSON path")
    return ap.parse_args()

def main():
    args = parse_args()
    runs: List[RunSummary] = []

    for path in args.csv_paths:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"CSV not found: {path}")
        rows = load_csv(path)
        m = summarize_rows(rows)
        sug = propose(m)
        runs.append(RunSummary(file=path, rows=len(rows), metrics=m, suggestions=sug))

    agg = aggregate_suggestions(runs)

    # ensure output dir
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    payload = {
        "runs": [
            {
                "file": r.file,
                "rows": r.rows,
                "metrics": asdict(r.metrics),
                "suggestions": r.suggestions.to_dict(),
            }
            for r in runs
        ],
        "aggregate": agg.to_dict(),
        "schema": {
            "metrics_keys": list(asdict(Metrics()).keys()),
            "suggestions_keys": ["dK", "dPi", "notes"]
        }
    }

    with open(args.out, "w") as f:
        json.dump(payload, f, indent=2)

    # also print a tiny human summary
    print("=== Ingest Summary ===")
    for r in runs:
        print(f"- {os.path.basename(r.file)}: R̄={r.metrics.mean_R:.3f}, Δ̄={r.metrics.mean_Delta:.3f}, "
              f"Φ̄={r.metrics.mean_Phi:.3f}, cross̄={r.metrics.mean_cross:.3f}, drift̄={r.metrics.mean_drift:.3f}")
        if r.suggestions.notes:
            print("  notes:", "; ".join(r.suggestions.notes))
        print(f"  → propose ΔK={r.suggestions.dK:+.2f}, Δπ={r.suggestions.dPi:+.2f}")
    print(f"\nWrote {args.out}")

if __name__ == "__main__":
    main()
