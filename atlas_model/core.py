"""
Core interfaces for the Atlas Model.
Keep this file tiny and dependency-free.
"""

from typing import Dict, List, Protocol

class ResonanceObject(Protocol):
    def coherence(self) -> float: ...
    def metadata(self) -> Dict: ...

class Coupler(Protocol):
    def forward(self, inputs: List[float], **params) -> float: ...
    def explain(self) -> str: ...

class Conductor(Protocol):
    target: float
    def step(self, C: float, **state) -> Dict: ...
