from sims.braided_field import simulate, BraidedConfig
import numpy as np

def test_braid_runs_and_reports():
    cfg = BraidedConfig(steps=500, N=80, dt=0.02, seed=7)
    out = simulate(cfg)
    for key in ["R","gap_to_env","K_cross_t","noise_t","anchors_count","summary"]:
        assert key in out
        assert len(out[key]) == cfg.steps if isinstance(out[key], np.ndarray) else True
    s = out["summary"]
    assert np.isfinite(s["R_mean_tail"])
    assert np.isfinite(s["gap_env_tail"])
    assert np.isfinite(s["anchors_tail_mean"])
    assert np.isfinite(s["r_tail_mean"])
