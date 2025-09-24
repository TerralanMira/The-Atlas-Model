---

# 📄 `tests/test_ritual_window.py`

```python
from sims.ritual_window import simulate, RitualConfig
import numpy as np

def test_ritual_shapes_and_modulation():
    cfg = RitualConfig(steps=400, N_total=40, groups=(20,20), seed=5)
    out = simulate(cfg)
    assert out["R_groups"].shape[1] == 2
    assert len(out["K_cross_t"]) == cfg.steps
    assert len(out["noise_t"]) == cfg.steps
    assert np.all(out["K_cross_t"] >= 0)
    # ensure modulation is non-constant
    assert out["K_cross_t"].ptp() > 0.01
    assert out["noise_t"].ptp() > 0.005
