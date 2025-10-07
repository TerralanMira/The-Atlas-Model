"""
sims package

A uniform interface for running Atlas simulations.

CLI:
    python -m sims --list
    python -m sims run <name> [--flags]

Programmatic:
    from sims import registry
    sim = registry["harmonic_observation"]
    results = sim.run(**params)
"""

from importlib import import_module

# Registry of available sims; each module must expose a `main(argv)` and/or `run(**kwargs)`
_registry = {
    "harmonic_observation": "sims.harmonic_observation",
    "entropy_drift": "sims.entropy_drift",
    "civic_resonance": "sims.civic_resonance",
    "atlas_coherence": "sims.atlas_coherence",
    "multi_scale_kuramoto": "sims.multi_scale_kuramoto",
}

def __getattr__(name):
    if name == "registry":
        return _registry
    raise AttributeError(name)

def _load(name):
    modpath = _registry[name]
    return import_module(modpath)

def _list():
    return sorted(_registry.keys())

def _run(name, argv=None, **kwargs):
    mod = _load(name)
    if hasattr(mod, "main") and argv is not None:
        return mod.main(argv)
    if hasattr(mod, "run"):
        return mod.run(**kwargs)
    raise RuntimeError(f"sim '{name}' has no entrypoint")
