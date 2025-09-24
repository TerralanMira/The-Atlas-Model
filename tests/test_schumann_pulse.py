from sims.schumann_pulse import simulate, SchumannConfig
import numpy as np

def test_schumann_runs_and_metrics():
    cfg = SchumannConfig(steps=400, N=64, dt=0.02, seed=2)
    out = simulate(cfg)
    assert "R" in out and "env" in out and "phi_env" in out and "phase_gap_to_env" in out
    assert len(out["R"]) == cfg.steps
    assert out["env_components"].shape[1] == cfg.steps
    # tail stats finite
    assert np.isfinite(out["summary"]["R_mean_tail"])
    assert np.isfinite(out["summary"]["gap_mean_tail"])
