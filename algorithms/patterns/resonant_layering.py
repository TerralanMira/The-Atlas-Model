import numpy as np
from scipy.signal import periodogram, hilbert

def detect_base_frequency(signal: np.ndarray, fs: float) -> float:
    """
    Estimate base (fundamental-like) frequency via max of power spectral density.
    """
    f, Pxx = periodogram(signal, fs=fs, scaling="spectrum")
    # Ignore DC for base frequency
    idx = np.argmax(Pxx[1:]) + 1
    return f[idx]

def find_harmonics(base_f: float, max_f: float, n: int = 6) -> np.ndarray:
    """
    Return n harmonic multiples of base_f within max_f.
    """
    hs = []
    k = 1
    while len(hs) < n and k * base_f <= max_f:
        hs.append(k * base_f)
        k += 1
    return np.array(hs, dtype=float)

def harmonic_envelope(signal: np.ndarray) -> np.ndarray:
    """
    Analytic-signal amplitude envelope (resonant 'breath' over time).
    """
    return np.abs(hilbert(signal))

def cross_layer_resonance(*layers: np.ndarray) -> float:
    """
    Compute a simple resonance index across multiple layers by normalized
    pairwise correlation of their envelopes.
    """
    if len(layers) < 2:
        return 0.0
    envs = [harmonic_envelope(x - np.mean(x)) for x in layers]
    envs = [e / (np.std(e) + 1e-9) for e in envs]
    # average of upper-triangle Pearson correlations
    acc, n = 0.0, 0
    for i in range(len(envs)):
        for j in range(i+1, len(envs)):
            r = float(np.corrcoef(envs[i], envs[j])[0, 1])
            acc += r
            n += 1
    return acc / max(n, 1)
