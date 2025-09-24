from sims.creation import simulate, CreationConfig
import numpy as np

def test_creation_runs_and_logs_events():
    cfg = CreationConfig(steps=800, N=90, grow_every=100, grow_budget=10, seed=9)
    out = simulate(cfg)
    # must return core traces
    for k in ["R","gap_to_env","K_cross_t","anchors_count","creation_events","summary"]:
        assert k in out
    assert out["R"].shape[0] == cfg.steps
    # summary finite
    s = out["summary"]
    assert np.isfinite(s["R_mean_tail"])
    assert np.isfinite(s["gap_env_tail"])
    assert np.isfinite(s["r_tail_mean"])
    # creation events shape
    ev = out["creation_events"]
    assert ev.ndim == 2 and ev.shape[1] == 3
