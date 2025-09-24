from sims.crystallization_points import simulate, CrystalConfig
import numpy as np

def test_crystal_runs_and_reports():
    cfg = CrystalConfig(steps=600, N=60, window=40, seed=4)
    out = simulate(cfg)
    # expected keys
    for k in ["R", "R_local", "anchors_count", "r_hist", "summary"]:
        assert k in out
    assert len(out["R"]) == cfg.steps
    assert out["R_local"].shape == (cfg.steps, cfg.N)
    assert out["r_hist"].shape == (cfg.steps, cfg.N)
    # finite tail means
    s = out["summary"]
    assert np.isfinite(s["R_mean_tail"])
    assert np.isfinite(s["anchors_tail_mean"])
    assert np.isfinite(s["r_tail_mean"])
