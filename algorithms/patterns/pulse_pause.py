import numpy as np

def pulse_pause_oscillator(T: int, dt: float, f_target: float, duty: float = 0.5, noise: float = 0.0) -> np.ndarray:
    """
    Discrete oscillator that alternates between 'pulse' (drive on) and 'pause' (drive off).
    - T: total steps
    - dt: time step
    - f_target: target frequency (Hz)
    - duty: fraction of period with drive on (0..1)
    - noise: additive Gaussian noise std
    Returns time-series x[t].
    """
    t = np.arange(T) * dt
    period = 1.0 / max(f_target, 1e-6)
    x = np.zeros(T)
    phase = 0.0
    for i in range(T):
        tau = t[i] % period
        drive_on = (tau / period) < duty
        omega = 2 * np.pi * f_target
        phase += omega * dt if drive_on else 0.5 * omega * dt
        x[i] = np.sin(phase) + (np.random.randn() * noise if noise > 0 else 0.0)
    return x

def schumann_lock(x: np.ndarray, fs: float, schumann_f: float = 7.83, k: float = 0.02) -> np.ndarray:
    """
    Phase-lock a series toward the Schumann resonance by gentle frequency nudging.
    """
    # simple integrator nudging toward target phase velocity
    y = np.zeros_like(x)
    phase = 0.0
    omega_target = 2 * np.pi * schumann_f
    for i in range(len(x)):
        omega = omega_target + k * x[i]  # small coupling
        phase += omega / fs
        y[i] = np.sin(phase)
    return y
