from sims.resonance_transfer import simulate, TransferConfig
import numpy as np

def test_transfer_runs_and_shapes():
    cfg = TransferConfig(steps=300, N_total=40, groups=(20,20), seed=3)
    out = simulate(cfg)
    assert "R_global" in out and "R_groups" in out and "gap" in out
    assert out["R_groups"].shape[1] == 2
    assert len(out["R_global"]) == cfg.steps
    assert len(out["gap"]) == cfg.steps
    # coherent metrics should be finite
    assert np.isfinite(out["R_global"]).all()
    assert np.isfinite(out["R_groups"]).all()
    assert np.isfinite(out["gap"]).all()
