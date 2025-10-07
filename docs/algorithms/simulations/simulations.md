## Hum Kernel (Observer Layer)

A small, auditable layer used by sims to model observation, stability, and memory.

- Code: `sims/hum_kernel.py`
- Docs: `atlas/hum_kernel.md` · `awareness/coherence_thresholds.md`

**Usage (inside a sim loop):**
```python
from sims.hum_kernel import HumParams, SimSnapshot, apply_hum_controls
hp = HumParams(rho=0.6, lam=0.15, mu=0.5, log=True, run_id="exp01")

for t in range(steps):
    R, psi = order_parameter(theta)
    snap = SimSnapshot(step=t, dt=dt, phases=theta, natural=omega, order_R=R, order_psi=psi)
    ctrl = apply_hum_controls(hp, snap)

    noise = base_sigma * ctrl["sigma_eff_scale"] * np.sqrt(dt) * rng.normal(0,1,size=n)
    bias  = ctrl["coupling_bias"] * np.sin(psi - theta)
    theta = (theta + dt*(omega + K*np.sin(psi - theta) + bias) + noise) % (2*np.pi)
