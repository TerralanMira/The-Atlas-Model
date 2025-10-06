#!/usr/bin/env python3
"""
Run Atlas simulations via a single, uniform CLI.

Usage:
  python -m sims --list
  python -m sims run community_kuramoto --n 256 --K 1.2 --rho 0.6
"""
from __future__ import annotations
import argparse, importlib, pkgutil, sys

SIM_PACKAGE = "sims"

def discover() -> dict[str, str]:
    mods = {}
    for m in pkgutil.iter_modules([SIM_PACKAGE]):
        # treat any .py with a `main(args)` as runnable
        mods[m.name] = f"{SIM_PACKAGE}.{m.name}"
    return mods

def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("--list", help="List available simulations")
    run = sub.add_parser("run", help="Run a simulation")
    run.add_argument("name", help="module inside sims/ having main(args)")
    run.add_argument("args", nargs=argparse.REMAINDER, help="args passed to sim")

    ns = parser.parse_args()
    mods = discover()

    if ns.cmd == "--list":
        for k in sorted(mods):
            print(k)
        return 0

    if ns.cmd == "run":
        if ns.name not in mods:
            print(f"[!] sim '{ns.name}' not found. Available: {', '.join(sorted(mods))}")
            return 2
        mod = importlib.import_module(mods[ns.name])
        if not hasattr(mod, "main"):
            print(f"[!] {mods[ns.name]} has no main(args)")
            return 3
        # Re-parse args within the sim's main
        return int(mod.main(ns.args) or 0)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
 To make each sim runnable, ensure each module (e.g., community_kuramoto.py) exposes a main(args: list[str]) that parses its own arguments and runs.
 
