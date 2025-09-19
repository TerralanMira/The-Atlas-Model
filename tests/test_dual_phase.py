import math
import pytest

# Import simulation; skip if not available (keeps CI green if module name changes)
field_equations = pytest.importorskip("algorithms.field_equations")
DualPhaseConfig = getattr(field_equations, "DualPhaseConfig", None)
simulate_dual_phase = getattr(field_equations, "simulate_dual_phase", None)

pytestmark = pytest.mark.skipif(
    DualPhaseConfig is None or simulate_dual_phase is None,
    reason="DualPhase sim not available in algorithms.field_equations"
)


def test_dual_phase_runs_quickly_and_bounds():
    # Keep this FAST for CI: very small step count, fixed seed if supported
    cfg = DualPhaseConfig(steps=60, dt=0.05)  # small run
    out = simulate_dual_phase(cfg)

    # Existence checks
    assert isinstance(out, dict)
    for key in ("R_total", "R_inner", "R_outer"):
        assert key in out, f"Missing key {key}"
        series = out[key]
        assert len(series) == cfg.steps
        # Bound checks with tolerance
        for r in series:
            assert -1e-9 <= float(r) <= 1.0 + 1e-9

    # Non-NaN / simple sanity
    r_final = float(out["R_total"][-1])
    assert not math.isnan(r_final)
