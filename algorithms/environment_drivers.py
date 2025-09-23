"""
Environment & External Drivers for Resonance Simulations.

Provides smooth, composable drivers (e.g., Schumann bands, day/night cycles)
that can entrain agents. Each driver returns a phase phi(t) and instantaneous
frequency dphi/dt for time t.

Usage:
    from algorithms.environment_drivers import CompositeDriver, SineDriver

    env = CompositeDriver([
        SineDriver(freq_hz=7.83, amplitude=1.0, phase=0.0),  # Schumann 1
        SineDriver(freq_hz=0.1, amplitude=0.4, phase=0.1),   # ultralow slow wave
    ], dt=0.05, time_scale=1.0)  # time_scale can stretch/compress "seconds"

    phi_t = env.phase_at(t_index)  # radians
    dphi_t = env.omega_at(t_index) # rad/s
"""

import numpy as np
from typing import List

TWOPI = 2 * np.pi

class BaseDriver:
    def phase_at(self, t_index: int) -> float:
        raise NotImplementedError
    def omega_at(self, t_index: int) -> float:
        raise NotImplementedError

class SineDriver(BaseDriver):
    """
    Continuous sine oscillator:
        phi(t) = 2π f t + phase0
        omega = 2π f
    'freq_hz' is in driver-time units; time can be rescaled via CompositeDriver.time_scale
    """
    def __init__(self, freq_hz: float, amplitude: float = 1.0, phase: float = 0.0):
        self.freq_hz = float(freq_hz)
        self.amplitude = float(amplitude)
        self.phase0 = float(phase)

    def phase_at(self, t_index: int, dt: float = 1.0, time_scale: float = 1.0) -> float:
        t = t_index * dt * time_scale
        return (TWOPI * self.freq_hz * t + self.phase0) % TWOPI

    def omega_at(self, t_index: int, dt: float = 1.0, time_scale: float = 1.0) -> float:
        return TWOPI * self.freq_hz  # constant angular frequency

class CompositeDriver(BaseDriver):
    """
    Weighted sum of phases is tricky (angles). We provide a resultant phase by vector sum
    of unit phasors scaled by amplitude. The instantaneous frequency is a weighted sum
    of component omegas projected along the resultant.
    """
    def __init__(self, drivers: List[SineDriver], dt: float = 0.05, time_scale: float = 1.0):
        self.drivers = drivers
        self.dt = float(dt)
        self.time_scale = float(time_scale)

    def phase_at(self, t_index: int) -> float:
        Z = 0+0j
        for d in self.drivers:
            phi = d.phase_at(t_index, self.dt, self.time_scale)
            Z += d.amplitude * np.exp(1j * phi)
        if np.abs(Z) < 1e-12:
            return 0.0
        return float(np.angle(Z))

    def omega_at(self, t_index: int) -> float:
        # approximate by amplitude-weighted mean
        num = 0.0
        den = 0.0
        for d in self.drivers:
            num += d.amplitude * d.omega_at(t_index, self.dt, self.time_scale)
            den += d.amplitude
        return float(num / max(den, 1e-12))
