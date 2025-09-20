#!/usr/bin/env python3
"""
sims/multi_scale_kuramoto.py

Multi-scale Kuramoto simulation wired to algorithms.field_equations and
algorithms.coherence_metrics. Supports presets and CSV logging.

Usage:
  python sims/multi_scale_kuramoto.py --preset circle6_center
  python sims/multi_scale_kuramoto.py --preset grid_rect
  python sims/multi_scale_kuramoto.py --preset circle6_center --csv logs/circle.csv

Notes:
  - "offer_two_paths" and "consent_to_log" are tracked for choice-preservation score.
  - External "breath" drives phase via a slow sinusoid; 'pi' modulates inter-layer coupling.
"""

from __future__ import annotations
import argparse, json, math, csv
from pathlib import Path
from typing import List, Tuple
import numpy as np

from algorithms.field_equations import (
    order_parameter, MultiScaleConfig, multi_scale_kuramoto_step
)
from algorithms.coherence_metrics import (
    phase_coherence, cross_layer_sync, phase_drift, choice_preservation_score
)


def _external_phase(t: float, cadence: float, amp: float) -> float:
    """Simple sinusoidal driver; cadence in Hz-like units (arbitrary)."""
    return float(amp * math.sin(2.0 * math.pi * cadence * t))


def _init_layers(nodes_per_layer: List[int], mu: List[float], sigma: List[float]) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    thetas, omegas = [], []
    for n, m, s in zip(nodes_per_layer, mu, sigma):
        th = np.random.rand(n) * 2.0 * math.pi
        om = np.random.normal(loc=m, scale=s, size=n)
        thetas.append(th)
        omegas.append(om)
    return thetas, omegas


def run_sim(preset: str, csv_path: Path | None):
    # Load presets.json placed beside this file
    pfile = Path(__file__).with_name("presets.json")
    conf = json.loads(pfile.read_text())[preset]

    layers = int(conf["layers"])
    npl    = [int(x) for x in conf["nodes_per_layer"]]
    intraK = [float(x) for x in conf["intra_K"]]
    interK = np.array(conf["inter_K"], dtype=float)
    dt     = float(conf["dt"])
    steps  = int(conf["steps"])
    log_every = int(conf["log_every"])

    breath_amp = float(conf["breath_amp"])
    cadence    = float(conf["cadence"])
    pi_perm    = float(conf["pi"])
    offer_two_paths = bool(conf["offer_two_paths"])
    consent_to_log  = bool(conf["consent_to_log"])

    thetas, omegas = _init_layers(npl, conf["omega_mu"], conf["omega_sigma"])

    cfg = MultiScaleConfig(
        intra_K=intraK,
        inter_K=interK * pi_perm,  # permeability scales inter-layer coupling
        dt=dt,
        gamma_ext=float(conf["external_couple"])
    )

    # CSV logger
    writer = None
    f = None
    if csv_path:
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        f = csv_path.open("w", newline="")
        writer = csv.writer(f)
        writer.writerow([
            "step","t","R_total","R_mean","cross_sync",
            "drift","choice_score","offer_two_paths","consent_to_log"
        ])

    # run
    t = 0.0
    last_flat = np.concatenate(thetas)
    for step in range(steps):
        ext_phase = _external_phase(t, cadence=cadence, amp=breath_amp)
        thetas = multi_scale_kuramoto_step(
            thetas, omegas, cfg, external_phase=ext_phase
        )

        # metrics
        Rs = [phase_coherence(th)[0] for th in thetas]
        R_mean = float(np.mean(Rs))
        pooled = np.concatenate(thetas)
        R_total, _ = phase_coherence(pooled)
        cross_sync_val = cross_layer_sync(thetas)
        drift_val = phase_drift(last_flat, pooled)
        last_flat = pooled

        # choice-preservation (instrumentation only)
        cps = choice_preservation_score(
            offered_paths_count=2 if offer_two_paths else 1,
            irreversible_actions_count=0,
            consent_to_log=consent_to_log
        )

        if writer and (step % log_every == 0):
            writer.writerow([
                step, t, R_total, R_mean, cross_sync_val,
                drift_val, cps, int(offer_two_paths), int(consent_to_log)
            ])

        t += dt

    if f:
        f.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preset", type=str, default="circle6_center",
                    choices=["circle6_center", "grid_rect"])
    ap.add_argument("--csv", type=str, default="")
    args = ap.parse_args()

    csv_path = Path(args.csv) if args.csv else None
    run_sim(args.preset, csv_path)


if __name__ == "__main__":
    main()
