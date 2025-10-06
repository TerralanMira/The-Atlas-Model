```python
import subprocess, sys

def _ok(cmd: list[str]):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert r.returncode == 0, r.stderr[:4000]

def test_list():
    _ok([sys.executable, "-m", "sims", "--list"])

def test_run_community_kuramoto_help():
    # relies on sim exposing a --help without full execution
    r = subprocess.run([sys.executable, "-m", "sims", "run", "community_kuramoto", "--help"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert r.returncode in (0,2), r.stderr[:2000]
  Adjust the second test once each sim’s main(args) supports --help.
