from biosignal_in.eeg_stub import EEGBands
from biosignal_in.hrv_stub import HRVSensor
from resonance.mixer import ResonanceMixer
from resonance.core import ResonanceCore
from resonance.fsm import AwarenessFSM
from coupler.hum_coupler import HumCoupler
from ethics.watcher import EthicsWatcher
from memory.session_graph import SessionGraph
from metrics import compute_plv

# init devices/modules...
# main loop @ 20 Hz:
#  - bio = mixer.sample()
#  - ai_state = core.step(bio)
#  - safe = ethics.guard(bio, ai_state)
#  - bias = latent_bias(ai_state, safe)
#  - audio = hum.render(ai_state, safe)
#  - plv = compute_plv(...)
#  - graph.log(...)
