# atlas_runner.py
# The Atlas Model: unified runner for simulation modules.
# - Dynamic import from sims.<name>
# - Standardized outputs: R_global, Q, tau_recovery, H_t, diagnostics
# - H-law fallback computation if missing: H = ∫ (R * Q) ds / kappa
# - Metrics persistence (JSON + PNG) and hum_state.json update
# - CLI usage:
#     python atlas_runner.py run kuramoto_schumann_hybrid --params '{"N":64,"K":1.0,"steps":2000}'
#     python atlas_runner.py list

from __future__ import annotations
import argparse
import importlib
import json
import math
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# -------------------------
# Paths & basic setup
# -------------------------
ROOT = Path(__file__).resolve().parent
METRICS_DIR = ROOT / "metrics"
STATE_DIR = ROOT / "state"
METRICS_DIR.mkdir(exist_ok=True)
STATE_DIR.mkdir(exist_ok=True)
STATE_FILE = STATE_DIR / "hum_state.json"

# -------------------------
# Utilities
# -------------------------

def _now_str() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

def _safe_float(x: Any, default: Optional[float] = None) -> Optional[float]:
    try:
        return float(x)
    except Exception:
        return default

def _series(x: Any) -> Optional[List[float]]:
    """Return list[float] if x looks like a series; else None."""
    if x is None:
        return None
    if isinstance(x, (list, tuple)):
        try:
            return [float(v) for v in x]
        except Exception:
            return None
    return None

def _mean(x: List[float]) -> float:
    return sum(x) / max(1, len(x))

def _variance(x: List[float]) -> float:
    if not x:
        return 0.0
    mu = _mean(x)
    return sum((v - mu) ** 2 for v in x) / len(x)

def _sigma(x: List[float]) -> float:
    return math.sqrt(_variance(x))

# -------------------------
# H-law helpers
# -------------------------

def compute_H_series(
    R_t: Optional[List[float]],
    Q_t: Optional[List[float]],
    kappa: float = 1.0
) -> Optional[List[float]]:
    """
    Compute H_t ≈ cumulative integral of (R * Q)/kappa over discrete steps.
    If Q_t missing, assume Q=1.0 (pure coherence view).
    """
    if R_t is None or not R_t:
        return None
    if Q_t is None or len(Q_t) != len(R_t):
        Q_t = [1.0] * len(R_t)
    acc = 0.0
    H_t = []
    for r, q in zip(R_t, Q_t):
        acc += (float(r) * float(q)) / float(kappa)
        H_t.append(acc)
    return H_t

def summarize_H(H_t: Optional[List[float]]) -> Tuple[Optional[float], Optional[float]]:
    """
    Return (H_mean, sigma_H) for stability/level checks.
    """
    if not H_t:
        return None, None
    return _mean(H_t), _sigma(H_t)

# -------------------------
# Output schema standardization
# -------------------------

REQUIRED_KEYS = ["R_global", "Q", "tau_recovery", "H_t", "diagnostics"]

def standardize_output(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize sim outputs to a common schema.
    Accepted raw keys (best effort):
      - Scalars: R_global, Q, tau_recovery
      - Series: R_t, Q_t, H_t
      - diagnostics: dict
    Fills missing with best-effort derivations/defaults.
    """
    out: Dict[str, Any] = {}
    # Scalars
    out["R_global"] = _safe_float(raw.get("R_global"), None)
    out["Q"] = _safe_float(raw.get("Q"), None)
    out["tau_recovery"] = _safe_float(raw.get("tau_recovery"), None)

    # Series candidates
    R_t = _series(raw.get("R_t"))
    Q_t = _series(raw.get("Q_t"))
    H_t = _series(raw.get("H_t"))

    # Derive H_t if absent but R_t (and maybe Q_t) exist
    if H_t is None and R_t is not None:
        H_t = compute_H_series(R_t, Q_t, kappa=float(raw.get("kappa", 1.0)))

    out["H_t"] = H_t
    out["diagnostics"] = raw.get("diagnostics", {})

    # If R_global missing but R_t exists, set to last value
    if out["R_global"] is None and R_t:
        out["R_global"] = R_t[-1]

    # If Q missing but Q_t exists, set to mean(Q_t)
    if out["Q"] is None and Q_t:
        out["Q"] = _mean(Q_t)

    # Ensure diagnostics is a dict
    if not isinstance(out["diagnostics"], dict):
        out["diagnostics"] = {"note": "non-dict diagnostics replaced"}

    return out

def validate_output_schema(out: Dict[str, Any]) -> List[str]:
    """
    Lightweight validation: ensure all required keys exist (allow None values),
    and types are reasonable.
    """
    errors = []
    for k in REQUIRED_KEYS:
        if k not in out:
            errors.append(f"missing key: {k}")
    if out.get("H_t") is not None and not isinstance(out["H_t"], list):
        errors.append("H_t must be list[float] or None")
    return errors

# -------------------------
# Persistence (JSON + PNG)
# -------------------------

def save_metrics(sim_name: str, params: Dict[str, Any], out: Dict[str, Any]) -> Dict[str, str]:
    """
    Save a JSON metrics file and quick plots for R_t and H_t if available.
    Returns paths.
    """
    ts = _now_str()
    base = f"{ts}_{sim_name}"
    json_path = METRICS_DIR / f"{base}.json"
    png_path_R = METRICS_DIR / f"{base}_R.png"
    png_path_H = METRICS_DIR / f"{base}_H.png"

    blob = {
        "timestamp": ts,
        "sim_name": sim_name,
        "params": params,
        "output": out,
    }
    json_path.write_text(json.dumps(blob, indent=2))

    # Optional plotting
    try:
        import matplotlib.pyplot as plt  # local import so runner works even if mpl missing
        # Plot R_t if present
        R_t = out.get("diagnostics", {}).get("R_t")
        if R_t is None:
            R_t = out.get("H_inputs", {}).get("R_t")  # optional alt key
        if R_t is None:
            R_t = out.get("R_t")  # in case sim standardize kept it

        if isinstance(R_t, list) and len(R_t) > 1:
            plt.figure()
            plt.plot(R_t)
            plt.title(f"R(t) – {sim_name}")
            plt.xlabel("t")
            plt.ylabel("R")
            plt.tight_layout()
            plt.savefig(png_path_R)
            plt.close()

        H_t = out.get("H_t")
        if isinstance(H_t, list) and len(H_t) > 1:
            plt.figure()
            plt.plot(H_t)
            plt.title(f"H(t) – {sim_name}")
            plt.xlabel("t")
            plt.ylabel("H")
            plt.tight_layout()
            plt.savefig(png_path_H)
            plt.close()
    except Exception as e:
        # Non-fatal: plotting optional
        pass

    return {"json": str(json_path), "png_R": str(png_path_R), "png_H": str(png_path_H)}

def update_hum_state(sim_name: str, out: Dict[str, Any], paths: Dict[str, str]) -> None:
    """
    Keep a small rolling state for the assistant to reference.
    """
    state = {}
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
        except Exception:
            state = {}

    H_t = out.get("H_t")
    H_mean, sigma_H = summarize_H(H_t)

    state.update({
        "last_update": _now_str(),
        "last_sim": sim_name,
        "R_global": out.get("R_global"),
        "Q": out.get("Q"),
        "tau_recovery": out.get("tau_recovery"),
        "H_mean": H_mean,
        "sigma_H": sigma_H,
        "artifacts": paths,
    })
    STATE_FILE.write_text(json.dumps(state, indent=2))

# -------------------------
# Dynamic loader & runner
# -------------------------

def import_sim_module(name: str):
    """
    Import module from sims.<name>. Accepts names like 'geo_kuramoto' or file-like 'kuramoto_schumann_hybrid'.
    """
    # normalize to module-safe
    module_name = name.replace("-", "_")
    return importlib.import_module(f"sims.{module_name}")

def run_sim(name: str, params: Dict[str, Any], *, save: bool = True) -> Dict[str, Any]:
    """
    Main programmatic API.
    """
    mod = import_sim_module(name)
    if not hasattr(mod, "run"):
        raise AttributeError(f"sims.{name} must expose a run(params: dict) -> dict")

    raw_out = mod.run(params or {})
    out = standardize_output(raw_out)
    errs = validate_output_schema(out)
    if errs:
        raise ValueError(f"Output schema errors: {errs}")

    artifacts = {"json": "", "png_R": "", "png_H": ""}
    if save:
        artifacts = save_metrics(name, params, out)
        update_hum_state(name, out, artifacts)

    # include quick summary for CLI
    H_mean, sigma_H = summarize_H(out.get("H_t"))
    summary = {
        "sim": name,
        "R_global": out.get("R_global"),
        "Q": out.get("Q"),
        "tau_recovery": out.get("tau_recovery"),
        "H_mean": H_mean,
        "sigma_H": sigma_H,
        "artifacts": artifacts
    }
    return summary

# -------------------------
# CLI
# -------------------------

def _parse_params_json(s: Optional[str]) -> Dict[str, Any]:
    if not s:
        return {}
    try:
        return json.loads(s)
    except json.JSONDecodeError as e:
        raise SystemExit(f"--params must be valid JSON (got error: {e})")

def list_available() -> List[str]:
    """
    Best-effort import of sims package to list available modules.
    """
    sims_dir = ROOT / "sims"
    names = []
    if sims_dir.exists():
        for p in sims_dir.glob("*.py"):
            if p.name.startswith("_"):
                continue
            names.append(p.stem)
    return sorted(names)

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Atlas Runner")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="Run a simulation")
    p_run.add_argument("name", help="simulation name (module under sims/)")
    p_run.add_argument("--params", help="JSON dict of parameters", default=None)
    p_run.add_argument("--nosave", action="store_true", help="Do not save metrics/state")

    p_list = sub.add_parser("list", help="List available sims")

    args = parser.parse_args(argv)

    if args.cmd == "list":
        names = list_available()
        if not names:
            print("No sims found under ./sims")
            return 0
        print("\n".join(names))
        return 0

    if args.cmd == "run":
        params = _parse_params_json(args.params)
        try:
            summary = run_sim(args.name, params, save=(not args.nosave))
        except Exception as e:
            print(f"[ERROR] {e}", file=sys.stderr)
            return 2
        # Pretty print concise summary
        print(json.dumps(summary, indent=2))
        return 0

    return 0

if __name__ == "__main__":
    sys.exit(main())
