import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import hilbert, welch

def coherence_index(signal1, signal2, fs):
    """
    Calculate phase-locking value (PLV) between two signals
    as a measure of coherence.
    """
    # Hilbert transform for instantaneous phase
    phase1 = np.angle(hilbert(signal1))
    phase2 = np.angle(hilbert(signal2))

    # Phase difference
    phase_diff = phase1 - phase2

    # Phase locking value
    plv = np.abs(np.sum(np.exp(1j * phase_diff))) / len(phase_diff)
    return plv

# Example usage with synthetic data
if __name__ == "__main__":
    fs = 256  # Hz sampling rate
    t = np.arange(0, 10, 1/fs)  # 10 seconds

    # Simulate HRV-like signal (sinusoidal ~0.1 Hz)
    hrv_signal = np.sin(2 * np.pi * 0.1 * t) + 0.05 * np.random.randn(len(t))

    # Simulate EEG alpha wave (~10 Hz) with phase coupling
    eeg_signal = np.sin(2 * np.pi * 10 * t + np.sin(2 * np.pi * 0.1 * t)) + 0.1 * np.random.randn(len(t))

    # Compute coherence
    plv = coherence_index(hrv_signal, eeg_signal, fs)
    print(f"Heart–Brain Coherence Index: {plv:.3f}")

    # Visualization
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(t, hrv_signal, label="HRV (Heart Rhythm)")
    plt.plot(t, eeg_signal, label="EEG (Alpha)")
    plt.legend()
    plt.title("Synthetic HRV & EEG Signals")

    plt.subplot(2, 1, 2)
    f_hrv, Pxx_hrv = welch(hrv_signal, fs=fs)
    f_eeg, Pxx_eeg = welch(eeg_signal, fs=fs)
    plt.semilogy(f_hrv, Pxx_hrv, label="HRV Spectrum")
    plt.semilogy(f_eeg, Pxx_eeg, label="EEG Spectrum")
    plt.legend()
    plt.title("Power Spectral Density")

    plt.tight_layout()
    plt.show()
  What this does:
	•	Generates synthetic HRV + EEG-like signals.
	•	Extracts instantaneous phases using Hilbert transform.
	•	Computes a phase-locking value (PLV) → a true mathematical coherence measure.
	•	Prints a coherence score (0–1).
	•	Visualizes both signals and their frequency content.
