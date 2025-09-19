from algorithms.field_equations import DualPhaseConfig, simulate_dual_phase

def test_dual_phase_runs():
    cfg = DualPhaseConfig(steps=40, dt=0.05)
    out = simulate_dual_phase(cfg)
    assert "R_total" in out and len(out["R_total"]) == cfg.steps
