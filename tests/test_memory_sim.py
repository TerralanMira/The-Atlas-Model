import json
from pathlib import Path

def test_memory_sim_doc_snippet_executes(tmp_path):
    code = r'''
from collections import defaultdict

class MemorySimulation:
    def __init__(self):
        self.memory_echoes = defaultdict(lambda: {"strength": 0, "pattern": None})

    def shared(self, event): return event.get("shared", False)
    def revisited(self, event): return event.get("revisited", False)
    def evolve_pattern(self, pattern): return f"{pattern}_evolved" if pattern else "seed"

    def process_event(self, event):
        event_id = event["event"]
        if self.shared(event):
            self.memory_echoes[event_id]["strength"] += 1
        else:
            self.memory_echoes[event_id]["strength"] -= 0.5
        if self.revisited(event):
            p = self.memory_echoes[event_id]["pattern"]
            self.memory_echoes[event_id]["pattern"] = self.evolve_pattern(p)

    def report(self): return dict(self.memory_echoes)

events = [
    {"event": "community_gathering", "shared": True},
    {"event": "shared_meal", "shared": True},
    {"event": "conflict", "shared": False},
    {"event": "resolution", "shared": True, "revisited": True}
]
sim = MemorySimulation()
for e in events: sim.process_event(e)
out = sim.report()
print(out)
    '''
    script = tmp_path / "snippet.py"
    script.write_text(code, encoding="utf-8")
    # execute snippet
    import subprocess, sys
    res = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    assert res.returncode == 0
    assert "community_gathering" in res.stdout
    assert "resolution" in res.stdout
