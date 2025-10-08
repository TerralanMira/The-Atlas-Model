# tests/test_creation.py
import numpy as np
from sims.creation import CreationConfig, simulate

def test_creation_runs_and_logs_events():
    cfg = CreationConfig(steps=1200, N=90, seed=9, dt=0.002)
    out = simulate(cfg)
    for k in ["R","gap_to_env","K","anchors_frac","creation_events","summary"]:
        assert k in out
    assert out["R"].ndim == 1 and out["R"].shape[0] == cfg.steps
    s = out["summary"]
    assert np.isfinite(s["R_mean_tail"])
    assert np.isfinite(s["K_mean_tail"])
    assert np.isfinite(s["anchors_mean_tail"])
    ev = out["creation_events"]
    assert ev.ndim == 2 and ev.shape[1] == 3
    
