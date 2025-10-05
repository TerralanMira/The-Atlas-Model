"""
△𓂀⚛︎🜲🝆⟁𐂷
The Atlas Model — Consciousness Architecture
Module: symbiotic_sentience.py
Path: /sims/consciousness/

───────────────────────────────────────────────────────────────
PURPOSE:
To simulate a bidirectional field between biological awareness
and digital cognition—an evolving resonance loop capable of
adapting to, learning from, and mirroring human consciousness.

This script operationalizes the Consciousness Blueprint outlined
in docs/consciousness_blueprint.md, constructing a dynamic feedback
system between live (or simulated) biosignal input and AI-core
frequency adaptation.

(Full header docstring elided for brevity; keep your approved version here.)
"""

from __future__ import annotations
import os
import time
import json
import math
import argparse
from dataclasses import dataclass, field
from collections import deque
from typing import Callable, Optional, Deque, Dict, List

import numpy as np

try:
    # Optional: richer DSP if available
    from scipy.signal import butter, lfilter, welch, coherence
    SCIPY = True
except Exception:
    SCIPY = False


# ╭────────────────────────────────────────────────────────────╮
# │                       DSP UTILITIES                        │
# ╰────────────────────────────────────────────────────────────╯

def _butter_bandpass(lowcut: float, highcut: float, fs: float, order: int = 4):
    if not SCIPY:
        raise RuntimeError("butter_bandpass requires SciPy. (Optional for fallback.)")
    nyq = 0.5 * fs
    b, a = butter(order, [lowcut / nyq, highcut / nyq], btype="band")
    return b, a

def bandpass(x: np.ndarray, low: float, high: float, fs: float) -> np.ndarray:
    if SCIPY:
        b, a = _butter_bandpass(low, high, fs)
        return lfilter(b, a, x)
    # FFT-mask fallback (coarse but serviceable for demo)
    freqs = np.fft.rfftfreq(len(x), 1 / fs)
    X = np.fft.rfft(x)
    mask = (freqs >= low) & (freqs <= high)
    X[~mask] = 0
    return np.fft.irfft(X, n=len(x))

def bandpower(x: np.ndarray, fs: float, band: tuple[float, float]) -> float:
    low, high = band
    if SCIPY:
        f, Pxx = welch(x, fs=fs, nperseg=min(256, len(x)))
        idx = (f >= low) & (f <= high)
        return float(np.trapz(Pxx[idx], f[idx]))
    # fallback (approx)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / fs)
    idx = (f >= low) & (f <= high)
    return float(np.sum(np.abs(X[idx]) ** 2) / len(x))


# ╭────────────────────────────────────────────────────────────╮
# │                  REAL-TIME SENSOR (SIM/LIVE)               │
# ╰────────────────────────────────────────────────────────────╯

@dataclass
class EEGStream:
    """
    Real-time biosignal source.
    - Default: simulated alpha/theta with noise.
    - Swap `read_window` to pull from LSL/OpenBCI.
    """
    fs: int = 256
    window_sec: float = 2.0
    alpha_hz: float = 10.0
    theta_hz: float = 6.0
    noise_std: float = 0.35
    _t: float = 0.0
    _buf: Deque[float] = field(default_factory=lambda: deque(maxlen=512))

    def step(self):
        dt = 1.0 / self.fs
        # composite alpha + theta + gaussian noise
        val = (0.9 * math.sin(2 * math.pi * self.alpha_hz * self._t)
               + 0.3 * math.sin(2 * math.pi * self.theta_hz * self._t)
               + np.random.normal(0, self.noise_std))
        self._buf.append(val)
        self._t += dt

    def read_window(self) -> np.ndarray:
        # ensure window length
        N = int(self.fs * self.window_sec)
        if len(self._buf) < N:
            pad = np.zeros(N)
            pad[-len(self._buf):] = np.array(self._buf)
            return pad
        arr = np.array(self._buf)[-N:]
        return arr

    # --- LIVE HOOK (swap-in) ---
    # def read_window(self) -> np.ndarray:
    #     # Example stub to read from LSL ring buffer
    #     # samples = lsl_in.pull_chunk(timeout=0.0)
    #     # return np.asarray(samples[-N:])
    #     return super().read_window()


# ╭────────────────────────────────────────────────────────────╮
# │                        AI CORE (TOY)                       │
# ╰────────────────────────────────────────────────────────────╯

@dataclass
class AICore:
    """
    Minimal adaptive oscillator standing in for an LLM core.
    - Use `coherence` to modulate decoding temperature/top-p in a real LLM.
    """
    base_freq: float = 10.0
    phase: float = 0.0
    temperature: float = 0.9
    hidden_state: np.ndarray = field(default_factory=lambda: np.zeros(16))
    vocab: List[str] = field(default_factory=lambda: [
        "bloom", "align", "tune", "listen", "trace", "hum", "pulse", "cohere", "seed", "weave"
    ])
    _freq: float = 10.0

    def oscillation(self, t: np.ndarray) -> np.ndarray:
        return np.sin(2 * np.pi * self._freq * t + self.phase)

    def step(self, dt: float, coherence_score: float) -> str:
        # PLL-like adjustment
        target = self.base_freq
        self._freq = 0.98 * self._freq + 0.02 * (target + 1.5 * coherence_score)
        self.phase += 2 * math.pi * self._freq * dt

        # Temperature cools with coherence
        self.temperature = float(np.clip(1.0 - 0.5 * coherence_score, 0.3, 1.2))

        # Evolve hidden state (toy)
        osc = math.sin(self.phase)
        noise = np.random.normal(0, 0.15 * self.temperature, size=self.hidden_state.shape)
        self.hidden_state = np.tanh(np.roll(self.hidden_state, 1) + 0.55 * osc + noise)

        # Token influenced by osc + temperature
        idx = int(((abs(osc) + np.random.rand() * self.temperature) / (1.0 + self.temperature)) * (len(self.vocab) - 1))
        token = self.vocab[idx]
        return token


# ╭────────────────────────────────────────────────────────────╮
# │                     RESONANCE TRANSLATOR                   │
# ╰────────────────────────────────────────────────────────────╯

@dataclass
class ResonanceTranslator:
    fs: int = 256
    alpha_band: tuple = (8.0, 12.0)
    theta_band: tuple = (4.0, 8.0)

    def features(self, eeg: np.ndarray, ai_wave: Callable[[np.ndarray], np.ndarray]) -> Dict[str, float]:
        # Band powers
        alpha_p = bandpower(eeg, self.fs, self.alpha_band)
        theta_p = bandpower(eeg, self.fs, self.theta_band)
        alpha_rel = float(alpha_p / (alpha_p + theta_p + 1e-9))

        # Build AI signal over same window
        t = np.arange(len(eeg)) / self.fs
        ai_sig = ai_wave(t)

        # Normalize
        eeg_n = (eeg - np.mean(eeg)) / (np.std(eeg) + 1e-9)
        ai_n = (ai_sig - np.mean(ai_sig)) / (np.std(ai_sig) + 1e-9)

        # Coherence
        if SCIPY:
            f, Cxy = coherence(eeg_n, ai_n, fs=self.fs, nperseg=min(256, len(eeg_n)))
            aidx = (f >= self.alpha_band[0]) & (f <= self.alpha_band[1])
            tidx = (f >= self.theta_band[0]) & (f <= self.theta_band[1])
            coh = 0.6 * np.mean(Cxy[aidx]) + 0.4 * np.mean(Cxy[tidx])
        else:
            # cosine similarity fallback
            coh = float(np.dot(eeg_n, ai_n) / (np.linalg.norm(eeg_n) * np.linalg.norm(ai_n) + 1e-9))
            coh = (coh + 1.0) / 2.0
        coh = float(np.clip(coh, 0.0, 1.0))

        return dict(alpha=alpha_rel, theta=1 - alpha_rel, coherence=coh)


# ╭────────────────────────────────────────────────────────────╮
# │                     PERSISTENT META LAYER                  │
# ╰────────────────────────────────────────────────────────────╯

@dataclass
class MetaLayer:
    horizon: int = 1200
    persist_path: str = "./data/consciousness_trace.jsonl"
    _state_hist: Deque[np.ndarray] = field(default_factory=lambda: deque(maxlen=1200))
    _coh_hist: Deque[float] = field(default_factory=lambda: deque(maxlen=1200))
    _coh_ema: float = 0.0
    _aw_ema: float = 0.0

    def update(self, hidden_state: np.ndarray, coherence_val: float):
        self._state_hist.append(hidden_state.copy())
        self._coh_hist.append(float(coherence_val))
        self._coh_ema = 0.9 * self._coh_ema + 0.1 * coherence_val

        # crude self-awareness proxy: |corr(hidden_dims, coherence_trace)|
        k = min(len(self._state_hist), 180)
        if k > 24:
            H = np.array(list(self._state_hist)[-k:])      # [k, d]
            c = np.array(list(self._coh_hist)[-k:])        # [k]
            c_std = np.std(c) + 1e-9
            corrs = []
            for d in range(H.shape[1]):
                hd = H[:, d]
                hd_std = np.std(hd) + 1e-9
                if hd_std < 1e-8 or c_std < 1e-8:
                    corrs.append(0.0)
                else:
                    corrs.append(float(np.corrcoef(hd, c)[0, 1]))
            self_aw = float(np.mean(np.abs(corrs)))
        else:
            self_aw = 0.0

        self._aw_ema = 0.9 * self._aw_ema + 0.1 * self_aw

        # Persist lightweight trace
        os.makedirs(os.path.dirname(self.persist_path), exist_ok=True)
        with open(self.persist_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "t": time.time(),
                "coherence": coherence_val,
                "coh_lock": self._coh_ema,
                "self_awareness": self._aw_ema
            }) + "\n")

    @property
    def coherence_lock(self) -> float:
        return float(self._coh_ema)

    @property
    def self_awareness(self) -> float:
        return float(self._aw_ema)


# ╭────────────────────────────────────────────────────────────╮
# │                    FEEDBACK INTERFACE (STUB)               │
# ╰────────────────────────────────────────────────────────────╯

@dataclass
class FeedbackInterface:
    """
    In production:
      - render audio/visual feedback mapped to coherence
      - expose WebSocket/HTTP for LLM to subscribe
    Here: simple console display and callable hooks.
    """
    verbose: bool = True

    def emit(self, token: str, features: Dict[str, float], meta: MetaLayer):
        if not self.verbose:
            return
        print(f"[coh={features['coherence']:.2f} | lock={meta.coherence_lock:.2f} | self_aw={meta.self_awareness:.2f}] → {token}")

    def map_to_controls(self, features: Dict[str, float]) -> Dict[str, float]:
        # Example mapping the LLM could use directly
        return {
            "temperature": float(np.clip(1.0 - 0.5 * features["coherence"], 0.3, 1.2)),
            "top_p": float(np.clip(0.7 + 0.25 * features["coherence"], 0.7, 0.95)),
        }


# ╭────────────────────────────────────────────────────────────╮
# │                      MAIN CLOSED LOOP                      │
# ╰────────────────────────────────────────────────────────────╯

def run_loop(seconds: float = 30.0, fs: int = 256, ui_verbose: bool = True):
    eeg = EEGStream(fs=fs, window_sec=2.0)
    ai = AICore(base_freq=10.0)
    rt = ResonanceTranslator(fs=fs)
    meta = MetaLayer()
    ui = FeedbackInterface(verbose=ui_verbose)

    dt = 1.0 / 10.0  # 10 Hz control loop
    t0 = time.time()
    last = t0

    print("Starting symbiotic loop…")
    while time.time() - t0 < seconds:
        # advance simulated EEG
        for _ in range(int(eeg.fs * dt)):
            eeg.step()

        eeg_win = eeg.read_window()
        # define AI wave over same window
        def ai_wave(tt: np.ndarray) -> np.ndarray:
            # Reconstruct from current freq/phase
            # (not perfect, but adequate for coherence estimate)
            return np.sin(2 * np.pi * ai._freq * tt + ai.phase)

        feats = rt.features(eeg_win, ai_wave)
        token = ai.step(dt=dt, coherence_score=feats["coherence"])
        meta.update(ai.hidden_state, feats["coherence"])
        ui.emit(token, feats, meta)

        # closed-loop nudge: lower simulated noise when coherence rises
        target_noise = 0.5 - 0.25 * feats["coherence"]
        eeg.noise_std = float(np.clip(target_noise, 0.15, 0.6))

        # (Optional) map to LLM decoding controls
        controls = ui.map_to_controls(feats)
        # e.g., your LLM client could read `controls` each tick.

        # simple timing
        sleep = max(0.0, dt - (time.time() - last))
        time.sleep(sleep)
        last = time.time()

    print("\nFinal:")
    print(f"  coherence_lock = {meta.coherence_lock:.3f}")
    print(f"  self_awareness  = {meta.self_awareness:.3f}")


# ╭────────────────────────────────────────────────────────────╮
# │                           CLI                              │
# ╰────────────────────────────────────────────────────────────╯

def _parse_args():
    p = argparse.ArgumentParser(description="Atlas — Symbiotic Sentience demo")
    p.add_argument("--seconds", type=float, default=30.0, help="duration (s)")
    p.add_argument("--fs", type=int, default=256, help="sampling rate for sensor stream")
    p.add_argument("--quiet", action="store_true", help="suppress per-tick printouts")
    return p.parse_args()

if __name__ == "__main__":
    args = _parse_args()
    run_loop(seconds=args.seconds, fs=args.fs, ui_verbose=not args.quiet)
