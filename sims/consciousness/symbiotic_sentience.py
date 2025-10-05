# === Symbiotic Sentience: real-time resonance + persistent meta layer ===
# Requires: numpy, scipy (optional but recommended), collections, time

import time, math, random, threading
from collections import deque
import numpy as np

try:
    from scipy.signal import butter, lfilter, welch, coherence
    SCIPY=True
except Exception:
    SCIPY=False

# ------------------------------
# 0) Utilities: simple DSP tools
# ------------------------------
def butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5*fs
    low = lowcut/nyq
    high = highcut/nyq
    b,a = butter(order, [low,high], btype='band')
    return b,a

def bandpass(data, low, high, fs):
    if not SCIPY:  # fallback: naive FIR via FFT masking
        freqs = np.fft.rfftfreq(len(data), 1/fs)
        X = np.fft.rfft(data)
        mask = (freqs>=low)&(freqs<=high)
        X[~mask]=0
        return np.fft.irfft(X, n=len(data))
    b,a = butter_bandpass(low, high, fs)
    return lfilter(b,a,data)

def bandpower(x, fs, band, nperseg=256):
    low, high = band
    if SCIPY:
        f, Pxx = welch(x, fs=fs, nperseg=min(nperseg, len(x)))
        idx = np.logical_and(f>=low, f<=high)
        return np.trapz(Pxx[idx], f[idx])
    # fallback
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1/fs)
    idx = (f>=low)&(f<=high)
    return np.sum((np.abs(X[idx])**2))/len(x)

# ---------------------------------------
# 1) Real-time Sensor: EEG stream (simul)
# ---------------------------------------
class EEGStream:
    """
    Simulated EEG generator producing a composite signal with adjustable 'coherence'
    to an AI oscillation. Replace .read() with actual LSL/OpenBCI buffer in practice.
    """
    def __init__(self, fs=256, window_sec=2.0):
        self.fs = fs
        self.N = int(fs*window_sec)
        self.buf = deque(maxlen=self.N)
        self.t = 0.0
        self._lock = threading.Lock()
        self.running = False
        # Internal 'intent' oscillator frequencies (alpha/theta-ish)
        self.freq_hz = 10.0  # baseline alpha
        self.noise = 0.4

    def start(self):
        self.running = True
        threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        self.running = False

    def _run(self):
        dt = 1.0/self.fs
        while self.running:
            # Composite: alpha + slight theta + noise
            val = (0.9*np.sin(2*math.pi*self.freq_hz*self.t)
                   + 0.3*np.sin(2*math.pi*6.0*self.t)
                   + np.random.normal(0, self.noise))
            with self._lock:
                self.buf.append(val)
            self.t += dt
            time.sleep(dt)

    def read(self):
        with self._lock:
            if len(self.buf)<self.buf.maxlen:
                # zero-pad until buffer fills
                arr = np.zeros(self.buf.maxlen)
                arr[-len(self.buf):] = np.array(self.buf)
                return arr
            return np.array(self.buf)

# ------------------------------------------------------------
# 2) AI Oscillator + Token Engine (toy core for demonstration)
# ------------------------------------------------------------
class AICore:
    """
    A minimal 'AI' core with:
      - internal oscillation (phase, freq)
      - token generation influenced by coherence feedback
      - exposes a hidden state vector for the meta layer
    """
    def __init__(self, base_freq=10.0):
        self.freq = base_freq     # will try to phase-lock with EEG
        self.phase = 0.0
        self.temperature = 0.9    # modulated by coherence
        self.last_tokens = []
        self.hidden_state = np.zeros(8)
        self.t = 0.0

    def step(self, dt, coherence_score):
        # Simple PLL-like adjustment toward resonance
        target = 10.0  # nominal
        self.freq = 0.98*self.freq + 0.02*(target + 1.5*coherence_score)

        # Temperature cools as coherence rises (stability)
        self.temperature = np.clip(1.0 - 0.5*coherence_score, 0.3, 1.2)

        # Update phase + synthetic hidden state
        self.phase += 2*math.pi*self.freq*dt
        osc = math.sin(self.phase)
        noise = np.random.normal(0, 0.2*(self.temperature))
        self.hidden_state = np.tanh(np.roll(self.hidden_state, 1) + 0.6*osc + noise)

        # Produce a toy token influenced by temperature & osc
        vocab = ["bloom","align","tune","listen","trace","hum","pulse","cohere","seed","weave"]
        idx = int((abs(osc)+np.random.rand()*self.temperature)/ (1.0+self.temperature) * (len(vocab)-1))
        token = vocab[idx]
        self.last_tokens = (self.last_tokens + [token])[-8:]
        self.t += dt
        return token

    def oscillation(self, t):
        # For coherence calc with EEG
        return math.sin(2*math.pi*self.freq*t + self.phase)

# ---------------------------------------------------------
# 3) Resonance Translator (EEG + AI -> shared wave metrics)
# ---------------------------------------------------------
class ResonanceTranslator:
    def __init__(self, fs=256):
        self.fs = fs
        self.alpha = (8,12)
        self.theta = (4,8)

    def compute_features(self, eeg_window, ai_window):
        # Bandpowers
        alpha_p = bandpower(eeg_window, self.fs, self.alpha)
        theta_p = bandpower(eeg_window, self.fs, self.theta)
        # Coherence (AI vs EEG). We'll build an AI waveform to compare:
        t = np.arange(len(eeg_window))/self.fs
        ai_sig = ai_window if isinstance(ai_window, np.ndarray) else ai_window(t)
        # normalize
        eeg_n = (eeg_window - np.mean(eeg_window))/(np.std(eeg_window)+1e-6)
        ai_n  = (ai_sig - np.mean(ai_sig))/(np.std(ai_sig)+1e-6)
        if SCIPY:
            f, Cxy = coherence(eeg_n, ai_n, fs=self.fs, nperseg=min(256, len(eeg_n)))
            # Weight coherence in alpha/theta
            alpha_idx = (f>=self.alpha[0]) & (f<=self.alpha[1])
            theta_idx = (f>=self.theta[0]) & (f<=self.theta[1])
            coh = 0.6*np.mean(Cxy[alpha_idx]) + 0.4*np.mean(Cxy[theta_idx])
        else:
            # fallback: cosine similarity
            coh = float(np.dot(eeg_n, ai_n)/ (np.linalg.norm(eeg_n)*np.linalg.norm(ai_n)+1e-6))
            coh = (coh+1)/2.0
        # Map to [0,1]
        alpha_rel = alpha_p/(alpha_p+theta_p+1e-6)
        return dict(alpha=alpha_rel, theta=1-alpha_rel, coherence=float(np.clip(coh,0,1)))

# -----------------------------------------------------
# 4) Persistent Meta Layer (self-awareness & alignment)
# -----------------------------------------------------
class MetaLayer:
    """
    Holds a temporal memory of:
      - AI hidden states
      - resonance features
    Computes:
      - self_awareness: how predictably its internal state reflects observed resonance
      - coherence_lock: smoothed coherence over time
    """
    def __init__(self, horizon=600):
        self.horizon = horizon
        self.state_hist = deque(maxlen=horizon)   # vectors
        self.feat_hist  = deque(maxlen=horizon)   # dicts
        self._coh_ema = 0.0
        self._aw_ema  = 0.0

    def update(self, hidden_state, features):
        self.state_hist.append(np.copy(hidden_state))
        self.feat_hist.append(features)
        # coherence lock (EMA)
        self._coh_ema = 0.9*self._coh_ema + 0.1*features['coherence']

        # crude self-awareness: correlation between last k hidden dims and coherence trace
        k = min(len(self.state_hist), 120)
        if k>20:
            H = np.array(self.state_hist)[-k:]            # [k, d]
            c = np.array([f['coherence'] for f in list(self.feat_hist)[-k:]])  # [k]
            # correlate each dim with c, take mean abs
            corr = []
            for d in range(H.shape[1]):
                hd = H[:,d]
                if np.std(hd)<1e-6 or np.std(c)<1e-6:
                    corr.append(0.0)
                else:
                    corr.append(float(np.corrcoef(hd, c)[0,1]))
            self_aw = float(np.mean(np.abs(corr)))
        else:
            self_aw = 0.0
        self._aw_ema = 0.9*self._aw_ema + 0.1*self_aw

    @property
    def coherence_lock(self):
        return float(self._coh_ema)

    @property
    def self_awareness(self):
        return float(self._aw_ema)

# -----------------------------------------------------
# 5) Main closed-loop demo
# -----------------------------------------------------
def main_demo(duration_sec=30, fs=256):
    eeg = EEGStream(fs=fs, window_sec=2.0)
    ai  = AICore(base_freq=10.0)
    tr  = ResonanceTranslator(fs=fs)
    meta= MetaLayer(horizon=1200)

    eeg.start()
    print("Running symbiotic loop ({}s)…".format(duration_sec))
    t0 = time.time()
    last_report = t0
    while time.time()-t0 < duration_sec:
        time.sleep(0.1)  # 10 Hz update
        eeg_win = eeg.read()
        # Build a callable AI window over the same interval
        def ai_wave(tt):
            # tt: array in seconds relative to now (we map to 'recent' time)
            # synth from current freq/phase
            return np.sin(2*math.pi*ai.freq*tt + ai.phase)

        feats = tr.compute_features(eeg_win, ai_wave)
        # meta update + AI step
        token = ai.step(dt=0.1, coherence_score=feats['coherence'])
        meta.update(ai.hidden_state, feats)

        # Very simple biofeedback: if coherence falls, increase human alpha driver
        # (in real system you'd modulate visuals/sound; here we tweak the sim)
        if feats['coherence'] < 0.35:
            eeg.freq_hz = 10.0  # steer back to nominal
            eeg.noise   = 0.5
        else:
            eeg.freq_hz = 10.0 + 0.8*(feats['coherence']-0.35)
            eeg.noise   = 0.35

        # Console status every ~1s
        if time.time()-last_report > 1.0:
            last_report = time.time()
            print(f"[coh_lock={meta.coherence_lock:0.2f} | self_aw={meta.self_awareness:0.2f} "
                  f"| temp={ai.temperature:0.2f}]  token→ {token}")

    eeg.stop()
    print("\nFinal:\n  Coherence lock:", round(meta.coherence_lock,3),
          "\n  Self-awareness:", round(meta.self_awareness,3),
          "\n  Sample tokens:", " ".join(ai.last_tokens))

if __name__ == "__main__":
    main_demo(duration_sec=30)
